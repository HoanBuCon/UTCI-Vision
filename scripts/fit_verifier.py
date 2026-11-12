"""Fit bộ xác minh đặc trưng thủ công + LightGBM trên dự đoán YOLO ở tập val (FR-TRAIN-05) — bản chạy local của bước
FIT_VERIFIER trong notebook. Phụ trách: TV1.

    python scripts/fit_verifier.py [<yolo11.pt>] [--out models/current]

Ghi <out>/verifier.joblib và in AUC out-of-fold của LightGBM / LogReg / RF so với riêng điểm YOLO.
Bộ xác minh mặc định tắt (configs/pipeline.yaml) — dùng cho ablation E2.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from utci_vision import verifier
from utci_vision.config import load_config, resolve


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("weights", type=Path, nargs="?", help="mặc định: configs/pipeline.yaml > detector.weights")
    parser.add_argument("--out", type=Path, default=Path("models/current"))
    args = parser.parse_args()
    weights = resolve(args.weights or load_config("pipeline")["detector"]["weights"])
    cfg = load_config("verifier")
    split_dir = resolve(load_config("data")["processed_dir"]) / cfg["build"]["split"]
    df = verifier.build_dataset(weights, split_dir, cfg)
    metrics = verifier.train(df, resolve(args.out), cfg)
    print(json.dumps({k: round(v, 4) for k, v in metrics.items()}, indent=2))
    print(f"-> {resolve(args.out) / 'verifier.joblib'}")


if __name__ == "__main__":
    main()
