"""Đóng gói processed/<version> thành zip + checksum để upload Google Drive / Kaggle (FR-DATA-05). Phụ trách: TV5 (làm sớm ở S1 để smoke Colab/Kaggle).

Zip chứa data.yaml (đường dẫn tương đối), train/ val/ test/, manifest.csv và
VERSION.json = {"version", "manifest_sha256", "n_images", "created_at"}. Ngoài zip: <name>.sha256.
Kaggle tự giải nén khi upload -> notebook kiểm tra bằng VERSION.json (training.verify_extracted).
"""

from __future__ import annotations

import json
import zipfile
from datetime import datetime
from pathlib import Path

import yaml

from ..training import sha256_file

SPLITS = ("train", "val", "test")


def package(processed_dir: Path, out_dir: Path, name: str, version: str) -> tuple[Path, Path]:
    """-> (zip, .sha256). Ảnh đã nén sẵn nên lưu ZIP_STORED; bỏ *.cache do Ultralytics sinh ra."""
    manifest = processed_dir / "manifest.csv"
    data = yaml.safe_load((processed_dir / "data.yaml").read_text(encoding="utf-8"))
    data["path"] = "."  # notebook local có thể đã ghi đường dẫn tuyệt đối; gói luôn dùng đường dẫn tương đối
    files = sorted(f for s in SPLITS for f in (processed_dir / s).rglob("*") if f.is_file() and f.suffix != ".cache")
    meta = {
        "version": version,
        "manifest_sha256": sha256_file(manifest),
        "n_images": sum(f.parent.name == "images" for f in files),
        "created_at": f"{datetime.now():%Y-%m-%dT%H:%M:%S}",
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"{name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as zf:
        zf.writestr(f"{name}/data.yaml", yaml.safe_dump(data, allow_unicode=True, sort_keys=False))
        zf.writestr(f"{name}/VERSION.json", json.dumps(meta, ensure_ascii=False, indent=2))
        zf.write(manifest, f"{name}/manifest.csv")
        for f in files:
            zf.write(f, f"{name}/{f.relative_to(processed_dir).as_posix()}")
    sha_path = out_dir / f"{name}.sha256"
    sha_path.write_text(f"{sha256_file(zip_path)}  {zip_path.name}\n", encoding="utf-8")
    return zip_path, sha_path
