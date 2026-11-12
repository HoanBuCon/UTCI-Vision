"""Xuất dữ liệu tĩnh cho web (trang Dữ liệu, Kết quả, So sánh, Dashboard) -> web/public/data/*.json. Phụ trách: TV2.

    python scripts/export_web_data.py

Nguồn (chạy local, đều có thể tái tạo): dataset/processed/v1 + reports/data (EDA), docs/danh_gia/*.csv và reports/*
(đánh giá), runs_out/<run_id>/yolo/results.csv (đường cong huấn luyện), experiments/registry.csv. Đầu ra nhỏ (vài chục KB)
và được commit để web hiển thị cả khi không có dataset / API đang nạp mô hình. Thiếu nguồn nào thì bỏ qua mục đó.
"""

from __future__ import annotations

import csv
import json
import re
from typing import Any

import numpy as np
import pandas as pd

from utci_vision.config import load_classes, load_config, load_yaml, resolve

OUT = resolve("web/public/data")
SIZE_BINS = [0, 8, 16, 24, 32, 48, 64, 96, 128, 1e9]
SIZE_LABELS = ["<8", "8–16", "16–24", "24–32", "32–48", "48–64", "64–96", "96–128", "≥128"]


def _r(x: Any, n: int = 4) -> Any:
    if isinstance(x, float):
        return None if np.isnan(x) else round(x, n)
    if isinstance(x, dict):
        return {k: _r(v, n) for k, v in x.items()}
    if isinstance(x, list):
        return [_r(v, n) for v in x]
    return x


def _records(df: pd.DataFrame) -> list[dict]:
    return _r(json.loads(df.to_json(orient="records", force_ascii=False)))


def _csv(path: str) -> pd.DataFrame | None:
    p = resolve(path)
    return pd.read_csv(p) if p.exists() else None


def eda() -> dict:
    from PIL import Image

    from utci_vision.data.labels import list_images, read_labels

    classes = load_classes()
    supers = load_yaml("configs/classes.yaml")["superclasses"]
    v1 = resolve(load_config("data")["processed_dir"])
    boxes, per_image = [], []
    for split in ("train", "val", "test"):
        for p in list_images(v1 / split):
            w, h = Image.open(p).size
            labels = read_labels(p.parent.parent / "labels" / f"{p.stem}.txt")
            per_image.append({"split": split, "n": len(labels), "res": f"{w}x{h}"})
            for b in labels:
                boxes.append(
                    {
                        "split": split,
                        "cls": b.class_id,
                        "side": float(np.sqrt(b.w * w * b.h * h)),
                        "cx": b.cx,
                        "cy": b.cy,
                    }
                )
    b, im = pd.DataFrame(boxes), pd.DataFrame(per_image)
    manifest = pd.read_csv(v1 / "manifest.csv", dtype={"classes": str})
    manifest["cl"] = manifest["classes"].fillna("").map(lambda s: [int(x) for x in re.findall(r"\d+", s)])
    exploded = manifest.explode("cl").dropna(subset=["cl"]).astype({"cl": int})
    clusters = exploded.groupby("cl").dup_cluster.nunique()
    per_class = []
    for c in classes:
        g = b[b.cls == c.id]
        per_class.append(
            {
                "id": c.id,
                "name": c.name_vi,
                "superclass": c.superclass,
                "qcvn": c.qcvn,
                "train": int((g.split == "train").sum()),
                "val": int((g.split == "val").sum()),
                "test": int((g.split == "test").sum()),
                "total": len(g),
                "clusters": int(clusters.get(c.id, 0)),
                "median_px": float(g.side.median()) if len(g) else 0.0,
                "pct_lt16": float((g.side < 16).mean() * 100) if len(g) else 0.0,
                "raw_ids": list(c.raw_ids),
            }
        )
    hist = pd.cut(b.side, SIZE_BINS, labels=SIZE_LABELS, right=False).value_counts().reindex(SIZE_LABELS).fillna(0)
    heat, _, _ = np.histogram2d(b.cy, b.cx, bins=[12, 20], range=[[0, 1], [0, 1]])
    raw = (
        load_yaml(resolve(load_config("data")["raw_dir"]) / "data.yaml")["names"]
        if (resolve(load_config("data")["raw_dir"]) / "data.yaml").exists()
        else []
    )
    other = next(c for c in classes if c.superclass == "other")
    issues = (
        json.loads(resolve("reports/data/issues.json").read_text(encoding="utf-8"))
        if resolve("reports/data/issues.json").exists()
        else {}
    )
    audit = {k: len(v) if isinstance(v, list) else v for k, v in issues.items()}  # chỉ số lượng, không lộ đường dẫn máy
    return _r(
        {
            "totals": {
                "images": len(im),
                "boxes": len(b),
                "classes": len(classes),
                "raw_classes": len(raw) or 32,
                "background_images": int((im.n == 0).sum()),
                "clusters": int(manifest.dup_cluster.nunique()),
                "median_side_px": float(b.side.median()),
                "pct_lt16": float((b.side < 16).mean() * 100),
                "pct_lt32": float((b.side < 32).mean() * 100),
                "imbalance": float(max(r["total"] for r in per_class) / min(r["total"] for r in per_class)),
                "excluded_images": 67,
            },
            "splits": {
                s: {"images": int((im.split == s).sum()), "boxes": int((b.split == s).sum())}
                for s in ("train", "val", "test")
            },
            "per_class": per_class,
            "superclasses": [
                {"key": k, "name": v["name_vi"], "boxes": int(b.cls.map(lambda i: classes[i].superclass).eq(k).sum())}
                for k, v in supers.items()
            ],
            "size_hist": [{"bin": k, "boxes": int(v)} for k, v in hist.items()],
            "resolutions": [{"res": k, "images": int(v)} for k, v in im.res.value_counts().items()],
            "signs_per_image": [
                {"n": int(k), "images": int(v)} for k, v in im.n.clip(upper=10).value_counts().sort_index().items()
            ],
            "position_heatmap": heat.astype(int).tolist(),
            "merged": {
                "into": other.name_vi,
                "raw_ids": list(other.raw_ids),
                "raw_names": [raw[i] for i in other.raw_ids] if raw else [],
            },
            "audit": audit,
        }
    )


def results() -> dict:
    run_dir = resolve("models/current")
    record = (
        json.loads((run_dir / "run_record.json").read_text(encoding="utf-8"))
        if (run_dir / "run_record.json").exists()
        else {}
    )
    out: dict[str, Any] = {
        "model": {
            k: record.get(k)
            for k in (
                "run_id",
                "author",
                "dataset_version",
                "started_at",
                "duration_s",
                "config",
                "environment",
                "metrics",
            )
        }
    }
    curves = resolve(f"runs_out/{record.get('run_id')}/yolo/results.csv")
    if curves.exists():
        d = pd.read_csv(curves)
        d.columns = [c.strip() for c in d.columns]
        keep = {
            "epoch": "epoch",
            "train/box_loss": "train_box",
            "train/cls_loss": "train_cls",
            "val/box_loss": "val_box",
            "val/cls_loss": "val_cls",
            "metrics/precision(B)": "precision",
            "metrics/recall(B)": "recall",
            "metrics/mAP50(B)": "map50",
            "metrics/mAP50-95(B)": "map50_95",
        }
        out["training"] = _records(d[list(keep)].rename(columns=keep))
    tables = {
        "bootstrap": "docs/danh_gia/S1_baseline_yolo11s_960/bootstrap_test.csv",
        "per_class": "docs/danh_gia/S1_baseline_yolo11s_960/class_review.csv",
        "per_class_ap": "docs/danh_gia/S1_baseline_yolo11s_960/ultralytics_val.csv",
        "similarity": "docs/danh_gia/S1_baseline_yolo11s_960/similarity.csv",
        "e1": "docs/danh_gia/S3_he_thong/E1_mac_dinh_1280.csv",
        "e2": "docs/danh_gia/S3_he_thong/E2_ablation_960.csv",
        "e4_ablation": "docs/danh_gia/S3_he_thong/E4_toi_ablation_960.csv",
        "t3": "docs/danh_gia/S3_he_thong/T3_bien_nho.csv",
        "e8": "reports/e8/e8_by_size.csv",
        "e8_paired": "reports/e8/e8_paired_delta.csv",
        "t4": "reports/t4/t4_enhance.csv",
        "t1": "reports/feasibility/t1_feature_sets.csv",
    }
    for key, path in tables.items():
        d = _csv(path)
        if d is not None:
            out[key] = _records(d.rename(columns={"Unnamed: 0": "id"}))
    out["sift_keypoints"] = [  # đo 29/10 trên 2 017 crop test (scripts trong lịch sử phiên; xem 04_BAO_CAO §6.3)
        {"size": "<16px", "median": 1, "pct_lt5": 93},
        {"size": "16-32", "median": 8, "pct_lt5": 25},
        {"size": "32-64", "median": 23, "pct_lt5": 11},
        {"size": ">=64", "median": 74, "pct_lt5": 2},
    ]
    out["benchmarks"] = {
        "gpu_detector_ms_1280": 22.5,
        "docker_cpu_image_s": [0.9, 1.6],
        "ws_cpu_fps": 9.3,
        "ws_docker_cpu_fps": 3.5,
    }
    reg = resolve("experiments/registry.csv")
    if reg.exists():
        rows = list(csv.DictReader(reg.open(encoding="utf-8")))
        out["registry"] = [
            {k: r[k] for k in ("run_id", "exp", "date", "author", "platform", "gpu", "dataset_version", "notes")}
            for r in rows
        ]
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("eda", eda), ("results", results)):
        try:
            data = fn()
        except FileNotFoundError as exc:
            print(f"bỏ qua {name}: thiếu {exc}")
            continue
        path = OUT / f"{name}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"-> {path} ({path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
