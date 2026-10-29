"""Phân tích một lần fine-tune YOLO11 trên processed/<version> — số liệu cho báo cáo (FR-EVAL). Phụ trách: TV1, TV3.

    python scripts/analyze_run.py <weights.pt> [--imgsz 960] [--boot 500] [--out reports/eval/<tên>]

Kết quả (in ra màn hình + CSV trong --out):
1. ultralytics_val.csv  — P/R/AP50/AP50-95 theo lớp trên val và test (Ultralytics `val`).
2. Bootstrap theo ảnh  — mAP50, mAP50-95, P/R ở conf 0.25 trên test kèm CI 95% (khớp cách ghép của Ultralytics).
3. boxes_<split>.csv    — từng biển thật ở conf 0.25: đúng lớp / sai lớp / bỏ sót + kích thước -> theo cỡ, theo lớp.
4. similarity.csv       — ảnh test chia nhóm theo khoảng cách pHash tới ảnh train gần nhất (đo mức lạc quan của test).

Ma trận nhầm lẫn của Ultralytics 8.4 ghép cả dự đoán conf 0.001 nên không dùng; mục 3 thay thế bằng ghép ở conf 0.25.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from utci_vision.config import load_classes, load_config, resolve
from utci_vision.data.dedup import compute_hashes
from utci_vision.data.labels import list_images, read_labels
from utci_vision.training import write_data_yaml

IOU_THRESHOLDS = np.linspace(0.5, 0.95, 10)
SIZE_BINS, SIZE_LABELS = [0, 16, 32, 64, np.inf], ["<16px", "16-32", "32-64", ">=64"]


def box_iou(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """IoU (len(a), len(b)) cho hộp xyxy."""
    x1 = np.maximum(a[:, None, 0], b[None, :, 0])
    y1 = np.maximum(a[:, None, 1], b[None, :, 1])
    x2 = np.minimum(a[:, None, 2], b[None, :, 2])
    y2 = np.minimum(a[:, None, 3], b[None, :, 3])
    inter = np.clip(x2 - x1, 0, None) * np.clip(y2 - y1, 0, None)

    def area(z):
        return (z[:, 2] - z[:, 0]) * (z[:, 3] - z[:, 1])

    return inter / (area(a)[:, None] + area(b)[None, :] - inter + 1e-9)


def match_like_ultralytics(pred_cls: np.ndarray, true_cls: np.ndarray, iou: np.ndarray) -> np.ndarray:
    """(P, 10) dự đoán đúng ở từng ngưỡng IoU — như DetectionValidator.match_predictions; iou: (T, P)."""
    correct = np.zeros((len(pred_cls), len(IOU_THRESHOLDS)), bool)
    iou = iou * (true_cls[:, None] == pred_cls[None, :])
    for i, t in enumerate(IOU_THRESHOLDS):
        m = np.array(np.nonzero(iou >= t)).T
        if len(m) > 1:
            m = m[iou[m[:, 0], m[:, 1]].argsort()[::-1]]
            m = m[np.unique(m[:, 1], return_index=True)[1]]
            m = m[np.unique(m[:, 0], return_index=True)[1]]
        if len(m):
            correct[m[:, 1], i] = True
    return correct


def ground_truth(image: Path, w: int, h: int) -> tuple[np.ndarray, np.ndarray]:
    boxes = read_labels(image.parent.parent / "labels" / f"{image.stem}.txt")
    return np.array([b.to_xyxy(w, h) for b in boxes]).reshape(-1, 4), np.array([b.class_id for b in boxes], int)


def predict(model, images: list[Path], imgsz: int, conf: float, iou: float, batch: int = 16):
    for i in range(0, len(images), batch):
        chunk = images[i : i + batch]
        results = model.predict([str(p) for p in chunk], imgsz=imgsz, conf=conf, iou=iou, max_det=300, verbose=False)
        yield from zip(chunk, results)


def ultralytics_val(model, data_yaml: Path, imgsz: int) -> pd.DataFrame:
    rows: dict[int, dict] = {}
    for split in ("val", "test"):
        box = model.val(
            data=str(data_yaml), imgsz=imgsz, split=split, batch=8, workers=0, plots=False, verbose=False
        ).box
        print(f"[Ultralytics {split}] P {box.mp:.3f} R {box.mr:.3f} mAP50 {box.map50:.3f} mAP50-95 {box.map:.3f}")
        for i, c in enumerate(box.ap_class_index):
            rows.setdefault(int(c), {}).update(
                {f"{split}_P": box.p[i], f"{split}_R": box.r[i], f"{split}_AP50": box.ap50[i], f"{split}_AP": box.ap[i]}
            )
    return pd.DataFrame.from_dict(rows, orient="index").sort_index()


def bootstrap_test(model, images: list[Path], imgsz: int, n_boot: int, seed: int = 0) -> pd.DataFrame:
    """Dự đoán conf 0.001 một lần, rồi lấy mẫu lại theo ảnh để có CI 95%."""
    from ultralytics.utils.metrics import ap_per_class

    per_image = []
    for path, r in predict(model, images, imgsz, conf=0.001, iou=0.7):
        gt, gc = ground_truth(path, r.orig_shape[1], r.orig_shape[0])
        pb, pc = r.boxes.xyxy.cpu().numpy(), r.boxes.cls.cpu().numpy().astype(int)
        tp = match_like_ultralytics(pc, gc, box_iou(gt, pb)) if len(gt) and len(pb) else np.zeros((len(pc), 10), bool)
        per_image.append((tp, r.boxes.conf.cpu().numpy(), pc, gc))

    def metrics(idx) -> tuple[float, float, float, float]:
        tp, conf, pc, tc = (np.concatenate([per_image[i][k] for i in idx]) for k in range(4))
        ap = ap_per_class(tp, conf, pc, tc)[5]
        keep = conf >= 0.25
        hit = tp[keep, 0].sum()
        return ap[:, 0].mean(), ap.mean(), hit / max(keep.sum(), 1), hit / len(tc)

    names = ["mAP50", "mAP50-95", "P@0.25", "R@0.25"]
    point = metrics(range(len(per_image)))
    rng = np.random.default_rng(seed)
    boots = np.array([metrics(rng.integers(0, len(per_image), len(per_image))) for _ in range(n_boot)])
    lo, hi = np.percentile(boots, [2.5, 97.5], axis=0)
    return pd.DataFrame({"metric": names, "value": point, "ci95_low": lo, "ci95_high": hi})


def boxes_at_conf(model, images: list[Path], imgsz: int, conf: float) -> tuple[pd.DataFrame, Counter]:
    """Mỗi biển thật: lớp dự đoán khớp IoU >= 0.5 (bất kể lớp; -1 = bỏ sót) ở `conf`; kèm số dự đoán thừa theo lớp."""
    rows, false_pos = [], Counter()
    for path, r in predict(model, images, imgsz, conf=conf, iou=0.5):
        gt, gc = ground_truth(path, r.orig_shape[1], r.orig_shape[0])
        pb, pc = r.boxes.xyxy.cpu().numpy(), r.boxes.cls.cpu().numpy().astype(int)
        matched: dict[int, int] = {}
        used_pred: set[int] = set()
        if len(gt) and len(pb):
            iou = box_iou(pb, gt)
            for k in np.argsort(-r.boxes.conf.cpu().numpy()):
                free = [j for j in range(len(gt)) if j not in matched]
                if free:
                    j = max(free, key=lambda j: iou[k, j])
                    if iou[k, j] >= 0.5:
                        matched[j] = int(pc[k])
                        used_pred.add(int(k))
        false_pos.update(int(pc[k]) for k in range(len(pb)) if k not in used_pred)
        sides = np.sqrt((gt[:, 2] - gt[:, 0]) * (gt[:, 3] - gt[:, 1])) if len(gt) else []
        for j, (c, side) in enumerate(zip(gc, sides)):
            rows.append({"image": path.name, "cls": int(c), "side": float(side), "pred": matched.get(j, -1)})
    df = pd.DataFrame(rows)
    df["outcome"] = np.where(df.pred == df.cls, "dung", np.where(df.pred == -1, "sot", "sai_lop"))
    df["size"] = pd.cut(df.side, SIZE_BINS, labels=SIZE_LABELS, right=False)
    return df, false_pos


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p, d = k / n, 1 + z * z / n
    c, h = p + z * z / (2 * n), z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / d, (c + h) / d


def per_class_review(boxes: pd.DataFrame, false_pos: Counter) -> pd.DataFrame:
    rows = []
    for c in load_classes():
        g = boxes[boxes.cls == c.id]
        k, n = int((g.outcome == "dung").sum()), len(g)
        wrong_in = int(((boxes.pred == c.id) & (boxes.cls != c.id)).sum())
        lo, hi = wilson(k, n) if n else (np.nan, np.nan)
        big = g[g.side >= 16]
        rows.append(
            {
                "id": c.id,
                "ten": c.name_vi,
                "n": n,
                "recall": k / n if n else np.nan,
                "recall_ci95": f"{lo:.2f}-{hi:.2f}",
                "precision": k / max(k + wrong_in + false_pos[c.id], 1),
                "recall_ge16px": (big.outcome == "dung").mean() if len(big) else np.nan,
                "ti_le_bien_nho": (g.side < 16).mean() if n else np.nan,
            }
        )
    return pd.DataFrame(rows)


def similarity_groups(boxes_test: pd.DataFrame, false_pos_by_image: pd.Series, root: Path) -> pd.DataFrame:
    """Nhóm ảnh test theo Hamming pHash tới ảnh train gần nhất (cùng cấu hình dedup của data.yaml)."""
    d = load_config("data")["dedup"]
    test_imgs, train_imgs = list_images(root / "test"), list_images(root / "train")
    te = compute_hashes(test_imgs, d["hash"], d["hash_size"]).astype(np.uint8)
    tr = compute_hashes(train_imgs, d["hash"], d["hash_size"]).astype(np.uint8)
    nearest = pd.Series([int((tr != row).sum(1).min()) for row in te], index=[p.name for p in test_imgs])
    print(
        f"Hamming test->train gần nhất: trung vị {nearest.median():.0f}; <= max_hamming: {(nearest <= d['max_hamming']).mean():.1%}"
    )
    group = pd.cut(nearest, [-1, 10, 14, 64], labels=["giong_train(<=10)", "trung_binh(11-14)", "khac_train(>=15)"])
    b = boxes_test.assign(group=boxes_test.image.map(group), ok=boxes_test.outcome == "dung", big=boxes_test.side >= 16)
    out = b.groupby("group", observed=True).agg(
        anh=("image", "nunique"),
        bien=("ok", "size"),
        dung=("ok", "sum"),
        ti_le_bien_nho=("big", lambda s: 1 - s.mean()),
    )
    out["recall"] = out.dung / out.bien
    out["recall_ge16px"] = b[b.big].groupby("group", observed=True).ok.mean()
    fp = false_pos_by_image.groupby(group).sum()
    out["precision"] = out.dung / (out.dung + fp.reindex(out.index).fillna(0))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("weights", type=Path)
    parser.add_argument("--imgsz", type=int, default=960)
    parser.add_argument("--boot", type=int, default=500, help="số lần bootstrap (0 = bỏ qua)")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    from ultralytics import YOLO

    root = resolve(load_config("data")["processed_dir"])
    out = resolve(args.out or Path("reports/eval") / args.weights.parent.name)
    out.mkdir(parents=True, exist_ok=True)
    model = YOLO(str(args.weights))
    pd.set_option("display.width", 200)

    ultralytics_val(model, write_data_yaml(root), args.imgsz).to_csv(out / "ultralytics_val.csv")

    if args.boot:
        ci = bootstrap_test(model, list_images(root / "test"), args.imgsz, args.boot)
        print(ci.round(3).to_string(index=False))
        ci.to_csv(out / "bootstrap_test.csv", index=False)

    boxes, false_pos = {}, Counter()
    for split in ("val", "test"):
        boxes[split], fp = boxes_at_conf(model, list_images(root / split), args.imgsz, conf=0.25)
        false_pos += fp
        boxes[split].to_csv(out / f"boxes_{split}.csv", index=False)
    both = pd.concat(boxes.values())
    by_size = pd.crosstab(both["size"], both.outcome, normalize="index").assign(n=both["size"].value_counts())
    print("Theo kích thước (val+test, conf 0.25):\n" + by_size.round(3).to_string())
    review = per_class_review(both, false_pos)
    print(review.sort_values("recall").round(3).head(8).to_string(index=False))
    review.to_csv(out / "class_review.csv", index=False)

    fp_test = Counter()
    for path, r in predict(model, list_images(root / "test"), args.imgsz, conf=0.25, iou=0.5):
        fp_test[path.name] = len(r.boxes)
    pred_per_image = pd.Series(fp_test)
    hits = boxes["test"].assign(ok=boxes["test"].outcome == "dung").groupby("image").ok.sum()
    false_pos_by_image = (pred_per_image - hits.reindex(pred_per_image.index).fillna(0)).clip(lower=0)
    sim = similarity_groups(boxes["test"], false_pos_by_image, root)
    print(sim.round(3).to_string())
    sim.to_csv(out / "similarity.csv")
    print(f"-> {out}")


if __name__ == "__main__":  # bắt buộc trên Windows: DataLoader workers chạy lại module này
    main()
