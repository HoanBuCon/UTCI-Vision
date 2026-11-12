"""utci_vision.api: health, classes, ảnh, job video, WebSocket — với detector giả (không cần trọng số)."""

from __future__ import annotations

import time

import cv2
import numpy as np
import pytest

testclient = pytest.importorskip("fastapi.testclient")

from utci_vision.api.main import STAGES, create_app  # noqa: E402
from utci_vision.pipeline import Components  # noqa: E402
from utci_vision.structures import Detection  # noqa: E402


class FakeDetector:
    def detect(self, images, conf=None, imgsz=None):
        return [[Detection((20, 20, 60, 60), 20, 0.9)] for _ in images]


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("UTCI_SKIP_MODELS", "1")
    with testclient.TestClient(create_app()) as c:
        c.app.state.jobs.outputs_dir = tmp_path
        yield c


@pytest.fixture
def ready(client):
    """API với detector giả, tắt OCR / xác minh."""
    cfg = client.app.state.pipeline_cfg
    cfg["ocr"]["enabled"] = cfg["verifier"]["enabled"] = False
    client.app.state.components = Components(detector=FakeDetector(), status={s: "loaded" for s in STAGES})
    return client


def _jpeg(h: int = 120, w: int = 160) -> bytes:
    return cv2.imencode(".jpg", np.full((h, w, 3), 128, np.uint8))[1].tobytes()


def test_health_reports_every_stage(client):
    health = client.get("/api/v1/health").json()
    assert health["status"] == "degraded" and set(health["models"]) == set(STAGES)


def test_classes(client):
    classes = client.get("/api/v1/classes").json()
    assert len(classes) == 27 and classes[20]["value_unit"] == "km/h"
    assert classes[-1]["superclass"] == "other" and "raw_ids" not in classes[-1]


def test_detect_without_model_is_503_and_rejects_bad_type(client, ready):
    client.app.state.components = Components(status={"detector": "thiếu trọng số"})
    assert client.post("/api/v1/detect/image", files={"file": ("a.jpg", _jpeg(), "image/jpeg")}).status_code == 503
    ready.app.state.components = Components(detector=FakeDetector(), status={})
    assert ready.post("/api/v1/detect/image", files={"file": ("a.txt", b"x", "text/plain")}).status_code == 415
    assert (
        ready.post("/api/v1/detect/image", files={"file": ("a.jpg", b"not-an-image", "image/jpeg")}).status_code == 400
    )


def test_detect_image_returns_detections_annotation_and_debug(ready):
    r = ready.post("/api/v1/detect/image?debug=true", files={"file": ("a.jpg", _jpeg(), "image/jpeg")})
    body = r.json()
    assert r.status_code == 200 and body["image_size"] == [160, 120]
    det = body["detections"][0]
    assert det["class_name"] == "Giới hạn tốc độ" and det["superclass"] == "prohibitory"
    assert body["annotated_image"].startswith("data:image/jpeg;base64,") and "ops" in body["debug"]


def test_video_job_end_to_end(ready, tmp_path):
    src = tmp_path / "in.mp4"
    writer = cv2.VideoWriter(str(src), cv2.VideoWriter_fourcc(*"mp4v"), 10, (160, 120))
    for _ in range(12):
        writer.write(np.full((120, 160, 3), 128, np.uint8))
    writer.release()
    job = ready.post("/api/v1/jobs/video", files={"file": ("in.mp4", src.read_bytes(), "video/mp4")}).json()["job_id"]
    for _ in range(100):
        status = ready.get(f"/api/v1/jobs/{job}").json()
        if status["status"] in ("done", "failed"):
            break
        time.sleep(0.1)
    assert status["status"] == "done", status
    assert status["summary"][0]["class_name"] == "Giới hạn tốc độ" and status["summary"][0]["frames"] >= 9
    assert ready.get(status["result_video_url"]).status_code == 200
    assert ready.get("/api/v1/jobs/khong-co").status_code == 404
    assert ready.post("/api/v1/jobs/video", files={"file": ("a.exe", b"x", "video/mp4")}).status_code == 415


def test_websocket_stream_tracks_frames(ready):
    with ready.websocket_connect("/api/v1/stream") as ws:
        replies = []
        for _ in range(4):
            ws.send_bytes(_jpeg())
            replies.append(ws.receive_json())
    assert replies[0]["detections"] == [] and replies[3]["detections"][0]["track_id"] == 1
    assert replies[3]["frame"] == 3 and replies[3]["annotated_image"] is None


# ---------------------------------------------------------------- ảnh mẫu, ghi đè cấu hình, CV truyền thống, so sánh


class RecordingDetector(FakeDetector):
    def __init__(self):
        self.imgsz = []

    def detect(self, images, conf=None, imgsz=None):
        self.imgsz.append(imgsz)
        return super().detect(images, conf, imgsz)


class FakeClassic:
    """Bộ phân loại HOG + SVM giả: mọi vùng là lớp 20 (Giới hạn tốc độ), xác suất 0.8."""

    def predict(self, crops):
        return np.full(len(crops), 20), np.full(len(crops), 0.8)


def _sign_image() -> np.ndarray:
    img = np.full((200, 240, 3), 90, np.uint8)
    cv2.circle(img, (60, 60), 30, (30, 30, 220), 6)  # viền đỏ (BGR) -> ứng viên "tròn"
    return img


@pytest.fixture
def sample(monkeypatch, tmp_path):
    from utci_vision.api import routes

    path = tmp_path / "s.jpg"
    cv2.imwrite(str(path), _sign_image())
    meta = {"id": "s1", "file": "s.jpg", "title": "Mẫu", "group": "Nhóm", "signs": 1, "small": 0, "size": "240x200"}
    monkeypatch.setattr(routes, "_samples", lambda: {"s1": {**meta, "path": path}})
    return "s1"


def test_samples_list_image_and_detect_with_overrides(ready, sample):
    assert ready.get("/api/v1/samples").json()[0]["id"] == sample
    assert ready.get(f"/api/v1/samples/{sample}/image").headers["content-type"] == "image/jpeg"
    assert ready.get("/api/v1/samples/khong_co/image").status_code == 404
    det = RecordingDetector()
    ready.app.state.components.detector = det
    r = ready.post(f"/api/v1/detect/image?sample={sample}&imgsz=960&return_input=true&degrade=dark&level=3")
    assert r.status_code == 200 and r.json()["input_image"].startswith("data:image/jpeg")
    assert det.imgsz[-1] == 960
    assert ready.post(f"/api/v1/detect/image?sample={sample}&imgsz=99").status_code == 400
    assert ready.post(f"/api/v1/detect/image?sample={sample}&degrade=fog").status_code == 400
    assert ready.post(f"/api/v1/detect/image?sample={sample}&verifier=true").status_code == 409  # chưa có trọng số
    assert ready.post("/api/v1/detect/image").status_code == 400  # thiếu cả file lẫn sample


def test_traditional_analyze(ready, sample):
    assert ready.post(f"/api/v1/traditional/analyze?sample={sample}").status_code == 503  # chưa có HOG + SVM
    ready.app.state.components.classic = FakeClassic()
    body = ready.post(f"/api/v1/traditional/analyze?sample={sample}").json()
    assert {"input", "masks", "candidates", "annotated"} <= set(body["images"])
    cand = body["candidates"][0]
    assert cand["color"] == "red" and cand["shape"] == "tròn" and cand["class_name"] == "Giới hạn tốc độ"
    assert cand["hog_image"].startswith("data:image/jpeg") and cand["sift_keypoints"] is not None
    assert body["detections"][0]["class_id"] == 20 and "segment" in body["latency_ms"]


def test_compare_yolo_vs_classic_per_box(ready, sample):
    ready.app.state.components.classic = FakeClassic()
    body = ready.post(f"/api/v1/compare?sample={sample}&imgsz=1280").json()
    assert body["deep"]["detections"][0]["class_id"] == 20 and body["traditional"]["annotated_image"]
    row = body["per_box"][0]
    assert row["agree"] and row["classic_class_name"] == row["yolo_class_name"] == "Giới hạn tốc độ"
    assert row["side_px"] == 40.0
