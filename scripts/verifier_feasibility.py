"""Thử nghiệm khả thi bộ xác minh đặc trưng thủ công (T0 + T1) với trọng số YOLO hiện có. Phụ trách: TV1, TV2.

    python scripts/verifier_feasibility.py [<yolo11.pt>] [--imgsz 960] [--boot 1000] [--out reports/feasibility]

T0 — Dư địa: YOLO chạy conf 0.10 trên val/test; mỗi dự đoán được gán đúng (TP) / sai lớp / định vị kém / trùng / nền.
     In thành phần dự đoán sai ở conf 0.25 và 0.10, trần của bộ xác minh chỉ loại bỏ (recall tối đa = recall @0.10),
     và AUC của riêng điểm YOLO (mức bộ xác minh phải vượt).
T1 — Khả thi: đặc trưng thủ công (verifier.region_features: màu HSV, hình học contour, Hu, HOG→PCA, độ nét) +
     ngữ cảnh YOLO -> LightGBM. Fit trên ứng viên của val (YOLO chưa thấy val khi train), đánh giá trên test.
     Ablation tập đặc trưng; so với YOLO thuần @0.25 ở (a) cùng recall, (b) ngưỡng chọn trên val (out-of-fold);
     CI 95% bootstrap theo ảnh; tách theo độ giống ảnh train (pHash).

Dự đoán "trùng" (cùng biển đã có dự đoán điểm cao hơn khớp) tính là sai — bảo thủ cho bộ xác minh.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from utci_vision.config import load_classes, load_config, resolve
from utci_vision.data.dedup import compute_hashes
from utci_vision.data.labels import list_images, read_labels
from utci_vision.verifier import FEATURE_GROUPS, FEATURE_NAMES, region_features

SUPERCLASSES = ["prohibitory", "warning", "mandatory", "info", "other"]
CONTEXT = ["yolo_score", "yolo_cls", "superclass", "log_w", "log_h", "aspect", "rel_cx", "rel_cy"]
FEATURE_SETS: dict[str, list[str]] = {
    "ngu_canh_yolo": CONTEXT,
    "+mau": CONTEXT + FEATURE_GROUPS["color"],
    "+mau+hinh_hoc+hu": CONTEXT + FEATURE_GROUPS["color"] + FEATURE_GROUPS["shape"] + FEATURE_GROUPS["hu"],
    "+mau+hinh_hoc+hu+hog": CONTEXT
    + FEATURE_GROUPS["color"]
    + FEATURE_GROUPS["shape"]
    + FEATURE_GROUPS["hu"]
    + ["HOG"],
    "day_du": CONTEXT + FEATURE_NAMES + ["HOG"],
    "chi_dac_trung_thu_cong": FEATURE_NAMES + ["HOG", "yolo_cls", "superclass"],
}


def box_iou(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    x1 = np.maximum(a[:, None, 0], b[None, :, 0])
    y1 = np.maximum(a[:, None, 1], b[None, :, 1])
    x2 = np.minimum(a[:, None, 2], b[None, :, 2])
    y2 = np.minimum(a[:, None, 3], b[None, :, 3])
    inter = np.clip(x2 - x1, 0, None) * np.clip(y2 - y1, 0, None)
    area_a = (a[:, 2] - a[:, 0]) * (a[:, 3] - a[:, 1])
    area_b = (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1])
    return inter / (area_a[:, None] + area_b[None, :] - inter + 1e-9)


def label_candidates(pb: np.ndarray, pc: np.ndarray, ps: np.ndarray, gt: np.ndarray, gc: np.ndarray) -> list[str]:
    """Ghép tham lam theo điểm giảm dần: tp | sai_lop | trung | dinh_vi_kem | nen."""
    out = ["nen"] * len(pb)
    if not len(gt):
        return out
    iou = box_iou(pb, gt)
    used: set[int] = set()
    for k in np.argsort(-ps):
        same = [j for j in range(len(gt)) if gc[j] == pc[k] and iou[k, j] >= 0.5]
        free = [j for j in same if j not in used]
        if free:
            used.add(max(free, key=lambda j: iou[k, j]))
            out[k] = "tp"
        elif same:
            out[k] = "trung"
        elif iou[k].max() >= 0.5:
            out[k] = "sai_lop"
        elif iou[k].max() >= 0.1:
            out[k] = "dinh_vi_kem"
    return out


def build_candidates(model, split: str, imgsz: int, cfg: dict) -> tuple[pd.DataFrame, np.ndarray, int]:
    """-> (một dòng / dự đoán YOLO conf >= proposal_conf, ma trận HOG thô, số biển GT)."""
    classes = load_classes()
    images = list_images(resolve(load_config("data")["processed_dir"]) / split)
    rows, hogs, n_gt = [], [], 0
    for i in range(0, len(images), 16):
        chunk = images[i : i + 16]
        results = model.predict(
            [str(p) for p in chunk],
            imgsz=imgsz,
            conf=cfg["build"]["proposal_conf"],
            iou=0.5,
            max_det=300,
            verbose=False,
        )
        for path, r in zip(chunk, results):
            img = cv2.imread(str(path))
            h, w = img.shape[:2]
            labels = read_labels(path.parent.parent / "labels" / f"{path.stem}.txt")
            gt = np.array([b.to_xyxy(w, h) for b in labels]).reshape(-1, 4)
            gc = np.array([b.class_id for b in labels], int)
            n_gt += len(gt)
            pb, pc, ps = r.boxes.xyxy.cpu().numpy(), r.boxes.cls.cpu().numpy().astype(int), r.boxes.conf.cpu().numpy()
            outcome = label_candidates(pb, pc, ps, gt, gc)
            for k in range(len(pb)):
                feats, hog_raw = region_features(img, tuple(pb[k]), cfg)
                x1, y1, x2, y2 = pb[k]
                rows.append(
                    {
                        "image": path.name,
                        "outcome": outcome[k],
                        "y": int(outcome[k] == "tp"),
                        "yolo_score": float(ps[k]),
                        "yolo_cls": int(pc[k]),
                        "superclass": SUPERCLASSES.index(classes[pc[k]].superclass),
                        "side": float(np.sqrt((x2 - x1) * (y2 - y1))),
                        "log_w": float(np.log1p(x2 - x1)),
                        "log_h": float(np.log1p(y2 - y1)),
                        "aspect": float((x2 - x1) / (y2 - y1 + 1e-9)),
                        "rel_cx": float((x1 + x2) / 2 / w),
                        "rel_cy": float((y1 + y2) / 2 / h),
                        **dict(zip(FEATURE_NAMES, feats.tolist())),
                    }
                )
                hogs.append(hog_raw)
    return pd.DataFrame(rows), np.array(hogs), n_gt


def pr_at(df: pd.DataFrame, score: str, thr: float, n_gt: int) -> tuple[float, float]:
    kept = df[df[score] >= thr]
    tp = int(kept.y.sum())
    return tp / max(len(kept), 1), tp / n_gt


def threshold_for_recall(df: pd.DataFrame, score: str, recall: float, n_gt: int) -> float:
    """Ngưỡng cao nhất vẫn đạt `recall`."""
    s = df.sort_values(score, ascending=False)
    hit = np.flatnonzero(s.y.cumsum().to_numpy() >= recall * n_gt)
    return float(s[score].iloc[hit[0]]) if len(hit) else float(s[score].min())


def report_t0(cands: dict[str, pd.DataFrame], n_gt: dict[str, int]) -> None:
    from sklearn.metrics import roc_auc_score

    print("\n=== T0 — Dư địa của bộ xác minh ===")
    for split, df in cands.items():
        print(f"[{split}] {n_gt[split]} biển thật | {len(df)} dự đoán conf ≥ 0.10")
        for thr in (0.25, 0.10):
            d = df[df.yolo_score >= thr]
            p, r = pr_at(df, "yolo_score", thr, n_gt[split])
            wrong = d[d.y == 0].outcome.value_counts()
            mix = " · ".join(f"{k} {v} ({v / max(len(d) - d.y.sum(), 1):.0%})" for k, v in wrong.items())
            print(f"  conf ≥ {thr:.2f}: P {p:.3f} R {r:.3f} | sai {len(d) - d.y.sum()}: {mix}")
        p25, r25 = pr_at(df, "yolo_score", 0.25, n_gt[split])
        _, r10 = pr_at(df, "yolo_score", 0.10, n_gt[split])
        print(
            f"  Trần bộ xác minh (chỉ loại bỏ) trên ứng viên ≥ 0.10: P 1.000 · R tối đa {r10:.3f} (YOLO @0.25: R {r25:.3f})"
        )
        print(f"  AUC của riêng điểm YOLO (đúng vs sai): {roc_auc_score(df.y, df.yolo_score):.3f}")


def matrix(df: pd.DataFrame, hogs: np.ndarray, cols: list[str], pca) -> np.ndarray:
    base = df[[c for c in cols if c != "HOG"]].to_numpy(np.float32)
    return np.hstack([base, pca.transform(hogs)]) if "HOG" in cols else base


def fit_lgbm(x: np.ndarray, y: np.ndarray, cfg: dict):
    import lightgbm as lgb

    return lgb.LGBMClassifier(**cfg["model"]["lightgbm"], random_state=0, verbose=-1).fit(x, y)


def run_t1(cands, hogs, n_gt, cfg, sim_group: pd.Series, n_boot: int) -> pd.DataFrame:
    from sklearn.decomposition import PCA
    from sklearn.metrics import average_precision_score, roc_auc_score
    from sklearn.model_selection import GroupKFold

    val, test = cands["val"], cands["test"].copy()
    pca = PCA(cfg["features"]["hog"]["pca_components"], random_state=0).fit(hogs["val"])
    p0, r0 = pr_at(test, "yolo_score", 0.25, n_gt["test"])
    _, r0_val = pr_at(val, "yolo_score", 0.25, n_gt["val"])
    print("\n=== T1 — Bộ xác minh đặc trưng thủ công (fit val -> đánh giá test) ===")
    print(f"YOLO thuần @0.25 trên test: P {p0:.3f} R {r0:.3f}")
    rows = []
    for name, cols in FEATURE_SETS.items():
        xv = matrix(val, hogs["val"], cols, pca)
        oof = np.zeros(len(val))
        for tr, te in GroupKFold(5).split(xv, val.y, groups=val.image):
            oof[te] = fit_lgbm(xv[tr], val.y.to_numpy()[tr], cfg).predict_proba(xv[te])[:, 1]
        val["oof"] = oof
        thr_val = threshold_for_recall(val, "oof", r0_val - 0.01, n_gt["val"])  # giữ recall ≈ YOLO@0.25 trên val
        model = fit_lgbm(xv, val.y.to_numpy(), cfg)
        test[name] = model.predict_proba(matrix(test, hogs["test"], cols, pca))[:, 1]
        p_dep, r_dep = pr_at(test, name, thr_val, n_gt["test"])
        p_eq, r_eq = pr_at(test, name, threshold_for_recall(test, name, r0, n_gt["test"]), n_gt["test"])
        rows.append(
            {
                "tap_dac_trung": name,
                "AUC": roc_auc_score(test.y, test[name]),
                "AP_ung_vien": average_precision_score(test.y, test[name]),
                "P_cung_recall": p_eq,
                "R_cung_recall": r_eq,
                "P_nguong_val": p_dep,
                "R_nguong_val": r_dep,
                "nguong_val": thr_val,
            }
        )
    yolo_row = {
        "tap_dac_trung": "YOLO thuần (điểm YOLO)",
        "AUC": roc_auc_score(test.y, test.yolo_score),
        "AP_ung_vien": average_precision_score(test.y, test.yolo_score),
        "P_cung_recall": p0,
        "R_cung_recall": r0,
        "P_nguong_val": p0,
        "R_nguong_val": r0,
        "nguong_val": 0.25,
    }
    table = pd.DataFrame([yolo_row, *rows])
    print(table.round(3).to_string(index=False))

    # CI bootstrap theo ảnh cho cấu hình đầy đủ, ngưỡng chọn trên val
    best = "day_du"
    thr = table.set_index("tap_dac_trung").loc[best, "nguong_val"]
    images = test.image.unique()
    gt_per_img = cands["gt_per_image"]
    rng = np.random.default_rng(0)
    by_img = {k: g for k, g in test.groupby("image")}
    deltas = []
    for _ in range(n_boot):
        pick = rng.choice(images, len(images))
        sub = pd.concat([by_img[i] for i in pick])
        ngt = int(sum(gt_per_img.get(i, 0) for i in pick))
        pa, ra = pr_at(sub, "yolo_score", 0.25, ngt)
        pb, rb = pr_at(sub, best, thr, ngt)
        deltas.append((pb - pa, rb - ra))
    lo, hi = np.percentile(np.array(deltas), [2.5, 97.5], axis=0)
    p_b, r_b = pr_at(test, best, thr, n_gt["test"])
    print(
        f"\n'{best}' (ngưỡng val {thr:.3f}) so với YOLO @0.25 trên test: "
        f"ΔP {p_b - p0:+.3f} [CI95 {lo[0]:+.3f}; {hi[0]:+.3f}] · ΔR {r_b - r0:+.3f} [CI95 {lo[1]:+.3f}; {hi[1]:+.3f}]"
    )

    # Theo độ giống ảnh train
    test["nhom"] = test.image.map(sim_group)
    out = []
    for g, d in test.groupby("nhom", observed=True):
        ngt = int(sum(gt_per_img.get(i, 0) for i in sim_group[sim_group == g].index))
        pa, ra = pr_at(d, "yolo_score", 0.25, ngt)
        pb, rb = pr_at(d, best, thr, ngt)
        out.append({"nhom": g, "bien": ngt, "P_yolo": pa, "R_yolo": ra, "P_xac_minh": pb, "R_xac_minh": rb})
    print("\nTheo độ giống ảnh train (pHash tới ảnh train gần nhất):")
    print(pd.DataFrame(out).round(3).to_string(index=False))

    # Thành phần dương tính giả còn lại
    for label, kept in (("YOLO @0.25", test[test.yolo_score >= 0.25]), ("xác minh", test[test[best] >= thr])):
        print(
            f"Sai còn lại — {label}: "
            + ", ".join(f"{k} {v}" for k, v in kept[kept.y == 0].outcome.value_counts().items())
        )
    model = fit_lgbm(matrix(val, hogs["val"], FEATURE_SETS[best], pca), val.y.to_numpy(), cfg)
    names = [c for c in FEATURE_SETS[best] if c != "HOG"] + [f"hog_pca{i}" for i in range(pca.n_components_)]
    imp = pd.Series(model.booster_.feature_importance("gain"), index=names).sort_values(ascending=False)
    print("\nĐặc trưng quan trọng nhất (gain):", ", ".join(f"{k} {v / imp.sum():.1%}" for k, v in imp.head(12).items()))
    return table


def similarity_groups(root: Path) -> pd.Series:
    d = load_config("data")["dedup"]
    te_imgs, tr_imgs = list_images(root / "test"), list_images(root / "train")
    te = compute_hashes(te_imgs, d["hash"], d["hash_size"]).astype(np.uint8)
    tr = compute_hashes(tr_imgs, d["hash"], d["hash_size"]).astype(np.uint8)
    nearest = pd.Series([int((tr != row).sum(1).min()) for row in te], index=[p.name for p in te_imgs])
    return pd.cut(nearest, [-1, 10, 14, 64], labels=["giong_train(<=10)", "trung_binh(11-14)", "khac_train(>=15)"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("weights", type=Path, nargs="?", help="mặc định: configs/pipeline.yaml > detector.weights")
    parser.add_argument("--imgsz", type=int, default=960)
    parser.add_argument("--boot", type=int, default=1000)
    parser.add_argument("--out", type=Path, default=Path("reports/feasibility"))
    args = parser.parse_args()
    args.weights = resolve(args.weights or load_config("pipeline")["detector"]["weights"])

    from ultralytics import YOLO

    cfg = load_config("verifier")
    root = resolve(load_config("data")["processed_dir"])
    out = resolve(args.out)
    out.mkdir(parents=True, exist_ok=True)
    model = YOLO(str(args.weights))
    cands, hogs, n_gt = {}, {}, {}
    for split in ("val", "test"):
        cache = out / f"candidates_{split}.pkl"
        if cache.exists():
            cands[split], hogs[split], n_gt[split] = pd.read_pickle(cache)
        else:
            cands[split], hogs[split], n_gt[split] = build_candidates(model, split, args.imgsz, cfg)
            pd.to_pickle((cands[split], hogs[split], n_gt[split]), cache)
    report_t0({k: cands[k] for k in ("val", "test")}, n_gt)

    gt_per_image = {}
    for p in list_images(root / "test"):
        gt_per_image[p.name] = len(read_labels(p.parent.parent / "labels" / f"{p.stem}.txt"))
    cands["gt_per_image"] = gt_per_image
    table = run_t1(cands, hogs, n_gt, cfg, similarity_groups(root), args.boot)
    table.to_csv(out / "t1_feature_sets.csv", index=False)
    print(f"-> {out}")


if __name__ == "__main__":  # bắt buộc trên Windows (DataLoader workers)
    main()
