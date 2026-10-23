"""Đọc cấu hình YAML (`configs/`) và thông tin 32 lớp biển báo."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .env import ROOT

CONFIG_DIR = ROOT / "configs"


def resolve(path: str | Path) -> Path:
    """Đường dẫn tương đối được tính từ thư mục gốc dự án."""
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def load_yaml(path: str | Path) -> dict[str, Any]:
    with resolve(path).open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config(name: str) -> dict[str, Any]:
    """`load_config("pipeline")` -> configs/pipeline.yaml."""
    return load_yaml(CONFIG_DIR / f"{name}.yaml")


@dataclass(frozen=True)
class ClassInfo:
    id: int
    name: str
    name_vi: str
    superclass: str
    qcvn: str = ""
    meaning: str = ""
    has_value: bool = False
    value_unit: str | None = None
    has_text: bool = False


@lru_cache(maxsize=1)
def load_classes() -> tuple[ClassInfo, ...]:
    classes = tuple(ClassInfo(**c) for c in load_yaml(CONFIG_DIR / "classes.yaml")["classes"])
    assert [c.id for c in classes] == list(range(len(classes))), "id lớp phải liên tục từ 0"
    return classes
