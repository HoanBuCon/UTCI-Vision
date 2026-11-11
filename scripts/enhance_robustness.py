"""T4 — Tăng cường ảnh thích nghi (CV truyền thống) có giữ được hiệu năng YOLO khi ảnh xấu không. Phụ trách: TV2, TV5.

    python scripts/enhance_robustness.py <yolo11.pt> [--imgsz 960] [--boot 1000] [--out reports/t4]

Ảnh test bị làm xấu nhân tạo (utci_vision.evaluation.experiments.DEGRADATIONS + mức tối mạnh hơn), rồi so sánh YOLO @0.25
trên ảnh (a) không xử lý, (b) qua bước tăng cường thích nghi của pipeline (enhance.assess -> needed_ops -> enhance, ngưỡng
configs/pipeline.yaml), (c) luôn áp gamma + CLAHE (đối chứng: tăng cường không cần đánh giá chất lượng).
Ảnh gốc cũng được đo để kiểm tra bước tăng cường không làm hại ảnh tốt. CI 95%: bootstrap ghép cặp theo ảnh.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from utci_vision.config import load_config, resolve
from utci_vision.data.labels import list_images, read_labels
from utci_vision.enhance import assess, enhance, needed_ops
from utci_vision.evaluation.experiments import darken, gaussian_noise, motion_blur
from utci_vision.evaluation.metrics import iou_matrix

CONDITIONS = {
    "goc": lambda img: img,
    "toi_gamma2.5": lambda img: darken(img, 2.5),
    "rat_toi_gamma3.5": lambda img: darken(img, 3.5),
    "nhieu_sigma15": gaussian_noise,
    "mo_chuyen_dong": motion_blur,
}


def count_hits(pb: np.ndarray, pc: np.ndarray, ps: np.ndarray, gt: np.ndarray, gc: np.ndarray) -> int:
    """Số biển thật được phát hiện đúng lớp (IoU ≥ 0.5, ghép tham lam theo điểm)."""
    if not len(gt) or not len(pb):
        return 0
    iou = iou_matrix(pb, gt) * (pc[:, None] == gc[None, :])
    used: set[int] = set()
    for k in np.argsort(-ps):
        free = [j for j in range(len(gt)) if j not in used and iou[k, j] >= 0.5]
        if free:
            used.add(max(free, key=lambda j: iou[k, j]))
    return len(used)


def run_condition(model, images, gts, degrade, mode: str, pipe: dict, imgsz: int) -> pd.DataFrame:
    rows = []
    for i in range(0, len(images), 16):
        chunk, frames, flagged = images[i : i + 16], [], []
        for path in chunk:
            img = degrade(cv2.imread(str(path)))
            if mode == "thich_nghi":
                ops = needed_ops(assess(img, pipe["quality"]["downscale_width"]), pipe["quality"])
                img = enhance(img, ops, pipe["enhance"]) if ops else img
                flagged.append(bool(ops))
            elif mode == "luon_gamma_clahe":
                img = enhance(img, {"gamma", "clahe"}, pipe["enhance"])
                flagged.append(True)
            else:
                flagged.append(False)
            frames.append(img)
        results = model.predict(frames, imgsz=imgsz, conf=0.25, iou=0.5, verbose=False)
        for path, r, f in zip(chunk, results, flagged):
            gt, gc = gts[path.name]
            pb, pc = r.boxes.xyxy.cpu().numpy(), r.boxes.cls.cpu().numpy().astype(int)
            hits = count_hits(pb, pc, r.boxes.conf.cpu().numpy(), gt, gc)
            rows.append({"image": path.name, "n_gt": len(gt), "pred": len(pb), "tp": hits, "tang_cuong": f})
    return pd.DataFrame(rows)


def pr(d: pd.DataFrame) -> tuple[float, float]:
    return d.tp.sum() / max(d.pred.sum(), 1), d.tp.sum() / max(d.n_gt.sum(), 1)


def paired_ci(a: pd.DataFrame, b: pd.DataFrame, n_boot: int, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """CI 95% của (ΔP, ΔR) = b − a, lấy mẫu lại cùng tập ảnh."""
    rng = np.random.default_rng(seed)
    arr_a, arr_b = a[["tp", "pred", "n_gt"]].to_numpy(), b[["tp", "pred", "n_gt"]].to_numpy()
    out = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(arr_a), len(arr_a))
        sa, sb = arr_a[idx].sum(0), arr_b[idx].sum(0)
        out.append((sb[0] / max(sb[1], 1) - sa[0] / max(sa[1], 1), sb[0] / sb[2] - sa[0] / sa[2]))
    return np.percentile(np.array(out), [2.5, 97.5], axis=0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("weights", type=Path)
    parser.add_argument("--imgsz", type=int, default=960)
    parser.add_argument("--boot", type=int, default=1000)
    parser.add_argument("--out", type=Path, default=Path("reports/t4"))
    args = parser.parse_args()
    from ultralytics import YOLO

    pipe = load_config("pipeline")
    out = resolve(args.out)
    out.mkdir(parents=True, exist_ok=True)
    images = list_images(resolve(load_config("data")["processed_dir"]) / "test")
    gts = {}
    for p in images:
        h, w = cv2.imread(str(p)).shape[:2]
        labels = read_labels(p.parent.parent / "labels" / f"{p.stem}.txt")
        gts[p.name] = (
            np.array([b.to_xyxy(w, h) for b in labels]).reshape(-1, 4),
            np.array([b.class_id for b in labels]),
        )
    model = YOLO(str(args.weights))
    rows = []
    for cond, degrade in CONDITIONS.items():
        base = run_condition(model, images, gts, degrade, "khong", pipe, args.imgsz)
        p0, r0 = pr(base)
        rows.append({"dieu_kien": cond, "che_do": "không xử lý", "ti_le_anh_tang_cuong": 0.0, "P": p0, "R": r0})
        for mode, label in (("thich_nghi", "tăng cường thích nghi"), ("luon_gamma_clahe", "luôn gamma + CLAHE")):
            d = run_condition(model, images, gts, degrade, mode, pipe, args.imgsz)
            p, r = pr(d)
            lo, hi = paired_ci(base, d, args.boot)
            rows.append(
                {
                    "dieu_kien": cond,
                    "che_do": label,
                    "ti_le_anh_tang_cuong": d.tang_cuong.mean(),
                    "P": p,
                    "R": r,
                    "dP": p - p0,
                    "dP_ci95": f"{lo[0]:+.3f};{hi[0]:+.3f}",
                    "dR": r - r0,
                    "dR_ci95": f"{lo[1]:+.3f};{hi[1]:+.3f}",
                }
            )
        print(pd.DataFrame(rows[-3:]).round(3).to_string(index=False), flush=True)
    table = pd.DataFrame(rows)
    table.to_csv(out / "t4_enhance.csv", index=False)
    print(f"-> {out}")


if __name__ == "__main__":
    main()
