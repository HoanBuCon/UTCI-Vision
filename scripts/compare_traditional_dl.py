"""E8 — Phân loại biển: đặc trưng truyền thống + SVM so với học sâu (YOLO11), theo kích thước biển. Phụ trách: TV1, TV2.

    python scripts/compare_traditional_dl.py <yolo11.pt> [--imgsz 960] [--out reports/e8]

Cùng một tập biển thật (GT) của processed/<version>; các phương pháp truyền thống fit trên crop train, chọn C trên val,
đánh giá trên test:
  1. HOG + SVM          — HOG trên crop xám 32×32 (configs/verifier.yaml > features.hog)
  2. HOG + màu + SVM    — thêm histogram HSV (H 16 bin × S 4 bin) của crop
  3. SIFT-BoVW + SVM    — SIFT trên crop phóng về 64×64, từ điển k-means 256 từ, histogram Hellinger
  4. YOLO11 (học sâu)   — với mỗi biển test: lớp của dự đoán điểm cao nhất có IoU ≥ 0.5 (conf ≥ 0.001); không có -> bỏ sót

Lưu ý công bằng: phương pháp truyền thống được cho sẵn vị trí biển (crop GT) nên chỉ làm phân loại; YOLO phải tự tìm biển.
Báo cáo cả "accuracy trên biển YOLO tìm thấy" (so sánh phân loại thuần) và "accuracy tổng" (bỏ sót tính là sai).
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from utci_vision.config import load_config, resolve
from utci_vision.data.crops import padded_crop
from utci_vision.data.labels import list_images, read_labels
from utci_vision.evaluation.metrics import iou_matrix, wilson_interval

SIZE_BINS, SIZE_LABELS = [0, 16, 32, 64, np.inf], ["<16px", "16-32", "32-64", ">=64"]


def collect_crops(split: str, pad: float) -> tuple[list[np.ndarray], pd.DataFrame]:
    root = resolve(load_config("data")["processed_dir"]) / split
    crops, rows = [], []
    for path in list_images(root):
        img = cv2.imread(str(path))
        h, w = img.shape[:2]
        for k, b in enumerate(read_labels(path.parent.parent / "labels" / f"{path.stem}.txt")):
            box = b.to_xyxy(w, h)
            crop = padded_crop(img, box, pad)
            if crop.size == 0:
                continue
            crops.append(crop)
            rows.append(
                {
                    "image": path.name,
                    "k": k,
                    "cls": b.class_id,
                    "box": box,
                    "side": float(np.sqrt((box[2] - box[0]) * (box[3] - box[1]))),
                }
            )
    return crops, pd.DataFrame(rows)


def hog_features(crops: list[np.ndarray], cfg: dict) -> np.ndarray:
    from skimage.feature import hog

    h = cfg["features"]["hog"]
    out = []
    for c in crops:
        g = cv2.resize(cv2.cvtColor(c, cv2.COLOR_BGR2GRAY), (h["size"], h["size"]), interpolation=cv2.INTER_AREA)
        out.append(
            hog(
                g,
                orientations=h["orientations"],
                pixels_per_cell=tuple(h["pixels_per_cell"]),
                cells_per_block=tuple(h["cells_per_block"]),
            )
        )
    return np.array(out, np.float32)


def hsv_hist(crops: list[np.ndarray]) -> np.ndarray:
    out = []
    for c in crops:
        hsv = cv2.cvtColor(cv2.resize(c, (32, 32), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [16, 4], [0, 180, 0, 256]).ravel()
        out.append(hist / (hist.sum() + 1e-9))
    return np.array(out, np.float32)


def sift_descriptors(crops: list[np.ndarray]) -> list[np.ndarray]:
    sift = cv2.SIFT_create()
    out = []
    for c in crops:
        g = cv2.resize(cv2.cvtColor(c, cv2.COLOR_BGR2GRAY), (64, 64), interpolation=cv2.INTER_CUBIC)
        _, d = sift.detectAndCompute(g, None)
        out.append(d if d is not None else np.zeros((0, 128), np.float32))
    return out


def bovw(desc: list[np.ndarray], kmeans) -> np.ndarray:
    k = kmeans.n_clusters
    out = np.zeros((len(desc), k), np.float32)
    for i, d in enumerate(desc):
        if len(d):
            out[i] = np.bincount(kmeans.predict(d), minlength=k)
    out /= out.sum(1, keepdims=True) + 1e-9
    return np.sqrt(out)  # Hellinger


def fit_svm(x_tr, y_tr, x_val, y_val):
    """SVM RBF, chuẩn hoá chuẩn; chọn C trên val."""
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC

    best = None
    for c in (1.0, 10.0):
        m = make_pipeline(StandardScaler(), SVC(C=c, kernel="rbf", gamma="scale")).fit(x_tr, y_tr)
        acc = (m.predict(x_val) == y_val).mean()
        print(f"    C={c:g}: accuracy val {acc:.3f}")
        if best is None or acc > best[0]:
            best = (acc, m)
    return best[1]


def yolo_predictions(weights: Path, test: pd.DataFrame, imgsz: int) -> tuple[np.ndarray, float]:
    """Lớp YOLO cho từng biển test (-1 = bỏ sót) + ms/ảnh."""
    from ultralytics import YOLO

    model = YOLO(str(weights))
    root = resolve(load_config("data")["processed_dir"]) / "test" / "images"
    pred = np.full(len(test), -1)
    groups = test.groupby("image").indices
    t0 = time.perf_counter()
    for name, idx in groups.items():
        r = model.predict(str(root / name), imgsz=imgsz, conf=0.001, iou=0.7, max_det=300, verbose=False)[0]
        pb, pc, ps = r.boxes.xyxy.cpu().numpy(), r.boxes.cls.cpu().numpy().astype(int), r.boxes.conf.cpu().numpy()
        if not len(pb):
            continue
        gt = np.array([test.box.iloc[i] for i in idx])
        iou = iou_matrix(gt, pb)
        for row, i in enumerate(idx):
            cand = np.flatnonzero(iou[row] >= 0.5)
            if len(cand):
                pred[i] = pc[cand[np.argmax(ps[cand])]]
    return pred, (time.perf_counter() - t0) * 1000 / len(groups)


def summarize(test: pd.DataFrame, methods: dict[str, np.ndarray], yolo: str) -> pd.DataFrame:
    """Accuracy trên mọi biển + trên đúng tập biển YOLO tìm thấy (so sánh phân loại thuần, cùng mẫu cho mọi phương pháp)."""
    from sklearn.metrics import f1_score

    rows = []
    test = test.assign(size=pd.cut(test.side, SIZE_BINS, labels=SIZE_LABELS, right=False), found=methods[yolo] >= 0)
    labels = sorted(test.cls.unique())
    for name, pred in methods.items():
        t = test.assign(pred=pred)
        for size, g in [("tất cả", t), *t.groupby("size", observed=True)]:
            k, n = int((g.pred == g.cls).sum()), len(g)
            lo, hi = wilson_interval(k, n)
            f = g[g.found]
            rows.append(
                {
                    "phuong_phap": name,
                    "kich_thuoc": size,
                    "n": n,
                    "accuracy": k / n,
                    "ci95": f"{lo:.3f}-{hi:.3f}",
                    "macro_F1": f1_score(g.cls, g.pred, average="macro", labels=labels, zero_division=0),
                    "n_yolo_tim_thay": len(f),
                    "accuracy_tren_bien_yolo_tim_thay": (f.pred == f.cls).mean() if len(f) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def paired_delta(test: pd.DataFrame, a: np.ndarray, b: np.ndarray, n_boot: int = 2000) -> pd.DataFrame:
    """Δaccuracy (a − b) ghép cặp trên các biển YOLO tìm thấy, theo kích thước; CI 95% bootstrap theo biển."""
    rng = np.random.default_rng(0)
    size = pd.cut(test.side, SIZE_BINS, labels=SIZE_LABELS, right=False)
    found = b >= 0
    rows = []
    for name, mask in [("tất cả", found), *[(s, found & (size == s).to_numpy()) for s in SIZE_LABELS]]:
        diff = ((a == test.cls.to_numpy()).astype(int) - (b == test.cls.to_numpy()).astype(int))[mask]
        boots = [diff[rng.integers(0, len(diff), len(diff))].mean() for _ in range(n_boot)]
        lo, hi = np.percentile(boots, [2.5, 97.5])
        rows.append(
            {"kich_thuoc": name, "n": int(mask.sum()), "delta_acc": diff.mean(), "ci95_low": lo, "ci95_high": hi}
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("weights", type=Path)
    parser.add_argument("--imgsz", type=int, default=960)
    parser.add_argument("--out", type=Path, default=Path("reports/e8"))
    args = parser.parse_args()
    from sklearn.cluster import MiniBatchKMeans

    cfg = load_config("verifier")
    out = resolve(args.out)
    out.mkdir(parents=True, exist_ok=True)
    pad = cfg["build"]["crop_pad_ratio"]
    data = {s: collect_crops(s, pad) for s in ("train", "val", "test")}
    for s, (c, _) in data.items():
        print(f"{s}: {len(c)} crop")
    y = {s: data[s][1].cls.to_numpy() for s in data}
    methods, timing = {}, {}

    print("HOG + SVM")
    hog = {s: hog_features(data[s][0], cfg) for s in data}
    m = fit_svm(hog["train"], y["train"], hog["val"], y["val"])
    t0 = time.perf_counter()
    methods["HOG + SVM"] = m.predict(hog_features(data["test"][0], cfg))
    timing["HOG + SVM"] = (time.perf_counter() - t0) * 1000 / len(y["test"])

    print("HOG + màu HSV + SVM")
    hc = {s: np.hstack([hog[s], hsv_hist(data[s][0])]) for s in data}
    m = fit_svm(hc["train"], y["train"], hc["val"], y["val"])
    t0 = time.perf_counter()
    methods["HOG + màu + SVM"] = m.predict(np.hstack([hog_features(data["test"][0], cfg), hsv_hist(data["test"][0])]))
    timing["HOG + màu + SVM"] = (time.perf_counter() - t0) * 1000 / len(y["test"])

    print("SIFT-BoVW + SVM")
    desc = {s: sift_descriptors(data[s][0]) for s in data}
    pool = np.vstack([d for d in desc["train"] if len(d)])
    sample = pool[np.random.default_rng(0).choice(len(pool), min(200_000, len(pool)), replace=False)]
    kmeans = MiniBatchKMeans(256, random_state=0, batch_size=4096, n_init=3).fit(sample)
    bw = {s: bovw(desc[s], kmeans) for s in data}
    no_kp = {s: float(np.mean([len(d) == 0 for d in desc[s]])) for s in data}
    print(f"    crop không có điểm SIFT (sau khi phóng 64×64): {no_kp}")
    m = fit_svm(bw["train"], y["train"], bw["val"], y["val"])
    t0 = time.perf_counter()
    methods["SIFT-BoVW + SVM"] = m.predict(bovw(sift_descriptors(data["test"][0]), kmeans))
    timing["SIFT-BoVW + SVM"] = (time.perf_counter() - t0) * 1000 / len(y["test"])

    print("YOLO11")
    methods["YOLO11 (học sâu)"], ms_img = yolo_predictions(args.weights, data["test"][1], args.imgsz)

    test = data["test"][1]
    table = summarize(test, methods, yolo="YOLO11 (học sâu)")
    pd.set_option("display.width", 220)
    print(table.round(3).to_string(index=False))
    delta = paired_delta(test, methods["HOG + màu + SVM"], methods["YOLO11 (học sâu)"])
    print(
        "Δaccuracy (HOG + màu + SVM − YOLO11) ghép cặp trên biển YOLO tìm thấy:\n"
        + delta.round(3).to_string(index=False)
    )
    delta.to_csv(out / "e8_paired_delta.csv", index=False)
    test.drop(columns="box").assign(**{k: v for k, v in methods.items()}).to_csv(
        out / "e8_predictions.csv", index=False
    )
    print(
        "Thời gian:", {k: f"{v:.2f} ms/crop" for k, v in timing.items()}, f"| YOLO {ms_img:.1f} ms/ảnh (gồm tìm biển)"
    )
    table.to_csv(out / "e8_by_size.csv", index=False)
    print(f"-> {out}")


if __name__ == "__main__":
    main()
