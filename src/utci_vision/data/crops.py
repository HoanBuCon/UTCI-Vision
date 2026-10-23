"""Cắt crop các lớp có số/chữ để TV5 gán nhãn giá trị và chữ (FR-DATA-08/09).

Đầu ra: <out_dir>/<split>/<class_id>/<ảnh>_<i>.png, giữ kích thước gốc.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from .labels import label_path_for, list_images, read_labels


def padded_crop(image: np.ndarray, box: tuple[float, float, float, float], pad_ratio: float) -> np.ndarray:
    h, w = image.shape[:2]
    x1, y1, x2, y2 = box
    pw, ph = (x2 - x1) * pad_ratio, (y2 - y1) * pad_ratio
    return image[max(0, int(y1 - ph)) : min(h, int(y2 + ph)), max(0, int(x1 - pw)) : min(w, int(x2 + pw))]


def build_crops(split_dir: Path, out_dir: Path, classes: list[int], pad_ratio: float, min_side: int) -> dict[str, int]:
    stats = {"crops": 0, "skipped_small": 0}
    for img_path in list_images(split_dir):
        image = cv2.imread(str(img_path))
        if image is None:
            continue
        h, w = image.shape[:2]
        for i, b in enumerate(read_labels(label_path_for(img_path))):
            if b.class_id not in classes:
                continue
            x1, y1, x2, y2 = b.to_xyxy(w, h)
            if min(x2 - x1, y2 - y1) < min_side:
                stats["skipped_small"] += 1
                continue
            target = out_dir / str(b.class_id) / f"{img_path.stem}_{i}.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(target), padded_crop(image, (x1, y1, x2, y2), pad_ratio))
            stats["crops"] += 1
    return stats
