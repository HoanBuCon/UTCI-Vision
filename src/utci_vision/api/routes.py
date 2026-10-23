"""Endpoint `/api/v1` (FR-API). Phụ trách: TV3.

Đã chạy được: /health, /classes. Khung: /detect/image (S2), /jobs/video (S3), WS /stream (S4).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, WebSocket

from .. import __version__
from ..config import load_classes, load_yaml
from .schemas import ClassInfoOut, DetectResponse, HealthResponse, JobCreated, JobStatus, ModelStatus

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    status = request.app.state.components.status
    models = {
        name: ModelStatus(loaded=state == "loaded", detail=None if state == "loaded" else state)
        for name, state in status.items()
    }
    return HealthResponse(
        status="ok" if all(m.loaded for m in models.values()) else "degraded",
        version=__version__,
        device=request.app.state.device,
        models=models,
    )


@router.get("/classes", response_model=list[ClassInfoOut])
def classes() -> list[ClassInfoOut]:
    supers = load_yaml("configs/classes.yaml")["superclasses"]
    return [ClassInfoOut(**vars(c), superclass_vi=supers[c.superclass]["name_vi"]) for c in load_classes()]


@router.post("/detect/image", response_model=DetectResponse)
async def detect_image(
    request: Request, file: Annotated[UploadFile, File()], annotate: bool = True, debug: bool = False
) -> DetectResponse:
    """Kiểm tra định dạng/kích thước -> decode -> Recognizer(video=False).process -> DetectResponse."""
    raise HTTPException(501, "Chưa triển khai (Sprint 2)")


@router.post("/jobs/video", response_model=JobCreated)
async def create_video_job(request: Request, file: Annotated[UploadFile, File()]) -> JobCreated:
    """Lưu video vào outputs/, giao jobs.JobManager xử lý nền."""
    raise HTTPException(501, "Chưa triển khai (Sprint 3)")


@router.get("/jobs/{job_id}", response_model=JobStatus)
async def get_video_job(request: Request, job_id: str) -> JobStatus:
    raise HTTPException(501, "Chưa triển khai (Sprint 3)")


@router.websocket("/stream")
async def stream(websocket: WebSocket) -> None:
    """Webcam: client gửi JPEG (bytes) -> server trả DetectResponse (JSON). Back-pressure: client chỉ gửi frame
    tiếp theo khi nhận xong kết quả. Mỗi kết nối một Recognizer(video=True), dùng chung mô hình đã nạp."""
    await websocket.accept()
    await websocket.send_json({"error": "Chưa triển khai (Sprint 4)"})
    await websocket.close()
