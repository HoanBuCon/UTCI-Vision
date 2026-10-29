"""Công cụ dữ liệu chạy local (FR-DATA). Phụ trách: TV5.

python scripts/data.py audit [--dedup]   # kiểm tra + thống kê + gom ảnh gần trùng -> reports/data/
python scripts/data.py split [--dry-run] # chia lại -> dataset/processed/v1 (cần audit --dedup trước)
python scripts/data.py crops             # cắt crop lớp có số/chữ để gán nhãn
python scripts/data.py package           # zip + checksum để upload Google Drive / Kaggle
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from utci_vision.config import load_classes, load_config, load_yaml, raw_class_map, resolve
from utci_vision.data import audit, crops, dedup, package, split


def cmd_audit(cfg: dict, args: argparse.Namespace) -> None:
    """Audit chạy trên dữ liệu gốc nên dùng id/tên lớp gốc (data.yaml của Roboflow), chưa gộp lớp."""
    raw_names = load_yaml(resolve(cfg["raw_dir"]) / "data.yaml")["names"]
    assert len(raw_names) == len(raw_class_map()), "classes.yaml > raw_ids không khớp số lớp của dataset gốc"
    out = resolve(cfg["reports_dir"])
    out.mkdir(parents=True, exist_ok=True)
    images, boxes, issues = audit.audit_dataset(
        resolve(cfg["raw_dir"]), cfg["raw_splits"], len(raw_names), cfg["audit"]["tiny_box_area"]
    )
    dist = audit.class_distribution(boxes, raw_names)
    if args.dedup:
        d = cfg["dedup"]
        hashes = dedup.compute_hashes([Path(p) for p in images["path"]], d["hash"], d["hash_size"])
        images["dup_cluster"] = dedup.cluster_near_duplicates(hashes, d["max_hamming"])
        sizes = images.groupby("dup_cluster")["image"].transform("count")
        leaks = (images.groupby("dup_cluster")["split"].nunique() > 1).sum()
        print(f"Ảnh trong cụm gần trùng: {(sizes > 1).sum()} | cụm vắt qua nhiều tập: {leaks}")
    images.to_csv(out / "images.csv", index=False)
    boxes.to_csv(out / "boxes.csv", index=False)
    dist.to_csv(out / "class_distribution.csv", encoding="utf-8-sig")
    (out / "issues.json").write_text(json.dumps(issues.__dict__, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Vấn đề:", issues.summary())
    print(pd.crosstab(images["resolution"], images["split"]))
    print(f"Box rất nhỏ: {int(boxes['tiny'].sum())}/{len(boxes)}\n{dist.to_string()}\n-> {out}")


def cmd_split(cfg: dict, args: argparse.Namespace) -> None:
    classes = load_classes()
    reports = resolve(cfg["reports_dir"])
    images = pd.read_csv(reports / "images.csv")
    if "dup_cluster" not in images:
        raise SystemExit("Thiếu cột dup_cluster — chạy `python scripts/data.py audit --dedup` trước.")
    excluded = split.read_exclusions([resolve(p) for p in cfg["split"].get("exclude_lists", [])])
    before = len(images)
    images = images[~images["image"].isin(excluded)].reset_index(drop=True)
    print(f"Loại {before - len(images)} ảnh theo {len(cfg['split'].get('exclude_lists', []))} danh sách")
    class_map = raw_class_map(classes)  # boxes.csv mang id gốc -> chia theo lớp của mô hình (sau gộp)
    boxes = pd.read_csv(reports / "boxes.csv").assign(class_id=lambda b: b["class_id"].map(class_map))
    images["class_counts"] = split.stratification_vectors(images, boxes, len(classes))
    images["raw_classes"] = images["classes"]
    images["classes"] = (
        images["raw_classes"]
        .fillna("")
        .astype(str)
        .map(lambda ids: " ".join(str(i) for i in sorted({class_map[int(r)] for r in ids.split()})))
    )
    dims = len(images["class_counts"].iloc[0])
    images["new_split"] = split.grouped_stratified_split(images, dims, cfg["split"]["ratios"], seed=cfg["seed"])
    report = split.split_report(images, "new_split", "class_counts")
    report.index = [c.name_vi for c in classes] + [f"[nguồn] {r}" for r in sorted(images["resolution"].unique())]
    print(report.to_string(), images["new_split"].value_counts(), sep="\n")
    if not args.dry_run:
        out = split.materialize(
            images, "new_split", resolve(cfg["processed_dir"]), [c.name for c in classes], class_map
        )
        report.to_csv(out / "split_report.csv", encoding="utf-8-sig")
        print(f"-> {out}")


def cmd_crops(cfg: dict, args: argparse.Namespace) -> None:
    c = cfg["crops"]
    for name in ("train", "val", "test"):
        stats = crops.build_crops(
            resolve(cfg["processed_dir"]) / name,
            resolve(c["out_dir"]) / name,
            c["classes"],
            c["pad_ratio"],
            c["min_side_px"],
        )
        print(name, stats)


def cmd_package(cfg: dict, args: argparse.Namespace) -> None:
    p = cfg["package"]
    print(*package.package(resolve(cfg["processed_dir"]), resolve(p["out_dir"]), p["name"], cfg["version"]), sep="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("audit").add_argument("--dedup", action="store_true")
    sub.add_parser("split").add_argument("--dry-run", action="store_true")
    sub.add_parser("crops")
    sub.add_parser("package")
    args = parser.parse_args()
    {"audit": cmd_audit, "split": cmd_split, "crops": cmd_crops, "package": cmd_package}[args.cmd](
        load_config("data"), args
    )


if __name__ == "__main__":
    main()
