"""Vẽ kết quả lên ảnh/video phía server (ảnh annotate, video job, infer). Nhãn tiếng Việt cần Pillow
vì cv2.putText không hỗ trợ Unicode. Phụ trách: TV3 — S2."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np

from .structures import Detection

SUPERCLASS_COLORS = {
    "prohibitory": (40, 40, 220),
    "warning": (0, 200, 255),
    "mandatory": (220, 120, 0),
    "info": (200, 160, 0),
    "other": (119, 119, 119),
}  # BGR, khớp web/src/styles.css
FONTS = [
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
]


@lru_cache(maxsize=8)
def _font(size: int):
    from PIL import ImageFont

    for path in FONTS:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def label_of(det: Detection) -> str:
    from .config import load_classes

    parts = [load_classes()[det.class_id].name_vi]
    if det.value is not None:
        parts.append(f"{det.value.number:g} {det.value.unit}")
    parts.append(f"{det.score:.2f}")
    if det.track_id is not None:
        parts.insert(0, f"#{det.track_id}")
    return " · ".join(parts)


def draw(image_bgr: np.ndarray, detections: list[Detection]) -> np.ndarray:
    """Box màu theo siêu lớp + "tên · giá trị · độ tin cậy" (+ chữ biển phụ)."""
    from PIL import Image, ImageDraw

    from .config import load_classes

    classes = load_classes()
    img = Image.fromarray(image_bgr[..., ::-1].copy())
    pen = ImageDraw.Draw(img)
    size = max(12, image_bgr.shape[0] // 45)
    font = _font(size)
    width = max(2, image_bgr.shape[0] // 400)
    for det in detections:
        b, g, r = SUPERCLASS_COLORS.get(classes[det.class_id].superclass, (0, 255, 0))
        color = (r, g, b)
        x1, y1, x2, y2 = det.bbox
        pen.rectangle([x1, y1, x2, y2], outline=color, width=width)
        lines = [label_of(det)]
        if det.text is not None and det.text.text:
            lines.append(det.text.text)
        if det.sub_sign is not None and det.sub_sign.text:
            lines.append(f"Biển phụ: {det.sub_sign.text}")
        ty = y1 - (size + 4) * len(lines) if y1 - (size + 4) * len(lines) > 0 else y2 + 2
        for line in lines:
            tw = pen.textlength(line, font=font)
            pen.rectangle([x1, ty, x1 + tw + 6, ty + size + 4], fill=color)
            pen.text((x1 + 3, ty + 1), line, fill=(255, 255, 255), font=font)
            ty += size + 4
    return np.asarray(img)[..., ::-1].copy()
