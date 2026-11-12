"""Pipeline nhận diện thống nhất (ADR-001). Phụ trách: TV3 — S2 (khung), S3–S4 (đầy đủ).

    frame ─► enhance [CV] ─► detector [DL] ─► tracking [CV] ─► tác vụ theo track (nền):
                                                                 verifier [CV+ML] · ocr [CV+DL]

Mỗi khâu là một module cùng tên; bật/tắt bằng configs/pipeline.yaml (ablation E2). Tác vụ theo track chạy trong
ThreadPool, không chặn luồng frame (FR-PIPE-12); với ảnh tĩnh chạy đồng bộ.
Dùng chung cho API (ảnh / video / WebSocket), scripts/infer.py và scripts/evaluate.py.
"""

from __future__ import annotations

import os
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field, replace
from typing import Any

import numpy as np

from .config import load_classes, load_config, resolve
from .enhance import assess, enhance, needed_ops
from .structures import BBox, Detection

DISABLED = "tắt (cấu hình)"


@dataclass
class FrameResult:
    frame_idx: int
    detections: list[Detection]
    latency_ms: dict[str, float] = field(default_factory=dict)  # total, enhance, detector, tracking, tasks
    debug: dict[str, Any] = field(default_factory=dict)  # ảnh/mask trung gian (chế độ Giải thích)


@dataclass
class Components:
    """Mô hình nạp MỘT lần, dùng chung giữa mọi phiên; None = khâu tắt hoặc thiếu trọng số."""

    detector: Any = None  # detector.Detector
    verifier: Any = None  # verifier.Verifier
    reader: Any = None  # ocr.TextReader
    status: dict[str, str] = field(default_factory=dict)  # tên khâu -> "loaded" | lý do chưa nạp (cho /health)
    ocr_cfg: dict[str, Any] = field(default_factory=dict)
    lexicon: list[str] = field(default_factory=list)


def resolve_device(cfg_device: Any) -> str | int | None:
    """`auto` -> biến môi trường UTCI_DEVICE (Docker đặt sẵn) hoặc để Ultralytics tự chọn."""
    if cfg_device in (None, "auto"):
        env = os.environ.get("UTCI_DEVICE")
        if env:
            return int(env) if env.isdigit() else env
        try:
            import torch

            return 0 if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"
    return cfg_device


def load_components(cfg: dict[str, Any]) -> Components:
    """Nạp Detector / Verifier / TextReader theo cờ `enabled`; thiếu trọng số thì ghi vào `status`, không raise."""
    comps = Components()
    device = resolve_device(cfg.get("device"))
    d = cfg["detector"]
    weights = resolve(d["weights"])
    if not weights.exists():
        comps.status["detector"] = f"thiếu trọng số {d['weights']}"
    else:
        try:
            from .detector import Detector

            comps.detector = Detector(weights, d["imgsz"], d["conf"], d["iou"], device, d["half"])
            comps.status["detector"] = "loaded"
        except Exception as exc:  # noqa: BLE001 — báo qua /health thay vì làm sập API
            comps.status["detector"] = f"lỗi nạp: {exc}"

    v = cfg["verifier"]
    if not v["enabled"]:
        comps.status["verifier"] = DISABLED
    elif not resolve(v["weights"]).exists():
        comps.status["verifier"] = f"thiếu trọng số {v['weights']}"
    else:
        try:
            from .verifier import Verifier

            comps.verifier = Verifier(resolve(v["weights"]), v["threshold"])
            comps.status["verifier"] = "loaded"
        except Exception as exc:  # noqa: BLE001
            comps.status["verifier"] = f"lỗi nạp: {exc}"

    if not cfg["ocr"]["enabled"]:
        comps.status["ocr"] = DISABLED
    else:
        try:
            from .ocr import TextReader, load_lexicon

            comps.ocr_cfg = load_config("ocr")
            comps.lexicon = load_lexicon(comps.ocr_cfg["postprocess"]["lexicon"])
            comps.reader = TextReader(comps.ocr_cfg)
            comps.status["ocr"] = "loaded"
        except Exception as exc:  # noqa: BLE001
            comps.status["ocr"] = f"lỗi nạp: {exc}"
    return comps


def _context_region(image: np.ndarray, bbox: BBox) -> tuple[np.ndarray, BBox]:
    """Vùng quanh biển (kể cả phía dưới để tìm biển phụ) + bbox trong toạ độ vùng đó — lưu cho tác vụ nền."""
    h, w = image.shape[:2]
    x1, y1, x2, y2 = bbox
    bw, bh = x2 - x1, y2 - y1
    rx1, ry1 = int(max(0, x1 - 0.6 * bw)), int(max(0, y1 - 0.2 * bh))
    rx2, ry2 = int(min(w, x2 + 0.6 * bw)), int(min(h, y2 + 1.5 * bh))
    return image[ry1:ry2, rx1:rx2].copy(), (x1 - rx1, y1 - ry1, x2 - rx1, y2 - ry1)


class Recognizer:
    """Một instance cho mỗi nguồn: ảnh tĩnh (video=False) hoặc một luồng video/webcam (video=True)."""

    def __init__(self, cfg: dict[str, Any], components: Components, video: bool = False):
        from .tracking import Tracker

        self.cfg, self.components, self.video = cfg, components, video
        t = cfg["tracking"]
        self.tracker = (
            Tracker(t["iou_threshold"], t["max_age"], t["min_hits"], t["vote_window"])
            if video and t["enabled"]
            else None
        )
        self.executor = ThreadPoolExecutor(cfg["track_tasks"]["workers"]) if self.tracker is not None else None
        self.pending: dict[int, Future] = {}  # track_id -> tác vụ nền đang chạy
        self.frame_idx = 0
        self.classes = load_classes()

    # ------------------------------------------------------------ cờ bật/tắt
    @property
    def _verify_on(self) -> bool:
        return bool(self.cfg["verifier"]["enabled"] and self.components.verifier is not None)

    @property
    def _ocr_on(self) -> bool:
        return bool(
            self.cfg["ocr"]["enabled"] and self.components.reader is not None and self.cfg["track_tasks"]["ocr"]
        )

    # ------------------------------------------------------------ xử lý một frame
    def process(self, frame_bgr: np.ndarray, debug: bool = False) -> FrameResult:
        lat: dict[str, float] = {}
        dbg: dict[str, Any] = {}
        t0 = time.perf_counter()

        image, ops = frame_bgr, set()
        if self.cfg["quality"]["enabled"]:
            q = assess(frame_bgr, self.cfg["quality"]["downscale_width"])
            ops = needed_ops(q, self.cfg["quality"]) if self.cfg["enhance"]["enabled"] else set()
            if ops:
                image = enhance(frame_bgr, ops, self.cfg["enhance"])
            if debug:
                dbg["quality"] = {k: round(v, 4) for k, v in vars(q).items()}
        dbg["ops"] = sorted(ops)
        if debug and ops:
            dbg.setdefault("images", {})["enhanced"] = image
        lat["enhance"] = (time.perf_counter() - t0) * 1000

        t1 = time.perf_counter()
        detections: list[Detection] = []
        if self.components.detector is not None:
            conf = self.cfg["detector"]["proposal_conf"] if self._verify_on else self.cfg["detector"]["conf"]
            detections = self.components.detector.detect([image], conf=conf)[0]
        lat["detector"] = (time.perf_counter() - t1) * 1000

        t2 = time.perf_counter()
        if self.tracker is not None:
            detections = self._update_tracks(image, detections)
            lat["tracking"] = (time.perf_counter() - t2) * 1000
        else:
            detections = self._run_tasks_sync(image, detections, dbg if debug else None)
            lat["tasks"] = (time.perf_counter() - t2) * 1000

        lat["total"] = (time.perf_counter() - t0) * 1000
        result = FrameResult(self.frame_idx, detections, {k: round(v, 2) for k, v in lat.items()}, dbg if debug else {})
        self.frame_idx += 1
        return result

    # ------------------------------------------------------------ ảnh tĩnh: tác vụ đồng bộ
    def _run_tasks_sync(self, image: np.ndarray, dets: list[Detection], dbg: dict | None) -> list[Detection]:
        if self._verify_on:
            dets = [d for d in self.components.verifier.verify(image, dets) if d.verified]
        if not self._ocr_on:
            return dets
        from .ocr import read_sign

        out = []
        for i, d in enumerate(dets):
            info = self.classes[d.class_id]
            if not (info.has_value or info.has_text or self.components.ocr_cfg["sub_sign"]["enabled"]):
                out.append(d)
                continue
            value, text, sub, images = read_sign(
                image,
                d.bbox,
                info.has_value,
                info.value_unit,
                info.has_text,
                self.components.reader,
                self.components.ocr_cfg,
                self.components.lexicon,
            )
            if dbg is not None:
                for name, img in images.items():
                    dbg.setdefault("images", {})[f"{name}_{i}"] = img
            out.append(replace(d, value=value, text=text, sub_sign=sub))
        return out

    # ------------------------------------------------------------ video: tracking + tác vụ nền theo track
    def _update_tracks(self, image: np.ndarray, dets: list[Detection]) -> list[Detection]:
        from .ocr import frame_score

        confirmed = self.tracker.update(dets, self.frame_idx)
        refresh = self.cfg["track_tasks"]["refresh_every"]
        for det in confirmed:
            track = self.tracker.get(det.track_id)
            region, local_box = _context_region(image, det.bbox)
            x1, y1, x2, y2 = (int(v) for v in local_box)
            sign = region[max(0, y1) : y2, max(0, x1) : x2]
            if sign.size:
                score = frame_score(sign)
                if score >= track.best_crop_score:
                    track.best_crop, track.best_crop_score = (region, local_box), score
            due = track.last_task_frame < 0 or self.frame_idx - track.last_task_frame >= refresh
            busy = det.track_id in self.pending and not self.pending[det.track_id].done()
            if due and not busy and track.best_crop is not None and (self._verify_on or self._ocr_on):
                track.last_task_frame = self.frame_idx
                self.pending[det.track_id] = self.executor.submit(self._track_task, track, det.class_id)
        alive = {t.track_id for t in self.tracker.tracks}
        self.pending = {k: f for k, f in self.pending.items() if k in alive}
        # biển đã bị bộ xác minh bác bỏ thì không hiển thị
        return [d for d in confirmed if d.verified is not False]

    def _track_task(self, track, class_id: int) -> None:
        """Chạy nền: xác minh + đọc số/chữ trên crop tốt nhất; kết quả gắn vào track (bỏ phiếu qua nhiều lần)."""
        from .ocr import read_sign, vote

        region, box = track.best_crop
        det = Detection(box, class_id, track.score)
        if self._verify_on:
            v = self.components.verifier.verify(region, [det])[0]
            track.verified, track.verified_score = v.verified, v.score
        if self._ocr_on:
            info = self.classes[class_id]
            value, text, sub, _ = read_sign(
                region,
                box,
                info.has_value,
                info.value_unit,
                info.has_text,
                self.components.reader,
                self.components.ocr_cfg,
                self.components.lexicon,
            )
            for key, item in (("value", value), ("text", text), ("sub_sign", sub)):
                if item is not None:
                    track.readings[key].append(item)
                    setattr(track, key, vote(track.readings[key]))

    def close(self) -> None:
        if self.executor is not None:
            self.executor.shutdown(wait=False, cancel_futures=True)
