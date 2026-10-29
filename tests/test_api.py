"""utci_vision.api: endpoint đã chạy được và khung trả 501."""

from __future__ import annotations

import pytest

testclient = pytest.importorskip("fastapi.testclient")

from utci_vision.api.main import STAGES, create_app  # noqa: E402


@pytest.fixture
def client():
    with testclient.TestClient(create_app()) as c:
        yield c


def test_health_reports_every_stage(client):
    health = client.get("/api/v1/health").json()
    assert health["status"] in {"ok", "degraded"} and set(health["models"]) == set(STAGES)


def test_classes(client):
    classes = client.get("/api/v1/classes").json()
    assert len(classes) == 27 and classes[20]["value_unit"] == "km/h"
    assert classes[-1]["superclass"] == "other" and "raw_ids" not in classes[-1]


def test_skeleton_endpoints_return_501(client):
    assert client.post("/api/v1/detect/image", files={"file": ("a.jpg", b"x")}).status_code == 501
    assert client.get("/api/v1/jobs/abc").status_code == 501
