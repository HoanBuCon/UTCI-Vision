"""Schema JSON của API (SRS §5.1). Đây là "hợp đồng" giữa backend (TV3) và frontend (TV2) — chốt ở Sprint 1.
Đồng bộ thủ công với web/src/api/types.ts.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ModelStatus(BaseModel):
    loaded: bool
    path: str | None = None
    detail: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    version: str
    device: str
    models: dict[str, ModelStatus]  # detector, verifier, ocr


class ClassInfoOut(BaseModel):
    id: int
    name_vi: str
    superclass: str
    superclass_vi: str
    qcvn: str = ""
    meaning: str = ""
    has_value: bool = False
    value_unit: str | None = None
    has_text: bool = False


class SignValueOut(BaseModel):
    number: float
    unit: str
    confidence: float


class SignTextOut(BaseModel):
    text: str
    raw: str
    confidence: float
    parsed: dict[str, Any] = Field(default_factory=dict)


class DetectionOut(BaseModel):
    bbox: tuple[float, float, float, float]  # x1, y1, x2, y2 theo pixel ảnh gốc
    class_id: int
    class_name: str
    superclass: str
    score: float
    verified: bool | None = None
    track_id: int | None = None
    value: SignValueOut | None = None
    text: SignTextOut | None = None
    sub_sign: SignTextOut | None = None


class DetectResponse(BaseModel):
    frame: int = 0
    image_size: tuple[int, int]  # (width, height)
    latency_ms: dict[str, float] = Field(default_factory=dict)
    detections: list[DetectionOut]
    annotated_image: str | None = None  # base64 JPEG khi annotate=true
    debug: dict[str, Any] | None = None  # ảnh trung gian (base64) khi debug=true
    input_image: str | None = None  # ảnh đầu vào thực tế (ảnh mẫu / đã làm xấu) khi return_input=true


class JobCreated(BaseModel):
    job_id: str


class JobStatus(BaseModel):
    job_id: str
    status: Literal["queued", "running", "done", "failed"]
    progress: float = 0.0  # 0..1
    result_video_url: str | None = None
    summary: list[dict[str, Any]] = Field(default_factory=list)  # biển đã xuất hiện: lớp, số lần, thời điểm đầu
    error: str | None = None


class SampleOut(BaseModel):
    id: str
    title: str
    group: str
    signs: int
    small: int
    size: str


class CandidateOut(BaseModel):
    """Vùng ứng viên của pipeline CV truyền thống (màu + hình dạng) và kết quả HOG + màu + SVM."""

    bbox: tuple[float, float, float, float]
    color: str  # red | blue | yellow
    shape: str  # tròn | tam giác | chữ nhật
    class_id: int | None = None  # None = SVM xếp vào lớp "nền"
    class_name: str | None = None
    score: float | None = None
    crop: str | None = None  # base64 JPEG
    hog_image: str | None = None
    sift_image: str | None = None
    sift_keypoints: int | None = None


class TraditionalResponse(BaseModel):
    image_size: tuple[int, int]
    latency_ms: dict[str, float] = Field(default_factory=dict)
    quality: dict[str, float] = Field(default_factory=dict)
    ops: list[str] = Field(default_factory=list)
    images: dict[str, str] = Field(default_factory=dict)  # input, enhanced, masks, candidates, annotated
    candidates: list[CandidateOut]
    detections: list[DetectionOut]


class CompareRow(BaseModel):
    """Một biển YOLO tìm thấy: lớp YOLO so với lớp HOG + màu + SVM trên cùng vùng ảnh."""

    bbox: tuple[float, float, float, float]
    side_px: float
    yolo_class_id: int
    yolo_class_name: str
    yolo_score: float
    classic_class_id: int | None
    classic_class_name: str | None
    classic_score: float | None
    agree: bool


class ComparePart(BaseModel):
    detections: list[DetectionOut]
    latency_ms: dict[str, float] = Field(default_factory=dict)
    annotated_image: str | None = None


class CompareResponse(BaseModel):
    image_size: tuple[int, int]
    input_image: str | None = None
    deep: ComparePart
    traditional: ComparePart
    per_box: list[CompareRow]
    classic_ms_per_box: float
