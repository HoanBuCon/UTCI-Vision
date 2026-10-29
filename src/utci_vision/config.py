"""Đọc cấu hình YAML (`configs/`) và danh sách lớp biển báo của mô hình (+ ánh xạ từ lớp gốc của dataset)."""

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
    raw_ids: tuple[int, ...] = ()  # id lớp trong dataset gốc (Roboflow) được gộp vào lớp này


@lru_cache(maxsize=1)
def load_classes() -> tuple[ClassInfo, ...]:
    classes = tuple(
        ClassInfo(**{**c, "raw_ids": tuple(c.get("raw_ids", ()))})
        for c in load_yaml(CONFIG_DIR / "classes.yaml")["classes"]
    )
    assert [c.id for c in classes] == list(range(len(classes))), "id lớp phải liên tục từ 0"
    return classes


def raw_class_map(classes: tuple[ClassInfo, ...] | None = None) -> dict[int, int]:
    """id lớp gốc -> id lớp mô hình. Mỗi id gốc 0..N-1 phải thuộc đúng một lớp."""
    mapping: dict[int, int] = {}
    for c in classes or load_classes():
        for raw in c.raw_ids:
            assert raw not in mapping, f"id gốc {raw} được gán cho 2 lớp"
            mapping[raw] = c.id
    assert sorted(mapping) == list(range(len(mapping))), "raw_ids phải phủ kín 0..N-1"
    return mapping
