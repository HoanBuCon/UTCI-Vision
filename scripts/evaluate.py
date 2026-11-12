"""Đánh giá toàn hệ thống — chạy local (FR-EVAL). Phụ trách: TV1 (E1, E2, E4), TV5 (benchmark).

    python scripts/evaluate.py detect --split test                  # E1
    python scripts/evaluate.py detect --split test --ablation       # E2: từng cấu hình trong ABLATIONS
    python scripts/evaluate.py detect --split test --degrade dark   # E4
    python scripts/evaluate.py benchmark --source video.mp4         # FPS/độ trễ từng khâu (local)
    python scripts/evaluate.py benchmark --yolo-only --source dataset/processed/v1/test  # mốc S1
    python scripts/evaluate.py benchmark --api --source video.mp4   # qua WebSocket (cổng UTCI_WEB_PORT)

    python scripts/evaluate.py flicker --source video.mp4           # E6: độ ổn định nhãn ± tracking (không cần nhãn)
    python scripts/evaluate.py small --split test                   # T3: biển nhỏ — imgsz 960 / 1280 / cắt ô

detect: Recognizer(video=False, cfg đã ablation) trên từng ảnh -> P / R / F1 tại điểm vận hành (chỉ số chính), recall
theo kích thước, mAP trên đầu ra pipeline (đã cắt ở ngưỡng hiển thị nên thấp hơn mAP của Ultralytics) -> reports/eval/,
registry. OCR tắt khi đo (không ảnh hưởng phát hiện).
TODO(TV5): benchmark toàn pipeline qua --api (WebSocket).
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator
from itertools import cycle, islice

import cv2
import numpy as np

from utci_vision.config import load_config, resolve
from utci_vision.data.labels import list_images, read_labels
from utci_vision.evaluation.experiments import ABLATIONS, DEGRADATIONS, apply_ablation, flicker_stats, measure_fps
from utci_vision.evaluation.metrics import evaluate_detections, iou_matrix
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


SIZE_BINS, SIZE_LABELS = [0, 16, 32, 64, np.inf], ["<16px", "16-32", "32-64", ">=64"]


def load_split(split: str, limit: int | None):
    root = resolve(load_config("data")["processed_dir"]) / split
    out = []
    for path in list_images(root)[:limit]:
        img = cv2.imread(str(path))
        h, w = img.shape[:2]
        gts = [(b.class_id, b.to_xyxy(w, h)) for b in read_labels(path.parent.parent / "labels" / f"{path.stem}.txt")]
        out.append((path, img, gts))
    return out


def operating_point(preds, gts_all) -> dict[str, float]:
    """P / R / F1 tại ngưỡng của pipeline (đúng lớp, IoU ≥ 0.5, ghép tham lam theo điểm) + recall theo kích thước."""
    tp = n_pred = n_gt = 0
    size_hit = {k: [0, 0] for k in SIZE_LABELS}
    for dets, gts in zip(preds, gts_all):
        n_pred += len(dets)
        n_gt += len(gts)
        used: set[int] = set()
        if dets and gts:
            iou = iou_matrix(np.array([d.bbox for d in dets]), np.array([b for _, b in gts]))
            for k in np.argsort([-d.score for d in dets]):
                cand = [
                    j for j, (c, _) in enumerate(gts) if j not in used and c == dets[k].class_id and iou[k, j] >= 0.5
                ]
                if cand:
                    used.add(max(cand, key=lambda j: iou[k, j]))
        tp += len(used)
        for j, (_, b) in enumerate(gts):
            side = float(np.sqrt((b[2] - b[0]) * (b[3] - b[1])))
            label = SIZE_LABELS[int(np.digitize(side, SIZE_BINS[1:-1]))]
            size_hit[label][0] += int(j in used)
            size_hit[label][1] += 1
    p, r = tp / max(n_pred, 1), tp / max(n_gt, 1)
    out = {"precision": p, "recall": r, "f1": 2 * p * r / max(p + r, 1e-9)}
    out |= {f"recall_{k}": v[0] / max(v[1], 1) for k, v in size_hit.items()}
    return out


def run_detect(args: argparse.Namespace) -> None:
    from utci_vision.config import load_classes
    from utci_vision.pipeline import Recognizer, load_components

    base = load_config("pipeline")
    base["ocr"]["enabled"] = False
    comps = load_components({**base, "verifier": {**base["verifier"], "enabled": True}})
    data = load_split(args.split, args.limit)
    if args.degrade:
        degrade = DEGRADATIONS[args.degrade]
        data = [(p, degrade(img), gts) for p, img, gts in data]
    configs = ABLATIONS if args.ablation else {"full": []}
    rows = []
    for name, disabled in configs.items():
        cfg = apply_ablation(base, disabled)
        if cfg["verifier"]["enabled"] and comps.verifier is None:
            print(f"[bỏ qua {name}] bộ xác minh chưa có trọng số ({comps.status['verifier']})")
            cfg["verifier"]["enabled"] = False
            if name == "+verifier":
                continue
        rec = Recognizer(cfg, comps, video=False)
        preds, ms = [], []
        for _, img, _ in data:
            r = rec.process(img)
            preds.append(r.detections)
            ms.append(r.latency_ms["total"])
        gts = [g for _, _, g in data]
        m = evaluate_detections(preds, gts, len(load_classes()))
        row = {
            "cau_hinh": name,
            **operating_point(preds, gts),
            "map50_dau_ra": m["map50"],
            "map50_95_dau_ra": m["map50_95"],
            "ms_tb": float(np.mean(ms)),
        }
        rows.append(row)
        print({k: round(v, 4) if isinstance(v, float) else v for k, v in row.items()}, flush=True)
    import pandas as pd

    table = pd.DataFrame(rows)
    exp = "E4" if args.degrade else ("E2" if args.ablation else "E1")
    out = resolve("reports/eval")
    out.mkdir(parents=True, exist_ok=True)
    tag = f"{exp}_{args.split}" + (f"_{args.degrade}" if args.degrade else "")
    table.to_csv(out / f"{tag}.csv", index=False)
    if args.limit:  # chạy thử: không ghi registry
        print(table.round(3).to_string(index=False))
        return
    run_id = log_run(
        exp,
        args.author,
        f"pipeline.yaml ({', '.join(configs)})",
        "v1",
        {"rows": table.round(4).to_dict("records")},
        notes=f"{args.split}{' degrade=' + args.degrade if args.degrade else ''}; P/R tại điểm vận hành",
    )
    print(table.round(3).to_string(index=False))
    print(f"-> {out / (tag + '.csv')} · registry {run_id}")


def run_flicker(args: argparse.Namespace) -> None:
    """E6: chạy video với tracking (nhãn bỏ phiếu theo track) và không tracking (track chỉ để ghép, nhãn theo frame)."""
    from utci_vision.pipeline import Recognizer, load_components
    from utci_vision.tracking import Tracker

    cfg = load_config("pipeline")
    cfg["ocr"]["enabled"] = False
    comps = load_components(cfg)
    cap = cv2.VideoCapture(str(resolve(args.source)))
    frames = []
    while len(frames) < args.frames and (ok := cap.read())[0]:
        frames.append(ok[1])
    cap.release()
    rec_on = Recognizer(cfg, comps, video=True)
    on = [[(d.track_id, d.class_id) for d in rec_on.process(f).detections] for f in frames]
    rec_on.close()
    t = cfg["tracking"]
    linker = Tracker(t["iou_threshold"], t["max_age"], 1, 1)  # cửa sổ bỏ phiếu 1 = nhãn theo từng frame
    cfg_off = apply_ablation(cfg, ["tracking.enabled"])
    rec_off = Recognizer(cfg_off, comps, video=True)
    off = [
        [(d.track_id, d.class_id) for d in linker.update(rec_off.process(f).detections, i)]
        for i, f in enumerate(frames)
    ]
    rows = {"co_tracking": flicker_stats(on), "khong_tracking": flicker_stats(off)}
    for k, v in rows.items():
        print(k, {a: round(b, 4) for a, b in v.items()})
    run_id = log_run("E6", args.author, "pipeline.yaml ± tracking", "video", rows, notes=f"nguồn {args.source}")
    print(f"registry {run_id}")


def run_small(args: argparse.Namespace) -> None:
    """T3: biển nhỏ không cần train lại — so imgsz 960, 1280 và cắt ô (ảnh đầy đủ + ô 640 ở độ phân giải gốc)."""
    import time

    import pandas as pd

    from utci_vision.detector import Detector
    from utci_vision.pipeline import resolve_device

    pipe = load_config("pipeline")
    d = pipe["detector"]
    data = load_split(args.split, args.limit)
    gts = [g for _, _, g in data]
    rows = []
    for name, imgsz, tiled in (("imgsz 960", 960, False), ("imgsz 1280", 1280, False), ("960 + cắt ô 640", 960, True)):
        det = Detector(d["weights"], imgsz, d["conf"], d["iou"], resolve_device(pipe.get("device")), d["half"])
        preds, t0 = [], time.perf_counter()
        for _, img, _ in data:
            preds.append(det.detect_tiled(img) if tiled else det.detect([img])[0])
        ms = (time.perf_counter() - t0) * 1000 / len(data)
        row = {"cau_hinh": name, **operating_point(preds, gts), "ms_anh": ms}
        rows.append(row)
        print({k: round(v, 4) if isinstance(v, float) else v for k, v in row.items()}, flush=True)
    table = pd.DataFrame(rows)
    out = resolve("reports/eval")
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / f"T3_{args.split}.csv", index=False)
    if args.limit:  # chạy thử: không ghi registry
        print(table.round(3).to_string(index=False))
        return
    run_id = log_run(
        "T3",
        args.author,
        "detector imgsz 960/1280/tiled",
        "v1",
        {"rows": table.round(4).to_dict("records")},
        notes=f"{args.split}; P/R @conf {d['conf']}; thiết bị {resolve_device(pipe.get('device'))}",
    )
    print(table.round(3).to_string(index=False))
    print(f"-> {out / f'T3_{args.split}.csv'} · registry {run_id}")


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
    flick = sub.add_parser("flicker")
    flick.add_argument("--source", required=True)
    flick.add_argument("--frames", type=int, default=3000)
    small = sub.add_parser("small")
    small.add_argument("--split", default="test")
    small.add_argument("--limit", type=int)
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
    if args.cmd in ("detect", "flicker", "small"):
        {"detect": run_detect, "flicker": run_flicker, "small": run_small}[args.cmd](args)
        return
    raise NotImplementedError("benchmark toàn pipeline / --api: chưa triển khai")


if __name__ == "__main__":
    main()
