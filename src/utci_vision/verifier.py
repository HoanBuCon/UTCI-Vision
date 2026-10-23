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

import numpy as np
import pandas as pd

from .structures import BBox, Detection

FEATURE_NAMES: list[str] = []  # TODO(TV2): tên theo đúng thứ tự vector (dùng cho feature importance)


def region_features(image_bgr: np.ndarray, bbox: BBox, cfg: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """[CV] -> (đặc trưng màu/hình dạng/Hu/độ nét, HOG thô)."""
    raise NotImplementedError("TODO(TV2, S2)")


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
