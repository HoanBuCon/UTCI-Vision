"""Quản lý job xử lý video chạy nền, không cần Redis/Celery (FR-API-04, ADR-003). Phụ trách: TV3 — S3."""

from __future__ import annotations

from pathlib import Path

from .schemas import JobStatus


class JobManager:
    """Lưu trạng thái job trong bộ nhớ; video kết quả ở outputs/<job_id>.mp4; dọn file quá outputs_ttl_hours."""

    def __init__(self, outputs_dir: Path, max_workers: int = 1):
        self.outputs_dir = outputs_dir
        self.jobs: dict[str, JobStatus] = {}

    def submit(self, video_path: Path) -> str:
        raise NotImplementedError("TODO(TV3, S3)")

    def status(self, job_id: str) -> JobStatus | None:
        raise NotImplementedError("TODO(TV3, S3)")

    def cleanup(self, ttl_hours: int) -> int:
        raise NotImplementedError("TODO(TV3, S3)")
