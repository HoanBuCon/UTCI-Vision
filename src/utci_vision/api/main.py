"""FastAPI app factory (FR-API, ADR-003). Phụ trách: TV3. Chạy: `python -m utci_vision.api [--reload]` (cổng UTCI_API_PORT)."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .. import __version__
from ..config import load_config, resolve
from ..env import Ports
from ..pipeline import Components, Recognizer, load_components, resolve_device
from .jobs import JobManager
from .routes import router

STAGES = ("detector", "verifier", "ocr")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Nạp cấu hình + mô hình MỘT lần, dùng chung cho mọi request/phiên (FR-API-07).

    UTCI_SKIP_MODELS=1 bỏ qua nạp mô hình (test API / CI không có trọng số).
    """
    app.state.pipeline_cfg = load_config("pipeline")
    app.state.api_cfg = load_config("api")
    app.state.device = str(resolve_device(app.state.pipeline_cfg.get("device")))
    if os.environ.get("UTCI_SKIP_MODELS") == "1":
        app.state.components = Components(status={s: "bỏ qua (UTCI_SKIP_MODELS)" for s in STAGES})
    else:
        app.state.components = load_components(app.state.pipeline_cfg)
    app.state.jobs = JobManager(
        resolve(app.state.api_cfg["outputs_dir"]),
        lambda: Recognizer(app.state.pipeline_cfg, app.state.components, video=True),
        app.state.api_cfg["limits"]["video_max_seconds"],
    )
    yield


def create_app() -> FastAPI:
    ports = Ports.from_env()
    app = FastAPI(title="UTCI-VISION API", version=__version__, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[f"http://localhost:{ports.dev}", f"http://localhost:{ports.web}"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()
