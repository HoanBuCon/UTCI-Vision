"""Metric phát hiện dùng chung cho cả 3 chế độ (FR-EVAL-01).

AP tính theo nội suy 101 điểm (kiểu COCO). Với YOLO có thể đối chiếu bằng `model.val()` của Ultralytics.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np

from ..structures import Detection

Box = tuple[float, float, float, float]


def iou(a: Box, b: Box) -> float:
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def average_precision(recall: np.ndarray, precision: np.ndarray) -> float:
    """AP kiểu COCO: precision làm đơn điệu giảm, lấy mẫu tại 101 mức recall 0, 0.01, ..., 1."""
    if len(recall) == 0:
        return 0.0
    prec = np.flip(np.maximum.accumulate(np.flip(precision)))
    x = np.linspace(0, 1, 101)
    idx = np.searchsorted(recall, x, side="left")
    sampled = np.zeros_like(x)
    valid = idx < len(recall)
    sampled[valid] = prec[idx[valid]]
    return float(sampled.mean())


def evaluate_detections(
    predictions: list[list[Detection]],
    ground_truths: list[list[tuple[int, Box]]],
    num_classes: int,
    iou_thresholds: tuple[float, ...] = tuple(np.round(np.arange(0.5, 0.96, 0.05), 2)),
) -> dict:
    """predictions[i] / ground_truths[i] là kết quả và GT (class_id, bbox) của ảnh thứ i.

    Trả về {"map50", "map50_95", "ap50_per_class", "precision", "recall"} (P/R tại IoU 0.5, mọi điểm tin cậy).
    """
    ap = np.full((num_classes, len(iou_thresholds)), np.nan)
    n_gt = np.zeros(num_classes, dtype=int)
    for gts in ground_truths:
        for c, _ in gts:
            n_gt[c] += 1

    tp_total = fp_total = 0
    for c in range(num_classes):
        preds = [(img_idx, d) for img_idx, dets in enumerate(predictions) for d in dets if d.class_id == c]
        preds.sort(key=lambda t: -t[1].score)
        gt_by_img = defaultdict(list)
        for img_idx, gts in enumerate(ground_truths):
            gt_by_img[img_idx] = [b for cls, b in gts if cls == c]
        if n_gt[c] == 0:
            continue
        for ti, thr in enumerate(iou_thresholds):
            matched = {k: np.zeros(len(v), dtype=bool) for k, v in gt_by_img.items()}
            tp = np.zeros(len(preds))
            for pi, (img_idx, det) in enumerate(preds):
                gts = gt_by_img[img_idx]
                if not gts:
                    continue
                ious = np.array([iou(det.bbox, g) for g in gts])
                best = int(ious.argmax())
                if ious[best] >= thr and not matched[img_idx][best]:
                    matched[img_idx][best] = True
                    tp[pi] = 1
            ctp, cfp = np.cumsum(tp), np.cumsum(1 - tp)
            recall = ctp / n_gt[c]
            precision = ctp / np.maximum(ctp + cfp, 1e-9)
            ap[c, ti] = average_precision(recall, precision) if len(preds) else 0.0
            if ti == 0:
                tp_total += int(tp.sum())
                fp_total += int(len(preds) - tp.sum())

    valid = ~np.isnan(ap[:, 0])
    return {
        "map50": float(np.nanmean(ap[:, 0])) if valid.any() else 0.0,
        "map50_95": float(np.nanmean(ap)) if valid.any() else 0.0,
        "ap50_per_class": {c: float(ap[c, 0]) for c in range(num_classes) if valid[c]},
        "precision": tp_total / max(tp_total + fp_total, 1),
        "recall": tp_total / max(int(n_gt.sum()), 1),
    }


def size_bucket(box: Box) -> str:
    """Phân loại kích thước theo quy ước COCO (diện tích pixel)."""
    area = (box[2] - box[0]) * (box[3] - box[1])
    return "small" if area < 32**2 else "medium" if area < 96**2 else "large"
