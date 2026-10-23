"""Kiểm tra toàn vẹn & thống kê dataset YOLO (FR-DATA-01, FR-DATA-02).

Xuất `images.csv` (1 dòng/ảnh) và `boxes.csv` (1 dòng/box) để vẽ biểu đồ EDA trong notebook/báo cáo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from PIL import Image

from .labels import label_path_for, list_images, read_labels


@dataclass
class AuditIssues:
    corrupt_images: list[str] = field(default_factory=list)
    missing_labels: list[str] = field(default_factory=list)
    bad_lines: list[str] = field(default_factory=list)
    invalid_boxes: list[str] = field(default_factory=list)
    empty_labels: list[str] = field(default_factory=list)

    def summary(self) -> dict[str, int]:
        return {k: len(v) for k, v in self.__dict__.items()}


def audit_split(split_dir: Path, split: str, num_classes: int, tiny_area: float, issues: AuditIssues):
    image_rows, box_rows = [], []
    for img_path in list_images(split_dir):
        try:
            with Image.open(img_path) as im:
                im.verify()
            with Image.open(img_path) as im:
                width, height = im.size
        except Exception:  # noqa: BLE001 — mọi lỗi đọc ảnh đều tính là ảnh hỏng
            issues.corrupt_images.append(str(img_path))
            continue

        lbl_path = label_path_for(img_path)
        if not lbl_path.exists():
            issues.missing_labels.append(str(img_path))
        try:
            boxes = read_labels(lbl_path)
        except ValueError as err:
            issues.bad_lines.append(f"{lbl_path}: {err}")
            boxes = []
        if not boxes:
            issues.empty_labels.append(str(img_path))

        for b in boxes:
            if not b.is_valid(num_classes):
                issues.invalid_boxes.append(f"{lbl_path}: {b}")
            box_rows.append(
                {
                    "split": split,
                    "image": img_path.name,
                    "class_id": b.class_id,
                    "cx": b.cx,
                    "cy": b.cy,
                    "w": b.w,
                    "h": b.h,
                    "area": b.area,
                    "w_px": b.w * width,
                    "h_px": b.h * height,
                    "tiny": b.area < tiny_area,
                }
            )
        image_rows.append(
            {
                "split": split,
                "image": img_path.name,
                "path": str(img_path),
                "width": width,
                "height": height,
                "resolution": f"{width}x{height}",
                "n_boxes": len(boxes),
                "classes": " ".join(str(c) for c in sorted({b.class_id for b in boxes})),
            }
        )
    return image_rows, box_rows


def audit_dataset(raw_dir: str | Path, splits: list[str], num_classes: int, tiny_area: float = 0.0005):
    """Trả về (images_df, boxes_df, issues)."""
    raw_dir = Path(raw_dir)
    issues = AuditIssues()
    image_rows, box_rows = [], []
    for split in splits:
        imgs, boxes = audit_split(raw_dir / split, split, num_classes, tiny_area, issues)
        image_rows += imgs
        box_rows += boxes
    return pd.DataFrame(image_rows), pd.DataFrame(box_rows), issues


def class_distribution(boxes_df: pd.DataFrame, class_names: list[str]) -> pd.DataFrame:
    table = boxes_df.pivot_table(index="class_id", columns="split", values="image", aggfunc="count", fill_value=0)
    table["total"] = table.sum(axis=1)
    table.insert(0, "name", [class_names[i] for i in table.index])
    return table.sort_values("total", ascending=False)
