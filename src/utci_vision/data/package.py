"""Đóng gói processed/<version> thành zip + checksum để upload Google Drive / Kaggle (FR-DATA-05). Phụ trách: TV5 — S2.

Zip chứa data.yaml (đường dẫn tương đối), train/ val/ test/, manifest.csv và
VERSION.json = {"version", "manifest_sha256", "n_images", "created_at"}. Ngoài zip: <name>.sha256.
Kaggle tự giải nén khi upload -> notebook kiểm tra bằng VERSION.json (training.verify_extracted).
"""

from __future__ import annotations

from pathlib import Path


def package(processed_dir: Path, out_dir: Path, name: str, version: str) -> tuple[Path, Path]:
    """-> (zip, .sha256)."""
    raise NotImplementedError("TODO(TV5, S2)")
