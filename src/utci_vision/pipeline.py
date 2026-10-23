"""Pipeline nhận diện thống nhất (ADR-001). Phụ trách: TV3 — S2 (khung), S3–S4 (đầy đủ).

    frame ─► enhance [CV] ─► detector [DL] ─► tracking [CV] ─► tác vụ theo track (nền):
                                                                 verifier [CV+ML] · ocr [CV+DL]

Mỗi khâu là một module cùng tên; bật/tắt bằng configs/pipeline.yaml (ablation E2). Tác vụ theo track chạy trong
ThreadPool, không chặn luồng frame (FR-PIPE-12); với ảnh tĩnh chạy đồng bộ.
Dùng chung cho API (ảnh / video / WebSocket), scripts/infer.py và scripts/evaluate.py.
"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .structures import Detection


@dataclass
class FrameResult:
    frame_idx: int
    detections: list[Detection]
    latency_ms: dict[str, float] = field(default_factory=dict)  # total, enhance, detector, tracking
    debug: dict[str, Any] = field(default_factory=dict)  # ảnh/mask trung gian (chế độ Giải thích)


@dataclass
class Components:
    """Mô hình nạp MỘT lần, dùng chung giữa mọi phiên; None = khâu tắt hoặc thiếu trọng số."""

    detector: Any = None  # detector.Detector
    verifier: Any = None  # verifier.Verifier
    reader: Any = None  # ocr.TextReader
    status: dict[str, str] = field(default_factory=dict)  # tên khâu -> "loaded" | lý do chưa nạp (cho /health)


def load_components(cfg: dict[str, Any]) -> Components:
    """Nạp Detector / Verifier / TextReader theo cờ `enabled`; thiếu trọng số thì ghi vào `status`, không raise."""
    raise NotImplementedError("TODO(TV3, S2)")


class Recognizer:
    """Một instance cho mỗi nguồn: ảnh tĩnh (video=False) hoặc một luồng video/webcam (video=True)."""

    def __init__(self, cfg: dict[str, Any], components: Components, video: bool = False):
        self.cfg, self.components, self.video = cfg, components, video
        self.tracker = None  # TODO(TV3, S3): tracking.Tracker nếu video và tracking.enabled
        self.executor = ThreadPoolExecutor(cfg["track_tasks"]["workers"]) if video else None
        self.pending: dict[int, Future] = {}  # track_id -> tác vụ nền đang chạy
        self.frame_idx = 0

    def process(self, frame_bgr: np.ndarray, debug: bool = False) -> FrameResult:
        raise NotImplementedError("TODO(TV3, S2)")

    def close(self) -> None:
        if self.executor is not None:
            self.executor.shutdown(wait=False, cancel_futures=True)
