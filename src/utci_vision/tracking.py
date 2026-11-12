"""[CV] Tracking kiểu SORT: Kalman (cx, cy, w, h + vận tốc) + ghép IoU Hungarian + bỏ phiếu nhãn (FR-PIPE-04).
Phụ trách: TV2 — S3.

Track giữ thêm trạng thái của tác vụ nền (crop tốt nhất, kết quả xác minh / đọc số / OCR) để pipeline
chỉ chạy lại khi cần (FR-PIPE-12).
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field, replace

import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment

from .evaluation.metrics import iou_matrix
from .structures import BBox, Detection, SignText, SignValue


def _new_kalman(bbox: BBox) -> cv2.KalmanFilter:
    """Trạng thái [cx, cy, w, h, vcx, vcy, vw, vh], đo [cx, cy, w, h], mô hình vận tốc không đổi (đơn vị: frame)."""
    kf = cv2.KalmanFilter(8, 4)
    kf.transitionMatrix = np.eye(8, dtype=np.float32)
    for i in range(4):
        kf.transitionMatrix[i, i + 4] = 1.0
    kf.measurementMatrix = np.eye(4, 8, dtype=np.float32)
    kf.processNoiseCov = np.diag([1, 1, 1, 1, 0.5, 0.5, 0.2, 0.2]).astype(np.float32)
    kf.measurementNoiseCov = np.diag([1, 1, 4, 4]).astype(np.float32)
    kf.errorCovPost = np.diag([10, 10, 10, 10, 100, 100, 100, 100]).astype(np.float32)
    kf.statePost = np.vstack([_to_z(bbox), np.zeros((4, 1), np.float32)])
    return kf


def _to_z(bbox: BBox) -> np.ndarray:
    x1, y1, x2, y2 = bbox
    return np.array([[(x1 + x2) / 2], [(y1 + y2) / 2], [x2 - x1], [y2 - y1]], np.float32)


def _to_bbox(state: np.ndarray) -> BBox:
    cx, cy, w, h = (float(v) for v in state[:4, 0])
    w, h = max(w, 1.0), max(h, 1.0)
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


@dataclass
class Track:
    track_id: int
    kalman: cv2.KalmanFilter  # 8 trạng thái / 4 đo
    history: deque = field(default_factory=deque)  # (class_id, score) trong cửa sổ bỏ phiếu
    hits: int = 0
    misses: int = 0
    bbox: BBox = (0.0, 0.0, 0.0, 0.0)
    score: float = 0.0
    best_crop: np.ndarray | None = None
    best_crop_score: float = 0.0
    last_task_frame: int = -1
    verified: bool | None = None
    verified_score: float | None = None
    value: SignValue | None = None
    text: SignText | None = None
    sub_sign: SignText | None = None
    readings: dict[str, list] = field(default_factory=lambda: {"value": [], "text": [], "sub_sign": []})

    def voted_class(self) -> tuple[int, float]:
        """Lớp có tổng điểm lớn nhất trong cửa sổ + điểm trung bình của lớp đó."""
        totals: dict[int, list[float]] = defaultdict(list)
        for cls, score in self.history:
            totals[cls].append(score)
        cls = max(totals, key=lambda c: sum(totals[c]))
        return cls, float(np.mean(totals[cls]))


class Tracker:
    def __init__(self, iou_threshold: float, max_age: int, min_hits: int, vote_window: int):
        self.iou_threshold, self.max_age = iou_threshold, max_age
        self.min_hits, self.vote_window = min_hits, vote_window
        self.tracks: list[Track] = []
        self._next_id = 1

    def update(self, detections: list[Detection], frame_idx: int) -> list[Detection]:
        """Predict -> ghép IoU -> cập nhật/tạo/xoá track. Trả detection của track đã xác nhận (≥ min_hits),
        kèm track_id, nhãn bỏ phiếu và kết quả tác vụ nền đã có."""
        predicted = [_to_bbox(t.kalman.predict()) for t in self.tracks]
        matches, unmatched_det = self._associate(detections, predicted)

        matched_tracks = set()
        for d_idx, t_idx in matches:
            track, det = self.tracks[t_idx], detections[d_idx]
            track.kalman.correct(_to_z(det.bbox))
            track.bbox, track.score = _to_bbox(track.kalman.statePost), det.score
            track.history.append((det.class_id, det.score))
            track.hits, track.misses = track.hits + 1, 0
            matched_tracks.add(t_idx)
        for t_idx, track in enumerate(self.tracks):
            if t_idx not in matched_tracks:
                track.misses += 1
        for d_idx in unmatched_det:
            det = detections[d_idx]
            track = Track(self._next_id, _new_kalman(det.bbox), deque(maxlen=self.vote_window), hits=1)
            track.bbox, track.score = det.bbox, det.score
            track.history.append((det.class_id, det.score))
            self.tracks.append(track)
            self._next_id += 1
        self.tracks = [t for t in self.tracks if t.misses <= self.max_age]
        return [self._output(t) for t in self.tracks if t.misses == 0 and t.hits >= self.min_hits]

    def _associate(self, detections: list[Detection], predicted: list[BBox]) -> tuple[list[tuple[int, int]], list[int]]:
        if not detections or not predicted:
            return [], list(range(len(detections)))
        iou = iou_matrix(np.array([d.bbox for d in detections]), np.array(predicted))
        rows, cols = linear_sum_assignment(-iou)
        matches = [(r, c) for r, c in zip(rows, cols) if iou[r, c] >= self.iou_threshold]
        matched = {r for r, _ in matches}
        return matches, [i for i in range(len(detections)) if i not in matched]

    @staticmethod
    def _output(track: Track) -> Detection:
        cls, score = track.voted_class()
        det = Detection(track.bbox, cls, score, track_id=track.track_id)
        if track.verified_score is not None:
            det = replace(det, score=track.verified_score, verified=track.verified)
        return replace(det, value=track.value, text=track.text, sub_sign=track.sub_sign)

    def get(self, track_id: int) -> Track | None:
        return next((t for t in self.tracks if t.track_id == track_id), None)
