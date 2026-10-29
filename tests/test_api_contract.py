"""Hợp đồng API (chốt S1): trường của schema Pydantic phải khớp interface TypeScript của frontend."""

from __future__ import annotations

import re

import pytest

from utci_vision.api import schemas
from utci_vision.env import ROOT

TS_FILE = ROOT / "web" / "src" / "api" / "types.ts"
PAIRS = [  # (Pydantic, TypeScript)
    ("SignValueOut", "SignValue"),
    ("SignTextOut", "SignText"),
    ("DetectionOut", "Detection"),
    ("DetectResponse", "DetectResponse"),
    ("ModelStatus", "ModelStatus"),
    ("HealthResponse", "HealthResponse"),
    ("ClassInfoOut", "ClassInfo"),
    ("JobStatus", "JobStatus"),
]


def ts_fields(name: str) -> set[str]:
    match = re.search(rf"export interface {name} \{{(.*?)\n\}}", TS_FILE.read_text(encoding="utf-8"), re.S)
    assert match, f"Không thấy interface {name} trong types.ts"
    return set(re.findall(r"^\s+(\w+)\??:", match.group(1), re.M))


@pytest.mark.parametrize(("py_name", "ts_name"), PAIRS)
def test_schema_matches_typescript(py_name, ts_name):
    assert set(getattr(schemas, py_name).model_fields) == ts_fields(ts_name)
