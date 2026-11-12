"""Suy luận nhanh không qua web: ảnh / thư mục ảnh / video -> ảnh, video đã vẽ + JSON. Phụ trách: TV3 — S2.

    python scripts/infer.py --source <ảnh | thư mục | video> [--out outputs/infer] [--debug] [--no-ocr]

Ảnh: Recognizer(video=False) -> <out>/<tên>.jpg + <tên>.json (+ ảnh trung gian khi --debug).
Video: Recognizer(video=True) (tracking + tác vụ nền) -> <out>/<tên>.mp4 + <tên>.json (kết quả từng frame).
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import cv2

from utci_vision.config import load_config, resolve
from utci_vision.data.labels import IMG_EXTS
from utci_vision.pipeline import Recognizer, load_components
from utci_vision.visualize import draw

VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}


def _det_json(result) -> dict:
    return {
        "frame": result.frame_idx,
        "latency_ms": result.latency_ms,
        "detections": [asdict(d) for d in result.detections],
    }


def run_images(paths: list[Path], cfg: dict, comps, out: Path, debug: bool) -> None:
    rec = Recognizer(cfg, comps, video=False)
    for path in paths:
        img = cv2.imread(str(path))
        if img is None:
            print(f"bỏ qua {path} (không đọc được)")
            continue
        r = rec.process(img, debug=debug)
        cv2.imwrite(str(out / f"{path.stem}.jpg"), draw(img, r.detections))
        (out / f"{path.stem}.json").write_text(json.dumps(_det_json(r), ensure_ascii=False, indent=2), encoding="utf-8")
        for name, im in r.debug.get("images", {}).items():
            cv2.imwrite(str(out / f"{path.stem}__{name}.jpg"), im)
        print(f"{path.name}: {len(r.detections)} biển · {r.latency_ms['total']:.0f} ms")


def run_video(path: Path, cfg: dict, comps, out: Path) -> None:
    from utci_vision.api.jobs import open_writer

    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    writer, out_path = open_writer(out / path.stem, fps, size)
    rec, frames = Recognizer(cfg, comps, video=True), []
    while (ok := cap.read())[0]:
        r = rec.process(ok[1])
        writer.write(draw(ok[1], r.detections))
        frames.append(_det_json(r))
    cap.release()
    writer.release()
    rec.close()
    (out / f"{path.stem}.json").write_text(json.dumps(frames, ensure_ascii=False), encoding="utf-8")
    print(f"{path.name}: {len(frames)} frame -> {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True)
    parser.add_argument("--out", default="outputs/infer")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--no-ocr", action="store_true", help="tắt đọc số / chữ (nhanh hơn)")
    args = parser.parse_args()

    cfg = load_config("pipeline")
    if args.no_ocr:
        cfg["ocr"]["enabled"] = False
    comps = load_components(cfg)
    if comps.detector is None:
        raise SystemExit(f"Chưa nạp được mô hình phát hiện: {comps.status['detector']}")
    source, out = resolve(args.source), resolve(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        images = sorted(p for p in source.rglob("*") if p.suffix.lower() in IMG_EXTS)
        run_images(images, cfg, comps, out, args.debug)
    elif source.suffix.lower() in VIDEO_EXTS:
        run_video(source, cfg, comps, out)
    else:
        run_images([source], cfg, comps, out, args.debug)
    print(f"-> {out}")


if __name__ == "__main__":
    main()
