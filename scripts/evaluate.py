"""Đánh giá toàn hệ thống — chạy local (FR-EVAL). Phụ trách: TV1 (E1, E2, E4), TV5 (benchmark).

    python scripts/evaluate.py detect --split test                  # E1
    python scripts/evaluate.py detect --split test --ablation       # E2: từng cấu hình trong ABLATIONS
    python scripts/evaluate.py detect --split test --degrade dark   # E4
    python scripts/evaluate.py benchmark --source video.mp4         # FPS/độ trễ từng khâu (local)
    python scripts/evaluate.py benchmark --yolo-only --source dataset/processed/v1/test  # mốc S1
    python scripts/evaluate.py benchmark --api --source video.mp4   # qua WebSocket (cổng UTCI_WEB_PORT)

TODO(TV1, S3): detect -> Recognizer(video=False, cfg đã ablation).process từng ảnh -> metrics.evaluate_detections
               -> in bảng, xuất AP theo lớp/kích thước vào reports/eval/, registry.log_run(exp=E1|E2|E4).
TODO(TV5, S3): benchmark toàn pipeline -> Recognizer + FrameResult.latency_ms từng khâu; --api qua WebSocket.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator
from itertools import cycle, islice

import cv2
import numpy as np

from utci_vision.config import load_config, resolve
from utci_vision.data.labels import list_images
from utci_vision.evaluation.experiments import ABLATIONS, DEGRADATIONS, measure_fps
from utci_vision.registry import log_run


def read_frames(source: str, n: int) -> Iterator[np.ndarray]:
    """n frame từ video (lặp lại nếu ngắn) hoặc từ thư mục ảnh (lặp vòng) — đã nạp sẵn vào RAM để không đo I/O."""
    path = resolve(source)
    if path.is_dir():
        frames = [cv2.imread(str(p)) for p in islice(list_images(path), n)]  # thư mục split (chứa images/)
    else:
        cap, frames = cv2.VideoCapture(str(path)), []
        while len(frames) < n and (ok := cap.read())[0]:
            frames.append(ok[1])
        cap.release()
    if not frames:
        raise SystemExit(f"Không đọc được frame nào từ {path}")
    return islice(cycle(frames), n)


def benchmark_yolo(args: argparse.Namespace) -> None:
    from utci_vision.detector import Detector

    cfg = load_config("pipeline")["detector"]
    weights = args.weights or cfg["weights"]
    imgsz = args.imgsz or cfg["imgsz"]
    det = Detector(weights, imgsz, cfg["conf"], cfg["iou"], args.device, cfg["half"])
    stats = measure_fps(lambda f: det.detect([f]), read_frames(args.source, args.frames))
    stats |= {"imgsz": imgsz, "weights": str(weights), "half": det.half}
    print({k: round(v, 2) if isinstance(v, float) else v for k, v in stats.items()})
    run_id = log_run(
        "BENCH-YOLO",
        args.author,
        f"pipeline.yaml>detector imgsz={imgsz}",
        args.dataset,
        stats,
        notes=f"YOLO-only, batch 1, nguồn {args.source}",
    )
    print(f"Đã ghi experiments/registry.csv: {run_id}")


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
    bench.add_argument("--weights", help="mặc định pipeline.yaml > detector.weights")
    bench.add_argument("--imgsz", type=int, help="mặc định pipeline.yaml > detector.imgsz")
    bench.add_argument("--device", help="vd. 0 hoặc cpu (mặc định: tự chọn)")
    bench.add_argument("--dataset", default="v1", help="phiên bản dữ liệu ghi vào registry")
    parser.add_argument("--author", default="TV1")
    args = parser.parse_args()
    if args.cmd == "benchmark" and args.yolo_only and not args.api:
        benchmark_yolo(args)
        return
    raise NotImplementedError("TODO — xem docstring")


if __name__ == "__main__":
    main()
