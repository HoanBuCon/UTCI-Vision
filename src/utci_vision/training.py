"""Tiện ích dùng chung cho 3 notebook fine-tune (ADR-006): định vị + kiểm tra dữ liệu, ghi run_record.json.

Cấu trúc một lần chạy:  <out_root>/<run_id>/{yolo11.pt, verifier.joblib, yolo/, run_record.json}
"""

from __future__ import annotations

import hashlib
import json
import time
import zipfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from .env import environment_summary, git_commit

# ---------------------------------------------------------------- dữ liệu


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def verify_checksum(zip_path: Path, sha_path: Path) -> str:
    """So SHA-256 của zip với file .sha256 (Colab tải zip từ Drive)."""
    expected = sha_path.read_text(encoding="utf-8").split()[0].strip()
    if (actual := sha256_file(zip_path)) != expected:
        raise ValueError(f"Checksum không khớp: {zip_path.name}\n  mong đợi {expected}\n  thực tế  {actual}")
    return actual


def verify_extracted(dataset_dir: Path) -> str:
    """Kiểm tra dữ liệu đã giải nén (Kaggle tự giải nén zip): SHA-256 của manifest.csv so với VERSION.json."""
    version = json.loads((dataset_dir / "VERSION.json").read_text(encoding="utf-8"))
    if (actual := sha256_file(dataset_dir / "manifest.csv")) != version["manifest_sha256"]:
        raise ValueError(f"manifest.csv không khớp phiên bản {version.get('version')}: dữ liệu bị thiếu/sai")
    return actual


def find_dataset_dir(root: Path) -> Path:
    return next(root.rglob("data.yaml")).parent


def extract_dataset(zip_path: Path, dest: Path) -> Path:
    """Giải nén (bỏ qua nếu đã có) và trả thư mục chứa data.yaml."""
    if not any(dest.rglob("data.yaml")):
        dest.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(dest)
    return find_dataset_dir(dest)


def write_data_yaml(dataset_dir: Path) -> Path:
    """Ghi `path` tuyệt đối của máy hiện tại vào data.yaml (gói dữ liệu dùng đường dẫn tương đối)."""
    path = dataset_dir / "data.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["path"] = str(dataset_dir.resolve())
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


# ---------------------------------------------------------------- run record


def new_run_id(model: str, imgsz: int, smoke: bool = False) -> str:
    return f"{datetime.now():%Y%m%d-%H%M}_{Path(model).stem}_{imgsz}{'_smoke' if smoke else ''}"


@dataclass
class RunRecord:
    run_id: str
    author: str
    dataset_version: str
    dataset_sha256: str | None = None
    config: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)  # {"yolo": ..., "verifier": ...}
    artifacts: list[str] = field(default_factory=list)
    smoke: bool = False
    commit: str = field(default_factory=git_commit)
    environment: dict[str, Any] = field(default_factory=environment_summary)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    duration_s: float = 0.0
    _t0: float = field(default_factory=time.perf_counter, repr=False)

    def save(self, run_dir: Path) -> Path:
        self.duration_s = round(time.perf_counter() - self._t0, 1)
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / "run_record.json"
        data = {k: v for k, v in asdict(self).items() if not k.startswith("_")}
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path
