"""experiments/registry.csv — sổ ghi chính thức mọi lần fine-tune/đánh giá (FR-EVAL-08, NFR-REP-01).
Fine-tune (notebook) -> run_record.json -> scripts/import_run.py ghi dòng ở đây; đánh giá local ghi trực tiếp."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

from .env import ROOT, environment_summary, git_commit

REGISTRY = ROOT / "experiments" / "registry.csv"
FIELDS = [
    "run_id",
    "exp",
    "date",
    "author",
    "platform",
    "commit",
    "torch",
    "cuda",
    "gpu",
    "config",
    "dataset_version",
    "metrics_json",
    "notes",
]


def log_run(
    exp: str,
    author: str,
    config: str,
    dataset_version: str,
    metrics: dict,
    notes: str = "",
    run_id: str | None = None,
    environment: dict | None = None,
    commit: str | None = None,
    registry: Path = REGISTRY,
) -> str:
    env = environment or environment_summary()
    run_id = run_id or f"{exp}-{datetime.now():%Y%m%d-%H%M%S}"
    registry.parent.mkdir(parents=True, exist_ok=True)
    new_file = not registry.exists() or registry.stat().st_size == 0
    with registry.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(
            {
                "run_id": run_id,
                "exp": exp,
                "date": f"{datetime.now():%Y-%m-%d}",
                "author": author,
                "platform": env.get("platform"),
                "commit": commit or git_commit(),
                "torch": env.get("torch"),
                "cuda": env.get("cuda"),
                "gpu": env.get("gpu"),
                "config": config,
                "dataset_version": dataset_version,
                "metrics_json": json.dumps(metrics, ensure_ascii=False),
                "notes": notes,
            }
        )
    return run_id
