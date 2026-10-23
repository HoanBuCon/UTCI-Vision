"""[CV] Đánh giá chất lượng frame + tăng cường thích nghi (FR-PIPE-01/02). Phụ trách: TV2 — S2.

Đánh giá trên ảnh thu nhỏ (< 1 ms); chỉ áp dụng gamma / CLAHE / khử nhiễu khi cần — ảnh bình thường đi thẳng qua.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class FrameQuality:
    mean_v: float  # độ sáng trung bình kênh V (0..1)
    std_l: float  # độ lệch chuẩn kênh L (0..1)
    laplacian_var: float  # phương sai Laplacian


def assess(image_bgr: np.ndarray, downscale_width: int = 320) -> FrameQuality:
    raise NotImplementedError("TODO(TV2, S2)")


def needed_ops(quality: FrameQuality, cfg: dict[str, Any]) -> set[str]:
    """Tập con của {"gamma", "clahe", "denoise"} theo ngưỡng configs/pipeline.yaml > quality."""
    raise NotImplementedError("TODO(TV2, S2)")


def enhance(image_bgr: np.ndarray, ops: set[str], cfg: dict[str, Any]) -> np.ndarray:
    """gamma tự động -> CLAHE kênh L (LAB) -> lọc song phương, theo `ops`."""
    raise NotImplementedError("TODO(TV2, S2)")
