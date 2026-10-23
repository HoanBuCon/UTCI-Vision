"""Đánh giá toàn hệ thống — chạy local (FR-EVAL). Phụ trách: TV1 (E1, E2, E4), TV5 (benchmark).

    python scripts/evaluate.py detect --split test                  # E1
    python scripts/evaluate.py detect --split test --ablation       # E2: từng cấu hình trong ABLATIONS
    python scripts/evaluate.py detect --split test --degrade dark   # E4
    python scripts/evaluate.py benchmark --source video.mp4         # FPS/độ trễ từng khâu (local)
    python scripts/evaluate.py benchmark --api --source video.mp4   # qua WebSocket (cổng UTCI_WEB_PORT)

TODO(TV1, S3): detect -> Recognizer(video=False, cfg đã ablation).process từng ảnh -> metrics.evaluate_detections
               -> in bảng, xuất AP theo lớp/kích thước vào reports/eval/, registry.log_run(exp=E1|E2|E4).
TODO(TV5, S1): benchmark -> experiments.measure_fps + FrameResult.latency_ms; mốc S1 chỉ YOLO (--yolo-only).
"""

from __future__ import annotations

import argparse

from utci_vision.evaluation.experiments import ABLATIONS, DEGRADATIONS


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    det = sub.add_parser("detect")
    det.add_argument("--split", default="test")
    det.add_argument("--ablation", action="store_true", help=f"chạy {list(ABLATIONS)}")
    det.add_argument("--degrade", choices=list(DEGRADATIONS))
    det.add_argument("--limit", type=int)
    bench = sub.add_parser("benchmark")
    bench.add_argument("--source", required=True)
    bench.add_argument("--api", action="store_true")
    bench.add_argument("--yolo-only", action="store_true")
    bench.add_argument("--frames", type=int, default=300)
    parser.add_argument("--author", default="TV1")
    parser.parse_args()
    raise NotImplementedError("TODO — xem docstring")


if __name__ == "__main__":
    main()
