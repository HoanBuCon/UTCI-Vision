"""Nhập kết quả một lần fine-tune (thư mục <run_id>/ từ Local/Colab/Kaggle) (FR-TRAIN-08).

    python scripts/import_run.py <thư-mục-run> [--promote] [--exp E3] [--notes "..."]

- Copy trọng số + run_record.json vào models/<run_id>/; --promote: copy sang models/current/ (pipeline, Docker dùng).
- Ghi một dòng experiments/registry.csv với môi trường lấy từ run_record (không phải máy hiện tại).
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from utci_vision.config import resolve
from utci_vision.registry import log_run

ARTIFACTS = ("yolo11.pt", "verifier.joblib")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--promote", action="store_true")
    parser.add_argument("--exp", default="E1")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    record = json.loads((args.run_dir / "run_record.json").read_text(encoding="utf-8"))
    targets = [resolve("models") / record["run_id"]] + ([resolve("models") / "current"] if args.promote else [])
    for target in targets:
        target.mkdir(parents=True, exist_ok=True)
        for name in (*ARTIFACTS, "run_record.json"):
            if (args.run_dir / name).exists():
                shutil.copy2(args.run_dir / name, target / name)
    log_run(
        args.exp,
        record["author"],
        json.dumps(record["config"], ensure_ascii=False),
        record["dataset_version"],
        record["metrics"],
        notes=("SMOKE " if record["smoke"] else "") + args.notes,
        run_id=record["run_id"],
        environment=record["environment"],
        commit=record["commit"],
    )
    print(f"Đã nhập {record['run_id']} -> {', '.join(str(t) for t in targets)}")


if __name__ == "__main__":
    main()
