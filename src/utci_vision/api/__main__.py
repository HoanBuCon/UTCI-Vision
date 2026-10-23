"""`python -m utci_vision.api [--reload]` — chạy API trên UTCI_API_HOST:UTCI_API_PORT (từ .env, không dùng cổng mặc định)."""

from __future__ import annotations

import argparse
import os

import uvicorn

from ..env import Ports

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()
    ports = Ports.from_env()
    uvicorn.run(
        "utci_vision.api.main:app",
        host=os.environ.get("UTCI_API_HOST", "127.0.0.1"),
        port=ports.api,
        reload=args.reload,
    )
