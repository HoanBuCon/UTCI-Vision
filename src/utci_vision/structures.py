"""Kiểu dữ liệu dùng chung giữa pipeline, API và đánh giá."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

BBox = tuple[float, float, float, float]  # x1, y1, x2, y2 (pixel)


@dataclass
class SignValue:
    """Giá trị số trên biển (km/h, m, T)."""

    number: float
    unit: str
    confidence: float = 0.0


@dataclass
class SignText:
    """Chữ đọc được trên biển chính / biển phụ và nghĩa đã phân tích."""

    raw: str
    text: str
    confidence: float = 0.0
    parsed: dict[str, Any] = field(default_factory=dict)


@dataclass
class Detection:
    """Một biển báo. `score` = điểm YOLO, hoặc xác suất đã hiệu chỉnh sau bộ xác minh."""

    bbox: BBox
    class_id: int
    score: float
    verified: bool | None = None
    track_id: int | None = None
    value: SignValue | None = None
    text: SignText | None = None
    sub_sign: SignText | None = None

    @property
    def height(self) -> float:
        return self.bbox[3] - self.bbox[1]
