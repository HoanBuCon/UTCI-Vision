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
    def detect(self, images, conf=None):
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
