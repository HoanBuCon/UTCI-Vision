"""[CV] Tracking kiểu SORT: Kalman (cx, cy, w, h + vận tốc) + ghép IoU Hungarian + bỏ phiếu nhãn (FR-PIPE-04).
Phụ trách: TV2 — S3.

Track giữ thêm trạng thái của tác vụ nền (crop tốt nhất, kết quả xác minh / đọc số / OCR) để pipeline
chỉ chạy lại khi cần (FR-PIPE-12).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np

from .structures import Detection, SignText, SignValue


@dataclass
class Track:
    track_id: int
    kalman: object  # cv2.KalmanFilter 8 trạng thái / 4 đo
    history: deque = field(default_factory=deque)  # (class_id, score) trong cửa sổ bỏ phiếu
    hits: int = 0
    misses: int = 0
    best_crop: np.ndarray | None = None
    best_crop_score: float = 0.0
    last_task_frame: int = -1
    verified: bool | None = None
    verified_score: float | None = None
    value: SignValue | None = None
    text: SignText | None = None
    sub_sign: SignText | None = None


class Tracker:
    def __init__(self, iou_threshold: float, max_age: int, min_hits: int, vote_window: int):
        self.iou_threshold, self.max_age = iou_threshold, max_age
        self.min_hits, self.vote_window = min_hits, vote_window
        self.tracks: list[Track] = []

    def update(self, detections: list[Detection], frame_idx: int) -> list[Detection]:
        """Predict -> ghép IoU -> cập nhật/tạo/xoá track. Trả detection của track đã xác nhận (≥ min_hits),
        kèm track_id, nhãn bỏ phiếu và kết quả tác vụ nền đã có."""
        raise NotImplementedError("TODO(TV2, S3)")
