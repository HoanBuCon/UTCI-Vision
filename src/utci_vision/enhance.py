"""[CV] Đánh giá chất lượng frame + tăng cường thích nghi (FR-PIPE-01/02). Phụ trách: TV2.

Đánh giá trên ảnh thu nhỏ (< 1 ms); chỉ áp dụng gamma / CLAHE / khử nhiễu khi cần — ảnh bình thường đi thẳng qua.
Ngưỡng ở configs/pipeline.yaml > quality, chọn theo phân vị trên dữ liệu thật (scripts/spike_enhance.py, S1).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np


@dataclass
class FrameQuality:
    mean_v: float  # độ sáng trung bình kênh V (0..1)
    std_l: float  # độ lệch chuẩn kênh L (0..1) — tương phản
    laplacian_var: float  # phương sai Laplacian trên ảnh xám thu nhỏ — nhiễu/chi tiết cao


def assess(image_bgr: np.ndarray, downscale_width: int = 320) -> FrameQuality:
    h, w = image_bgr.shape[:2]
    if w > downscale_width:
        image_bgr = cv2.resize(
            image_bgr, (downscale_width, max(1, round(h * downscale_width / w))), interpolation=cv2.INTER_AREA
        )
    v = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)[..., 2]
    lab_l = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)[..., 0]
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    return FrameQuality(
        mean_v=float(v.mean() / 255.0),
        std_l=float(lab_l.std() / 255.0),
        laplacian_var=float(cv2.Laplacian(gray, cv2.CV_64F).var()),
    )


def needed_ops(quality: FrameQuality, cfg: dict[str, Any]) -> set[str]:
    """Tập con của {"gamma", "clahe", "denoise"} theo ngưỡng configs/pipeline.yaml > quality."""
    ops: set[str] = set()
    if quality.mean_v < cfg["dark_mean_v"]:
        ops |= {"gamma", "clahe"}
    if quality.std_l < cfg["low_contrast_std_l"]:
        ops.add("clahe")
    if quality.laplacian_var > cfg["noisy_laplacian"]:
        ops.add("denoise")
    return ops


def auto_gamma(image_bgr: np.ndarray, target_mean: float = 0.5, lo: float = 0.4, hi: float = 3.0) -> float:
    """Gamma sao cho độ sáng trung bình kênh V tiến về target_mean (out = in^(1/gamma))."""
    mean = float(np.clip(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)[..., 2].mean() / 255.0, 1e-3, 0.999))
    return float(np.clip(np.log(mean) / np.log(target_mean), lo, hi))


def gamma_correct(image_bgr: np.ndarray, gamma: float) -> np.ndarray:
    table = ((np.arange(256) / 255.0) ** (1.0 / max(gamma, 1e-6)) * 255).clip(0, 255).astype(np.uint8)
    return cv2.LUT(image_bgr, table)


def clahe_lab(image_bgr: np.ndarray, clip_limit: float = 2.0, tile_grid: int = 8) -> np.ndarray:
    """CLAHE trên kênh L của LAB — tăng tương phản cục bộ mà không lệch màu biển."""
    l_ch, a_ch, b_ch = cv2.split(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB))
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_grid, tile_grid))
    return cv2.cvtColor(cv2.merge((clahe.apply(l_ch), a_ch, b_ch)), cv2.COLOR_LAB2BGR)


def enhance(image_bgr: np.ndarray, ops: set[str], cfg: dict[str, Any]) -> np.ndarray:
    """gamma tự động -> CLAHE kênh L (LAB) -> lọc song phương, theo `ops` (cfg = configs/pipeline.yaml > enhance)."""
    out = image_bgr
    if "gamma" in ops:
        g = cfg["gamma"]
        out = gamma_correct(out, auto_gamma(out, g["target_mean"], g["min"], g["max"]))
    if "clahe" in ops:
        out = clahe_lab(out, cfg["clahe"]["clip_limit"], cfg["clahe"]["tile_grid"])
    if "denoise" in ops:
        d = cfg["denoise"]
        out = cv2.bilateralFilter(out, d["d"], d["sigma_color"], d["sigma_space"])
    return out
