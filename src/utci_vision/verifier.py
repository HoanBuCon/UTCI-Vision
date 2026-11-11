"""[CV + ML] Bộ xác minh: đặc trưng vùng (CV) + LightGBM stacking trên dự đoán YOLO (FR-PIPE-05/06, FR-TRAIN-05).
Phụ trách: TV2 (đặc trưng, S2) · TV1 (mô hình, S3).

- Đặc trưng vùng [CV]: tỉ lệ pixel đỏ/xanh/vàng/trắng (mask HSV) · độ tròn 4πA/P², số đỉnh approxPolyDP, solidity,
  tỉ lệ khung của contour lớn nhất · 7 Hu moments (log) · HOG crop xám 32×32 (→ PCA) · độ nét (phương sai Laplacian).
- Mô hình [ML]: mỗi mẫu = một box YOLO ở tập val (proposal_conf thấp); đặc trưng = [điểm YOLO, siêu lớp + id lớp,
  kích thước/vị trí box, đặc trưng vùng, độ khớp màu/hình dạng với siêu lớp]; nhãn = 1 nếu khớp GT cùng lớp.
  Fit (không pretrained), hiệu chỉnh xác suất; đầu ra thay cho điểm YOLO.
Tham số: configs/verifier.yaml.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import pandas as pd

from .structures import BBox, Detection

COLORS = ("red", "blue", "yellow", "white")
# Nhóm đặc trưng (ablation E3: màu / +hình học / +HOG). Thứ tự = thứ tự vector của region_features (chưa gồm HOG).
FEATURE_GROUPS: dict[str, list[str]] = {
    "color": [f"{c}_{part}" for c in COLORS for part in ("all", "ring", "core")],
    "shape": ["circularity", "n_vertices", "solidity", "extent", "contour_area", "contour_aspect", "contour_found"],
    "hu": [f"hu{i}" for i in range(1, 8)],
    "quality": ["sharpness", "mean_v", "std_l"],
}
FEATURE_NAMES: list[str] = [name for names in FEATURE_GROUPS.values() for name in names]


def crop_region(image_bgr: np.ndarray, bbox: BBox, pad_ratio: float, size: int) -> np.ndarray:
    """Cắt box (nới `pad_ratio` mỗi phía, kẹp trong ảnh) và đưa về size×size."""
    h, w = image_bgr.shape[:2]
    x1, y1, x2, y2 = bbox
    px, py = (x2 - x1) * pad_ratio, (y2 - y1) * pad_ratio
    x1, y1 = int(max(0, np.floor(x1 - px))), int(max(0, np.floor(y1 - py)))
    x2, y2 = int(min(w, np.ceil(x2 + px))), int(min(h, np.ceil(y2 + py)))
    crop = image_bgr[y1 : max(y2, y1 + 1), x1 : max(x2, x1 + 1)]
    return cv2.resize(crop, (size, size), interpolation=cv2.INTER_AREA if crop.shape[0] > size else cv2.INTER_CUBIC)


def color_masks(crop_bgr: np.ndarray, ranges: dict[str, list]) -> dict[str, np.ndarray]:
    """Mask nhị phân theo các dải HSV trong configs/verifier.yaml (đỏ có 2 dải vì H quấn quanh 0/180)."""
    hsv = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2HSV)
    masks = {}
    for name in COLORS:
        m = np.zeros(hsv.shape[:2], np.uint8)
        for lo, hi in ranges[name]:
            m |= cv2.inRange(hsv, np.array(lo, np.uint8), np.array(hi, np.uint8))
        masks[name] = m > 0
    return masks


def _shape_features(mask: np.ndarray, approx_eps: float) -> tuple[list[float], np.ndarray]:
    """Đặc trưng hình học + 7 Hu moments (log) của contour ngoài lớn nhất trong `mask`."""
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [c for c in contours if cv2.contourArea(c) > 0]
    if not contours:
        return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], np.zeros(7)
    c = max(contours, key=cv2.contourArea)
    area, perimeter = cv2.contourArea(c), cv2.arcLength(c, True)
    hull_area = cv2.contourArea(cv2.convexHull(c))
    _, _, bw, bh = cv2.boundingRect(c)
    n_vertices = len(cv2.approxPolyDP(c, approx_eps * perimeter, True))
    total = float(mask.size)
    shape = [
        4 * np.pi * area / (perimeter**2 + 1e-9),  # 1 = hình tròn hoàn hảo
        float(n_vertices),  # 3 = tam giác, 4 = chữ nhật, nhiều = tròn
        area / (hull_area + 1e-9),
        area / (bw * bh + 1e-9),
        area / total,
        bw / (bh + 1e-9),
        1.0,
    ]
    hu = cv2.HuMoments(cv2.moments(c)).ravel()
    return shape, -np.sign(hu) * np.log10(np.abs(hu) + 1e-30)


def region_features(image_bgr: np.ndarray, bbox: BBox, cfg: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """[CV] Đặc trưng thủ công của một vùng -> (vector theo FEATURE_NAMES, HOG thô chưa giảm chiều).

    cfg = configs/verifier.yaml. Màu tính trên toàn crop, vành ngoài (viền biển) và lõi; hình học + Hu trên contour lớn
    nhất của mask đỏ/xanh/vàng (không có màu biển thì dùng ngưỡng Otsu trên ảnh xám); HOG trên crop xám size×size.
    """
    from skimage.feature import hog

    f = cfg["features"]
    crop = crop_region(image_bgr, bbox, cfg["build"]["crop_pad_ratio"], f["crop_size"])
    size = crop.shape[0]
    yy, xx = np.mgrid[:size, :size]
    r = np.hypot(xx - (size - 1) / 2, yy - (size - 1) / 2) / (size / 2)
    ring, core = (r > 0.6) & (r <= 1.0), r <= 0.6  # vùng sau khi nới pad: viền biển rơi vào vành 0.6–1.0

    masks = color_masks(crop, f["color_ranges"])
    color = [float(m[region].mean()) for m in masks.values() for region in (np.ones_like(m), ring, core)]

    sign_mask = masks["red"] | masks["blue"] | masks["yellow"]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    if sign_mask.mean() < 0.05:
        _, otsu = cv2.threshold(gray, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        sign_mask = otsu.astype(bool)
    sign_mask = cv2.morphologyEx(sign_mask.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    shape, hu = _shape_features(sign_mask, f["approx_eps"])

    lab_l = cv2.cvtColor(crop, cv2.COLOR_BGR2LAB)[..., 0]
    quality = [
        float(cv2.Laplacian(gray, cv2.CV_64F).var()),
        float(cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)[..., 2].mean() / 255.0),
        float(lab_l.std() / 255.0),
    ]

    h = f["hog"]
    hog_raw = hog(
        cv2.resize(gray, (h["size"], h["size"]), interpolation=cv2.INTER_AREA),
        orientations=h["orientations"],
        pixels_per_cell=tuple(h["pixels_per_cell"]),
        cells_per_block=tuple(h["cells_per_block"]),
        feature_vector=True,
    )
    return np.array(color + shape + list(hu) + quality, dtype=np.float32), hog_raw.astype(np.float32)


@dataclass
class VerifierBundle:
    """Lưu chung một file joblib: mô hình đã hiệu chỉnh + PCA cho HOG + tên đặc trưng + ngưỡng."""

    model: Any
    hog_pca: Any
    feature_names: list[str]
    threshold: float = 0.5


def build_dataset(yolo_weights: Path, split_dir: Path, cfg: dict[str, Any], limit: int | None = None) -> pd.DataFrame:
    """Chạy YOLO trên split -> đặc trưng + nhãn; một dòng / box, cột `image` để chia fold theo ảnh."""
    raise NotImplementedError("TODO(TV1, S3)")


def train(df: pd.DataFrame, run_dir: Path, cfg: dict[str, Any]) -> dict[str, float]:
    """GroupKFold theo ảnh; so sánh lightgbm / logreg / rf (E3); lưu run_dir/verifier.joblib."""
    raise NotImplementedError("TODO(TV1, S3)")


class Verifier:
    def __init__(self, weights: Path):
        self.bundle: VerifierBundle | None = None  # TODO(TV1, S3): joblib.load(weights)

    def verify(self, image_bgr: np.ndarray, detections: list[Detection]) -> list[Detection]:
        """score = xác suất đã hiệu chỉnh; verified = score ≥ threshold."""
        raise NotImplementedError("TODO(TV1, S3)")
