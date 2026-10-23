"""Vẽ kết quả lên ảnh/video phía server (ảnh annotate, video job, infer). Nhãn tiếng Việt cần Pillow
vì cv2.putText không hỗ trợ Unicode. Phụ trách: TV3 — S2."""

from __future__ import annotations

import numpy as np

from .structures import Detection

SUPERCLASS_COLORS = {
    "prohibitory": (40, 40, 220),
    "warning": (0, 200, 255),
    "mandatory": (220, 120, 0),
    "info": (200, 160, 0),
}  # BGR, khớp web/src/styles.css
FONTS = ["C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]


def draw(image_bgr: np.ndarray, detections: list[Detection]) -> np.ndarray:
    """Box màu theo siêu lớp + "tên · giá trị · độ tin cậy" (+ chữ biển phụ)."""
    raise NotImplementedError("TODO(TV3, S2)")
