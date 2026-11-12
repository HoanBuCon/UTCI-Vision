"""Endpoint `/api/v1` (FR-API). Phụ trách: TV3."""

from __future__ import annotations

import asyncio
import base64
import copy
import time
import uuid
from typing import Annotated, Any

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse

from .. import __version__
from ..config import load_classes, load_config, load_yaml, resolve
from ..pipeline import DISABLED, FrameResult, Recognizer
from ..structures import Detection
from .schemas import (
    CandidateOut,
    ClassInfoOut,
    ComparePart,
    CompareResponse,
    CompareRow,
    DetectionOut,
    DetectResponse,
    HealthResponse,
    JobCreated,
    JobStatus,
    ModelStatus,
    SampleOut,
    SignTextOut,
    SignValueOut,
    TraditionalResponse,
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


# ---------------------------------------------------------------- đầu vào: upload hoặc ảnh mẫu, tuỳ chọn làm xấu


def _samples() -> dict[str, dict[str, Any]]:
    cfg = load_config("samples")
    root = resolve(cfg["images_dir"])
    return {s["id"]: {**s, "path": root / s["file"]} for s in cfg["samples"]}


@router.get("/samples", response_model=list[SampleOut])
def samples() -> list[SampleOut]:
    """Ảnh mẫu có sẵn trên máy chủ (configs/samples.yaml) — chỉ liệt kê ảnh thực sự tồn tại."""
    return [
        SampleOut(**{k: v for k, v in s.items() if k in SampleOut.model_fields})
        for s in _samples().values()
        if s["path"].exists()
    ]


@router.get("/samples/{sample_id}/image")
def sample_image(sample_id: str) -> FileResponse:
    s = _samples().get(sample_id)
    if s is None or not s["path"].exists():
        raise HTTPException(404, "Không có ảnh mẫu này")
    return FileResponse(s["path"], media_type="image/jpeg")


def _degrade(image: np.ndarray, degrade: str | None, level: float | None) -> np.ndarray:
    """Mô phỏng điều kiện xấu (trang Demo): dark = gamma (mặc định 2.5), noise = sigma (15), blur = kích thước nhân (9)."""
    from ..evaluation.experiments import darken, gaussian_noise, motion_blur

    if not degrade:
        return image
    if degrade == "dark":
        return darken(image, level or 2.5)
    if degrade == "noise":
        return gaussian_noise(image, level or 15)
    if degrade == "blur":
        k = int(level or 9)
        return motion_blur(image, k + (k + 1) % 2)
    raise HTTPException(400, f"degrade phải là dark | noise | blur, nhận '{degrade}'")


async def _load_input(request: Request, file: UploadFile | None, sample: str | None) -> np.ndarray:
    if sample:
        s = _samples().get(sample)
        if s is None or not s["path"].exists():
            raise HTTPException(404, f"Không có ảnh mẫu '{sample}'")
        return cv2.imread(str(s["path"]))
    if file is None:
        raise HTTPException(400, "Cần gửi file ảnh hoặc tham số sample")
    limit = request.app.state.api_cfg["limits"]["image_max_mb"] * 1024 * 1024
    if file.content_type not in IMAGE_TYPES:
        raise HTTPException(415, f"Định dạng {file.content_type} không hỗ trợ — dùng JPEG/PNG/BMP/WebP")
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, f"Ảnh vượt {limit // 1024 // 1024} MB")
    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(400, "Không giải mã được ảnh")
    return image


def _pipeline_cfg(
    request: Request, enhance: bool | None, verifier: bool | None, imgsz: int | None, tiled: bool, ocr: bool = True
) -> dict[str, Any]:
    """Cấu hình pipeline cho một request — ablation trực tiếp trên web (bật/tắt từng khâu)."""
    cfg = copy.deepcopy(request.app.state.pipeline_cfg)
    if enhance is not None:
        cfg["quality"]["enabled"] = cfg["enhance"]["enabled"] = enhance
    if verifier is not None:
        if verifier and request.app.state.components.verifier is None:
            raise HTTPException(409, "Bộ xác minh chưa có trọng số (scripts/fit_verifier.py)")
        cfg["verifier"]["enabled"] = verifier
    if imgsz is not None:
        if not 320 <= imgsz <= 1920:
            raise HTTPException(400, "imgsz phải trong khoảng 320–1920")
        cfg["detector"]["imgsz"] = imgsz
    cfg["detector"]["tiled"] = tiled
    if not ocr:
        cfg["ocr"]["enabled"] = False
    return cfg


@router.post("/detect/image", response_model=DetectResponse)
async def detect_image(
    request: Request,
    file: Annotated[UploadFile | None, File()] = None,
    sample: str | None = None,
    annotate: bool = True,
    debug: bool = False,
    return_input: bool = False,
    enhance: bool | None = None,
    verifier: bool | None = None,
    imgsz: int | None = None,
    tiled: bool = False,
    degrade: str | None = None,
    level: float | None = None,
) -> DetectResponse:
    """Ảnh upload hoặc ảnh mẫu -> (làm xấu) -> Recognizer(video=False) với cấu hình ghi đè -> DetectResponse."""
    _require_detector(request)
    image = _degrade(await _load_input(request, file, sample), degrade, level)
    cfg = _pipeline_cfg(request, enhance, verifier, imgsz, tiled)
    rec = Recognizer(cfg, request.app.state.components, video=False)
    result = await run_in_threadpool(rec.process, image, debug)
    resp = await run_in_threadpool(to_response, image, result, annotate, debug)
    if return_input:
        resp.input_image = _b64_jpeg(image)
    return resp


# ---------------------------------------------------------------- CV truyền thống & so sánh với học sâu


def _require_classic(request: Request) -> None:
    if request.app.state.components.classic is None:
        raise HTTPException(
            503, f"Chưa có bộ phân loại HOG + SVM: {request.app.state.components.status.get('classic')}"
        )


def _traditional(image: np.ndarray, comps, enhance: bool, details: bool) -> dict[str, Any]:
    """Chạy pipeline truyền thống: (tăng cường) -> màu + hình dạng -> HOG + màu + SVM."""
    from .. import traditional as tr
    from ..enhance import assess, needed_ops
    from ..enhance import enhance as do_enhance

    pipe = load_config("pipeline")
    t0 = time.perf_counter()
    q = assess(image, pipe["quality"]["downscale_width"])
    ops = needed_ops(q, pipe["quality"]) if enhance else set()
    work = do_enhance(image, ops, pipe["enhance"]) if ops else image
    t_enh = (time.perf_counter() - t0) * 1000
    ver = load_config("verifier")["features"]
    dets, cands, info = tr.detect(work, comps.classic, ver["color_ranges"], load_config("traditional")["detect"])
    classes = load_classes()
    background = len(classes)
    crops = [tr.padded_crop(work, c.bbox) for c in cands]
    cls, prob = comps.classic.predict([c for c in crops if c.size]) if cands else ([], [])
    # ảnh HOG / SIFT cho tối đa 8 ứng viên: ưu tiên vùng SVM nhận là biển, rồi tới vùng lớn
    shown = set(sorted(range(len(cands)), key=lambda i: (int(cls[i]) == background, i))[:8])
    out_cands = []
    for i, (c, k, p) in enumerate(zip(cands, cls, prob)):
        is_sign = int(k) != background
        item = CandidateOut(
            bbox=tuple(round(v, 1) for v in c.bbox),
            color=c.color,
            shape=c.shape,
            class_id=int(k) if is_sign else None,
            class_name=classes[int(k)].name_vi if is_sign else None,
            score=round(float(p), 3),
        )
        if details and i in shown and crops[i].size:
            sift_vis, n_kp = tr.sift_keypoints(crops[i])
            item.crop = _b64_jpeg(cv2.resize(crops[i], (128, 128), interpolation=cv2.INTER_CUBIC))
            item.hog_image = _b64_jpeg(tr.hog_image(crops[i], ver["hog"]))
            item.sift_image, item.sift_keypoints = _b64_jpeg(sift_vis), n_kp
        out_cands.append(item)
    dets = [d for d in dets if d.class_id != background]
    return {
        "work": work,
        "ops": sorted(ops),
        "quality": {k: round(v, 4) for k, v in vars(q).items()},
        "dets": dets,
        "cands": cands,
        "candidates": out_cands,
        "masks": info["masks"],
        "ms": {"enhance": round(t_enh, 2), **{k: round(v, 2) for k, v in info["ms"].items()}},
    }


@router.post("/traditional/analyze", response_model=TraditionalResponse)
async def traditional_analyze(
    request: Request,
    file: Annotated[UploadFile | None, File()] = None,
    sample: str | None = None,
    enhance: bool = True,
    degrade: str | None = None,
    level: float | None = None,
) -> TraditionalResponse:
    """Demo CV truyền thống: ảnh trung gian từng bước + vùng ứng viên + HOG / SIFT + lớp do SVM dự đoán."""
    from .. import traditional as tr
    from ..visualize import draw

    _require_classic(request)
    image = _degrade(await _load_input(request, file, sample), degrade, level)
    r = await run_in_threadpool(_traditional, image, request.app.state.components, enhance, True)
    images = {
        "input": _b64_jpeg(image),
        "masks": _b64_jpeg(tr.overlay_masks(r["work"], r["masks"])),
        "candidates": _b64_jpeg(tr.draw_candidates(r["work"], r["cands"])),
        "annotated": _b64_jpeg(draw(r["work"], r["dets"])),
    }
    if r["ops"]:
        images["enhanced"] = _b64_jpeg(r["work"])
    return TraditionalResponse(
        image_size=(image.shape[1], image.shape[0]),
        latency_ms=r["ms"],
        quality=r["quality"],
        ops=r["ops"],
        images=images,
        candidates=r["candidates"],
        detections=[to_out(d) for d in r["dets"]],
    )


def _compare(image: np.ndarray, request: Request, enhance: bool, imgsz: int | None) -> CompareResponse:
    from .. import traditional as tr
    from ..visualize import draw

    comps = request.app.state.components
    cfg = _pipeline_cfg(request, enhance, None, imgsz, False, ocr=False)
    deep = Recognizer(cfg, comps, video=False).process(image)
    trad = _traditional(image, comps, enhance, False)
    classes, background = load_classes(), len(load_classes())
    crops = [tr.padded_crop(image, d.bbox) for d in deep.detections]
    t0 = time.perf_counter()
    cls, prob = comps.classic.predict([c for c in crops if c.size]) if crops else ([], [])
    per_box_ms = (time.perf_counter() - t0) * 1000 / max(len(crops), 1)
    rows = []
    for d, k, p in zip(deep.detections, cls, prob):
        k = int(k)
        rows.append(
            CompareRow(
                bbox=tuple(round(v, 1) for v in d.bbox),
                side_px=round(float(np.sqrt((d.bbox[2] - d.bbox[0]) * (d.bbox[3] - d.bbox[1]))), 1),
                yolo_class_id=d.class_id,
                yolo_class_name=classes[d.class_id].name_vi,
                yolo_score=round(d.score, 3),
                classic_class_id=k if k != background else None,
                classic_class_name=classes[k].name_vi if k != background else None,
                classic_score=round(float(p), 3),
                agree=k == d.class_id,
            )
        )
    return CompareResponse(
        image_size=(image.shape[1], image.shape[0]),
        input_image=_b64_jpeg(image),
        deep=ComparePart(
            detections=[to_out(d) for d in deep.detections],
            latency_ms=deep.latency_ms,
            annotated_image=_b64_jpeg(draw(image, deep.detections)),
        ),
        traditional=ComparePart(
            detections=[to_out(d) for d in trad["dets"]],
            latency_ms=trad["ms"],
            annotated_image=_b64_jpeg(draw(trad["work"], trad["dets"])),
        ),
        per_box=rows,
        classic_ms_per_box=round(per_box_ms, 2),
    )


@router.post("/compare", response_model=CompareResponse)
async def compare(
    request: Request,
    file: Annotated[UploadFile | None, File()] = None,
    sample: str | None = None,
    enhance: bool = True,
    imgsz: int | None = None,
    degrade: str | None = None,
    level: float | None = None,
) -> CompareResponse:
    """Cùng một ảnh: hệ thống học sâu (YOLO11) và hệ thống truyền thống (màu + hình dạng + HOG + SVM), cộng với
    so sánh phân loại trên từng biển YOLO tìm thấy (YOLO vs HOG + màu + SVM)."""
    _require_detector(request)
    _require_classic(request)
    image = _degrade(await _load_input(request, file, sample), degrade, level)
    return await run_in_threadpool(_compare, image, request, enhance, imgsz)


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
