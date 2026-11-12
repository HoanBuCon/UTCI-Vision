"""[CV truyền thống] Pipeline nhận diện biển báo không dùng học sâu — đối chứng với YOLO11 (E8, trang So sánh).

    ảnh ─► đánh giá chất lượng + tăng cường thích nghi (enhance.py)
        ─► phân đoạn màu HSV (đỏ / xanh / vàng) ─► hình thái học (mở / đóng)
        ─► contour ─► lọc hình dạng (độ tròn, số đỉnh, solidity, tỉ lệ khung) ─► vùng ứng viên
        ─► đặc trưng thủ công HOG + histogram màu HSV ─► SVM (RBF) ─► lớp biển + xác suất

Tham số: configs/verifier.yaml (dải màu HSV, HOG) và configs/traditional.yaml (lọc contour). Bộ phân loại huấn luyện bằng
scripts/train_hog_svm.py -> models/current/hog_svm.joblib.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from .structures import BBox, Detection

SHAPE_COLORS = {"red": (40, 40, 220), "blue": (220, 120, 0), "yellow": (0, 200, 255)}  # BGR


# ---------------------------------------------------------------- đặc trưng thủ công


def hog_features(crops: list[np.ndarray], hog_cfg: dict[str, Any]) -> np.ndarray:
    """HOG trên crop xám size×size (một vector cố định cho mọi kích thước biển)."""
    from skimage.feature import hog

    size = hog_cfg["size"]
    out = []
    for c in crops:
        g = cv2.resize(cv2.cvtColor(c, cv2.COLOR_BGR2GRAY), (size, size), interpolation=cv2.INTER_AREA)
        out.append(
            hog(
                g,
                orientations=hog_cfg["orientations"],
                pixels_per_cell=tuple(hog_cfg["pixels_per_cell"]),
                cells_per_block=tuple(hog_cfg["cells_per_block"]),
            )
        )
    return np.array(out, np.float32).reshape(len(crops), -1)


def hsv_hist(crops: list[np.ndarray]) -> np.ndarray:
    """Histogram HSV 16 bin H × 4 bin S, chuẩn hoá — mã hoá màu QCVN (viền đỏ, nền xanh, nền vàng)."""
    out = []
    for c in crops:
        hsv = cv2.cvtColor(cv2.resize(c, (32, 32), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [16, 4], [0, 180, 0, 256]).ravel()
        out.append(hist / (hist.sum() + 1e-9))
    return np.array(out, np.float32).reshape(len(crops), -1)


def classic_features(crops: list[np.ndarray], hog_cfg: dict[str, Any]) -> np.ndarray:
    return np.hstack([hog_features(crops, hog_cfg), hsv_hist(crops)])


def padded_crop(image: np.ndarray, box: BBox, pad: float = 0.1) -> np.ndarray:
    h, w = image.shape[:2]
    x1, y1, x2, y2 = box
    pw, ph = (x2 - x1) * pad, (y2 - y1) * pad
    return image[max(0, int(y1 - ph)) : min(h, int(y2 + ph)), max(0, int(x1 - pw)) : min(w, int(x2 + pw))]


def hog_image(crop: np.ndarray, hog_cfg: dict[str, Any], size: int = 128) -> np.ndarray:
    """Ảnh trực quan HOG (độ lớn gradient theo từng ô) để hiển thị trên web."""
    from skimage.exposure import rescale_intensity
    from skimage.feature import hog

    g = cv2.resize(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY), (size, size), interpolation=cv2.INTER_AREA)
    _, vis = hog(
        g, orientations=hog_cfg["orientations"], pixels_per_cell=(16, 16), cells_per_block=(1, 1), visualize=True
    )
    vis = (rescale_intensity(vis, out_range=(0, 255))).astype(np.uint8)
    return cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)


def sift_keypoints(crop: np.ndarray, size: int = 128) -> tuple[np.ndarray, int]:
    """Điểm SIFT trên crop (phóng về size) — minh hoạ vì sao SIFT kém trên biển nhỏ."""
    g = cv2.resize(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY), (size, size), interpolation=cv2.INTER_CUBIC)
    kps = cv2.SIFT_create().detect(g, None)
    vis = cv2.drawKeypoints(
        cv2.cvtColor(g, cv2.COLOR_GRAY2BGR), kps, None, (0, 220, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
    )
    return vis, len(kps)


# ---------------------------------------------------------------- bộ phân loại HOG + màu + SVM


@dataclass
class ClassicClassifier:
    """SVM (RBF) trên HOG + histogram HSV; lưu bằng joblib."""

    model: Any
    hog_cfg: dict[str, Any]
    metrics: dict[str, float] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> ClassicClassifier:
        import joblib

        return joblib.load(path)

    def save(self, path: Path) -> None:
        import joblib

        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    def predict(self, crops: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
        """-> (lớp, xác suất của lớp đó)."""
        if not crops:
            return np.zeros(0, int), np.zeros(0)
        proba = self.model.predict_proba(classic_features(crops, self.hog_cfg))
        idx = proba.argmax(1)
        return self.model.classes_[idx].astype(int), proba[np.arange(len(idx)), idx]


# ---------------------------------------------------------------- phát hiện bằng màu + hình dạng


@dataclass
class Candidate:
    bbox: BBox
    color: str
    shape: str
    circularity: float
    vertices: int


def _mask(hsv: np.ndarray, ranges: list) -> np.ndarray:
    m = np.zeros(hsv.shape[:2], np.uint8)
    for lo, hi in ranges:
        m |= cv2.inRange(hsv, np.array(lo, np.uint8), np.array(hi, np.uint8))
    return m


def color_shape_candidates(
    image_bgr: np.ndarray, color_ranges: dict, cfg: dict[str, Any]
) -> tuple[list[Candidate], dict[str, np.ndarray]]:
    """Phân đoạn màu HSV -> hình thái học -> contour -> lọc hình dạng; trả vùng ứng viên + mask từng màu."""
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    kernel = np.ones((cfg["morph_kernel"], cfg["morph_kernel"]), np.uint8)
    h, w = image_bgr.shape[:2]
    out, masks = [], {}
    for color in ("red", "blue", "yellow"):
        m = _mask(hsv, color_ranges[color])
        m = cv2.morphologyEx(cv2.morphologyEx(m, cv2.MORPH_OPEN, kernel), cv2.MORPH_CLOSE, kernel)
        masks[color] = m
        contours, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            area = cv2.contourArea(c)
            x, y, bw, bh = cv2.boundingRect(c)
            if area < cfg["min_area"] or bw * bh > cfg["max_area_ratio"] * h * w:
                continue
            aspect = bw / max(bh, 1)
            peri = cv2.arcLength(c, True)
            circ = 4 * np.pi * area / (peri**2 + 1e-9)
            vertices = len(cv2.approxPolyDP(c, cfg["approx_eps"] * peri, True))
            solidity = area / (cv2.contourArea(cv2.convexHull(c)) + 1e-9)
            # viền đỏ của biển cấm là vòng rỗng -> dùng hình bao lồi, đánh giá theo độ tròn của bao lồi
            hull = cv2.convexHull(c)
            hull_circ = 4 * np.pi * cv2.contourArea(hull) / (cv2.arcLength(hull, True) ** 2 + 1e-9)
            shape = None
            if 0.6 <= aspect <= 1.6 and hull_circ >= cfg["min_circularity"]:
                shape = "tròn"
            elif color in ("red", "yellow") and vertices == 3 and 0.7 <= aspect <= 1.5 and solidity > 0.6:
                shape = "tam giác"
            elif color == "blue" and 4 <= vertices <= 6 and 0.5 <= aspect <= 3.0 and solidity > 0.8:
                shape = "chữ nhật"
            if shape:
                out.append(
                    Candidate((float(x), float(y), float(x + bw), float(y + bh)), color, shape, float(circ), vertices)
                )
    return _nms(out, 0.3), masks


def _nms(cands: list[Candidate], iou_thr: float) -> list[Candidate]:
    from .evaluation.metrics import iou

    cands = sorted(cands, key=lambda c: -(c.bbox[2] - c.bbox[0]) * (c.bbox[3] - c.bbox[1]))
    keep: list[Candidate] = []
    for c in cands:
        if all(iou(c.bbox, k.bbox) < iou_thr and _inside(c.bbox, k.bbox) < 0.7 for k in keep):
            keep.append(c)
    return keep


def _inside(small: BBox, big: BBox) -> float:
    """Tỉ lệ diện tích của `small` nằm trong `big` (mảnh màu bên trong một biển lớn hơn)."""
    ix = max(0.0, min(small[2], big[2]) - max(small[0], big[0]))
    iy = max(0.0, min(small[3], big[3]) - max(small[1], big[1]))
    return ix * iy / max((small[2] - small[0]) * (small[3] - small[1]), 1e-9)


def detect(
    image_bgr: np.ndarray, clf: ClassicClassifier, color_ranges: dict, cfg: dict[str, Any]
) -> tuple[list[Detection], list[Candidate], dict[str, Any]]:
    """Pipeline truyền thống đầy đủ -> (phát hiện đã phân loại, mọi ứng viên, thời gian + mask)."""
    t0 = time.perf_counter()
    cands, masks = color_shape_candidates(image_bgr, color_ranges, cfg)
    t1 = time.perf_counter()
    crops = [padded_crop(image_bgr, c.bbox) for c in cands]
    cls, prob = clf.predict([c for c in crops if c.size]) if cands else (np.zeros(0, int), np.zeros(0))
    t2 = time.perf_counter()
    dets = [Detection(c.bbox, int(k), float(p)) for c, k, p in zip(cands, cls, prob) if p >= cfg["min_confidence"]]
    info = {
        "ms": {"segment": (t1 - t0) * 1000, "classify": (t2 - t1) * 1000, "total": (t2 - t0) * 1000},
        "masks": masks,
    }
    return dets, cands, info


def overlay_masks(image_bgr: np.ndarray, masks: dict[str, np.ndarray]) -> np.ndarray:
    """Tô màu các mask lên ảnh xám mờ để thấy vùng mỗi màu."""
    base = cv2.cvtColor(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR) // 2
    for color, m in masks.items():
        base[m > 0] = SHAPE_COLORS[color]
    return base


def draw_candidates(image_bgr: np.ndarray, cands: list[Candidate]) -> np.ndarray:
    out = image_bgr.copy()
    for c in cands:
        x1, y1, x2, y2 = (int(v) for v in c.bbox)
        cv2.rectangle(out, (x1, y1), (x2, y2), SHAPE_COLORS[c.color], 2)
    return out
