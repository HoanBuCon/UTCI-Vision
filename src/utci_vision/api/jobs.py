"""Quản lý job xử lý video chạy nền, không cần Redis/Celery (FR-API-04, ADR-003). Phụ trách: TV3 — S3."""

from __future__ import annotations

import threading
import time
import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import cv2

from .schemas import JobStatus

# codec trình duyệt phát được trước; mp4v chỉ để tải về (trình duyệt thường không phát)
CODECS = (("avc1", ".mp4"), ("H264", ".mp4"), ("VP80", ".webm"), ("mp4v", ".mp4"))


def open_writer(stem: Path, fps: float, size: tuple[int, int]) -> tuple[cv2.VideoWriter, Path]:
    for fourcc, ext in CODECS:
        path = stem.with_suffix(ext)
        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*fourcc), fps, size)
        if writer.isOpened():
            return writer, path
        writer.release()
    raise RuntimeError("OpenCV không ghi được video với codec nào")


class JobManager:
    """Lưu trạng thái job trong bộ nhớ; video kết quả ở outputs/<job_id>.<mp4|webm>; dọn file quá outputs_ttl_hours.

    `make_recognizer()` trả một pipeline.Recognizer(video=True) mới cho mỗi job (mô hình dùng chung).
    """

    def __init__(self, outputs_dir: Path, make_recognizer: Callable[[], Any], max_seconds: float, max_workers: int = 1):
        self.outputs_dir = outputs_dir
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.make_recognizer, self.max_seconds = make_recognizer, max_seconds
        self.jobs: dict[str, JobStatus] = {}
        self.results: dict[str, Path] = {}
        self._lock = threading.Lock()
        self._pool = ThreadPoolExecutor(max_workers)

    def submit(self, video_path: Path) -> str:
        job_id = uuid.uuid4().hex[:12]
        self.jobs[job_id] = JobStatus(job_id=job_id, status="queued")
        self._pool.submit(self._run, job_id, video_path)
        return job_id

    def status(self, job_id: str) -> JobStatus | None:
        return self.jobs.get(job_id)

    def result_path(self, job_id: str) -> Path | None:
        return self.results.get(job_id)

    def _update(self, job_id: str, **kw) -> None:
        with self._lock:
            self.jobs[job_id] = self.jobs[job_id].model_copy(update=kw)

    def _run(self, job_id: str, video_path: Path) -> None:
        from ..config import load_classes
        from ..visualize import draw

        cap = cv2.VideoCapture(str(video_path))
        rec = None
        try:
            if not cap.isOpened():
                raise ValueError("Không đọc được video (định dạng không hỗ trợ)")
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
            if total and total / fps > self.max_seconds:
                raise ValueError(f"Video dài {total / fps:.0f} s, vượt giới hạn {self.max_seconds:.0f} s")
            w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            writer, out_path = open_writer(self.outputs_dir / job_id, fps, (w, h))
            rec = self.make_recognizer()
            classes = load_classes()
            seen: dict[int, dict[str, Any]] = {}
            self._update(job_id, status="running")
            i = 0
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                result = rec.process(frame)
                writer.write(draw(frame, result.detections))
                for d in result.detections:
                    info = seen.setdefault(
                        d.track_id if d.track_id is not None else -(i * 1000 + d.class_id),
                        {"class_id": d.class_id, "first_seen_s": round(i / fps, 2), "frames": 0},
                    )
                    info.update(class_id=d.class_id, class_name=classes[d.class_id].name_vi)
                    info["frames"] += 1
                    if d.value is not None:
                        info["value"] = f"{d.value.number:g} {d.value.unit}"
                    if d.text is not None:
                        info["text"] = d.text.text
                    if d.sub_sign is not None:
                        info["sub_sign"] = d.sub_sign.text
                i += 1
                if total and i % 10 == 0:
                    self._update(job_id, progress=round(min(i / total, 0.99), 3))
            writer.release()
            self.results[job_id] = out_path
            summary = sorted(seen.values(), key=lambda s: s["first_seen_s"])
            self._update(
                job_id, status="done", progress=1.0, result_video_url=f"/api/v1/jobs/{job_id}/video", summary=summary
            )
        except Exception as exc:  # noqa: BLE001 — báo lỗi qua trạng thái job
            self._update(job_id, status="failed", error=str(exc))
        finally:
            cap.release()
            if rec is not None:
                rec.close()
            video_path.unlink(missing_ok=True)

    def cleanup(self, ttl_hours: int) -> int:
        """Xoá file kết quả cũ hơn ttl; trả số file đã xoá."""
        cutoff, removed = time.time() - ttl_hours * 3600, 0
        for f in self.outputs_dir.glob("*"):
            if f.is_file() and f.stat().st_mtime < cutoff:
                f.unlink(missing_ok=True)
                removed += 1
        return removed
