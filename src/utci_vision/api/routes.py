"""Endpoint `/api/v1` (FR-API). Phụ trách: TV3."""

from __future__ import annotations

import asyncio
import base64
import uuid
from typing import Annotated, Any

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse

from .. import __version__
from ..config import load_classes, load_yaml
from ..pipeline import DISABLED, FrameResult, Recognizer
from ..structures import Detection
from .schemas import (
    ClassInfoOut,
    DetectionOut,
    DetectResponse,
    HealthResponse,
    JobCreated,
    JobStatus,
    ModelStatus,
    SignTextOut,
    SignValueOut,
)

router = APIRouter()
IMAGE_TYPES = {"image/jpeg", "image/png", "image/bmp", "image/webp"}
VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}


def _b64_jpeg(img: np.ndarray, quality: int = 85) -> str:
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode() if ok else ""


def to_out(d: Detection) -> DetectionOut:
    info = load_classes()[d.class_id]
    return DetectionOut(
        bbox=tuple(round(v, 1) for v in d.bbox),
        class_id=d.class_id,
        class_name=info.name_vi,
        superclass=info.superclass,
        score=round(d.score, 4),
        verified=d.verified,
        track_id=d.track_id,
        value=SignValueOut(number=d.value.number, unit=d.value.unit, confidence=round(d.value.confidence, 3))
        if d.value
        else None,
        text=SignTextOut(text=d.text.text, raw=d.text.raw, confidence=round(d.text.confidence, 3), parsed=d.text.parsed)
        if d.text
        else None,
        sub_sign=(
            SignTextOut(
                text=d.sub_sign.text,
                raw=d.sub_sign.raw,
                confidence=round(d.sub_sign.confidence, 3),
                parsed=d.sub_sign.parsed,
            )
            if d.sub_sign
            else None
        ),
    )


def to_response(image: np.ndarray, result: FrameResult, annotate: bool, debug: bool) -> DetectResponse:
    from ..visualize import draw

    dbg: dict[str, Any] | None = None
    if debug:
        dbg = {k: v for k, v in result.debug.items() if k != "images"}
        dbg["images"] = {k: _b64_jpeg(v) for k, v in result.debug.get("images", {}).items()}
    return DetectResponse(
        frame=result.frame_idx,
        image_size=(image.shape[1], image.shape[0]),
        latency_ms=result.latency_ms,
        detections=[to_out(d) for d in result.detections],
        annotated_image=_b64_jpeg(draw(image, result.detections)) if annotate else None,
        debug=dbg,
    )


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    status = request.app.state.components.status
    models = {
        name: ModelStatus(loaded=state == "loaded", detail=None if state == "loaded" else state)
        for name, state in status.items()
    }
    ok = all(m.loaded or m.detail == DISABLED for m in models.values())
    return HealthResponse(
        status="ok" if ok else "degraded", version=__version__, device=request.app.state.device, models=models
    )


@router.get("/classes", response_model=list[ClassInfoOut])
def classes() -> list[ClassInfoOut]:
    supers = load_yaml("configs/classes.yaml")["superclasses"]
    return [ClassInfoOut(**vars(c), superclass_vi=supers[c.superclass]["name_vi"]) for c in load_classes()]


def _require_detector(request: Request) -> None:
    if request.app.state.components.detector is None:
        raise HTTPException(
            503, f"Chưa nạp được mô hình phát hiện: {request.app.state.components.status.get('detector')}"
        )


@router.post("/detect/image", response_model=DetectResponse)
async def detect_image(
    request: Request, file: Annotated[UploadFile, File()], annotate: bool = True, debug: bool = False
) -> DetectResponse:
    """Kiểm tra định dạng/kích thước -> decode -> Recognizer(video=False).process -> DetectResponse."""
    _require_detector(request)
    limit = request.app.state.api_cfg["limits"]["image_max_mb"] * 1024 * 1024
    if file.content_type not in IMAGE_TYPES:
        raise HTTPException(415, f"Định dạng {file.content_type} không hỗ trợ — dùng JPEG/PNG/BMP/WebP")
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, f"Ảnh vượt {limit // 1024 // 1024} MB")
    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(400, "Không giải mã được ảnh")
    rec = Recognizer(request.app.state.pipeline_cfg, request.app.state.components, video=False)
    result = await run_in_threadpool(rec.process, image, debug)
    return await run_in_threadpool(to_response, image, result, annotate, debug)


@router.post("/jobs/video", response_model=JobCreated)
async def create_video_job(request: Request, file: Annotated[UploadFile, File()]) -> JobCreated:
    """Lưu video vào outputs/, giao jobs.JobManager xử lý nền."""
    _require_detector(request)
    jobs = request.app.state.jobs
    ext = "." + (file.filename or "video.mp4").rsplit(".", 1)[-1].lower()
    if ext not in VIDEO_EXTS:
        raise HTTPException(415, f"Định dạng {ext} không hỗ trợ — dùng {', '.join(sorted(VIDEO_EXTS))}")
    limit = request.app.state.api_cfg["limits"]["video_max_mb"] * 1024 * 1024
    path = jobs.outputs_dir / f"upload_{uuid.uuid4().hex[:8]}{ext}"
    size = 0
    with path.open("wb") as f:
        while chunk := await file.read(1 << 20):
            size += len(chunk)
            if size > limit:
                f.close()
                path.unlink(missing_ok=True)
                raise HTTPException(413, f"Video vượt {limit // 1024 // 1024} MB")
            f.write(chunk)
    jobs.cleanup(request.app.state.api_cfg["outputs_ttl_hours"])
    return JobCreated(job_id=jobs.submit(path))


@router.get("/jobs/{job_id}", response_model=JobStatus)
async def get_video_job(request: Request, job_id: str) -> JobStatus:
    status = request.app.state.jobs.status(job_id)
    if status is None:
        raise HTTPException(404, "Không có job này (có thể đã hết hạn)")
    return status


@router.get("/jobs/{job_id}/video")
async def get_job_video(request: Request, job_id: str, download: bool = False) -> FileResponse:
    path = request.app.state.jobs.result_path(job_id)
    if path is None or not path.exists():
        raise HTTPException(404, "Chưa có video kết quả")
    media = "video/webm" if path.suffix == ".webm" else "video/mp4"
    return FileResponse(path, media_type=media, filename=f"utci_{job_id}{path.suffix}" if download else None)


@router.websocket("/stream")
async def stream(websocket: WebSocket) -> None:
    """Webcam: client gửi JPEG (bytes) -> server trả DetectResponse (JSON). Back-pressure: client chỉ gửi frame
    tiếp theo khi nhận xong kết quả. Mỗi kết nối một Recognizer(video=True), dùng chung mô hình đã nạp."""
    await websocket.accept()
    app = websocket.app
    if app.state.components.detector is None:
        await websocket.send_json({"error": f"Chưa nạp được mô hình: {app.state.components.status.get('detector')}"})
        await websocket.close()
        return
    rec = Recognizer(app.state.pipeline_cfg, app.state.components, video=True)
    max_w = app.state.api_cfg["stream"]["max_width"]
    try:
        while True:
            data = await websocket.receive_bytes()
            frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                await websocket.send_json({"error": "Frame không hợp lệ"})
                continue
            if frame.shape[1] > max_w:
                frame = cv2.resize(
                    frame, (max_w, int(frame.shape[0] * max_w / frame.shape[1])), interpolation=cv2.INTER_AREA
                )
            result = await asyncio.to_thread(rec.process, frame)
            await websocket.send_json(to_response(frame, result, annotate=False, debug=False).model_dump())
    except WebSocketDisconnect:
        pass
    finally:
        rec.close()
