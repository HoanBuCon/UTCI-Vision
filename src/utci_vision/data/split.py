"""Chia lại train/val/test theo nhóm, cân bằng phân bố lớp (FR-DATA-04).

Mỗi "nhóm" = một cụm ảnh gần trùng (xem dedup.py) và luôn nằm trọn trong một tập.
Thuật toán tham lam (iterative stratification): duyệt nhóm từ hiếm đến phổ biến, gán vào tập đang thiếu
nhiều nhất (so với tỉ lệ mục tiêu) đối với lớp hiếm nhất mà nhóm đó chứa.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def grouped_stratified_split(
    images: pd.DataFrame,
    num_classes: int,
    ratios: dict[str, float],
    group_col: str = "dup_cluster",
    classes_col: str = "class_counts",
    seed: int = 42,
) -> pd.Series:
    """`images[classes_col]` là vector đếm số box theo lớp (độ dài num_classes).

    Trả về Series tên tập (train/val/test) theo index của `images`.
    """
    rng = np.random.default_rng(seed)
    names = list(ratios)
    target = np.array([ratios[n] for n in names], dtype=float)
    target /= target.sum()

    groups = images.groupby(group_col)
    group_ids = list(groups.groups)
    counts = np.stack([np.sum(np.stack(groups.get_group(g)[classes_col].to_list()), axis=0) for g in group_ids])
    n_images = np.array([len(groups.get_group(g)) for g in group_ids])

    totals = counts.sum(axis=0) + 1e-9
    # nhóm chứa lớp hiếm được xếp trước; xáo nhẹ để không phụ thuộc thứ tự file
    rarity = np.where(counts > 0, 1.0 / totals, 0).max(axis=1)
    order = np.lexsort((rng.random(len(group_ids)), -rarity))

    assigned_cls = np.zeros((len(names), num_classes))
    assigned_img = np.zeros(len(names))
    total_img = n_images.sum()
    result: dict[object, str] = {}
    for gi in order:
        c = counts[gi]
        # thiếu hụt tương đối theo số ảnh (dùng cho ảnh nền và để phá thế hoà)
        img_deficit = (target * total_img - assigned_img) / total_img
        if c.sum() > 0:
            # Iterative stratification (Sechidis et al., 2011): quyết định theo lớp hiếm nhất mà nhóm chứa
            key = int(np.argmin(np.where(c > 0, totals, np.inf)))
            deficit = (target * totals[key] - assigned_cls[:, key]) / totals[key] + 1e-3 * img_deficit
        else:
            deficit = img_deficit
        k = int(np.argmax(deficit))
        assigned_cls[k] += c
        assigned_img[k] += n_images[gi]
        result[group_ids[gi]] = names[k]
    return images[group_col].map(result)


def split_report(images: pd.DataFrame, split_col: str, classes_col: str) -> pd.DataFrame:
    """Bảng số box theo lớp × tập để kiểm tra độ cân bằng sau khi chia."""
    rows = {s: np.sum(np.stack(g[classes_col].to_list()), axis=0) for s, g in images.groupby(split_col)}
    return pd.DataFrame(rows)


def stratification_vectors(images: pd.DataFrame, boxes: pd.DataFrame, num_classes: int) -> pd.Series:
    """Vector [số box theo lớp | one-hot độ phân giải] cho từng ảnh — cân bằng cả lớp lẫn nguồn ảnh."""
    counts = boxes.groupby(["image", "class_id"]).size().unstack(fill_value=0)
    counts = counts.reindex(columns=range(num_classes), fill_value=0)
    resolutions = sorted(images["resolution"].unique())
    return images.apply(
        lambda row: np.concatenate(
            [
                counts.loc[row["image"]].to_numpy() if row["image"] in counts.index else np.zeros(num_classes),
                [float(row["resolution"] == r) for r in resolutions],
            ]
        ),
        axis=1,
    )


def materialize(images: pd.DataFrame, split_col: str, out_dir: Path, names: list[str]) -> Path:
    """Copy ảnh + nhãn vào <out_dir>/<split>/{images,labels}, ghi data.yaml (đường dẫn tương đối) và manifest.csv."""
    from .labels import label_path_for

    for _, row in images.iterrows():
        src = Path(row["path"])
        for sub, src_file, name in (("images", src, src.name), ("labels", label_path_for(src), src.stem + ".txt")):
            dst = out_dir / row[split_col] / sub / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src_file.exists():
                shutil.copy2(src_file, dst)
            else:
                dst.write_text("", encoding="utf-8")
    data_yaml = {
        "path": ".",
        "train": "train/images",
        "val": "val/images",
        "test": "test/images",
        "nc": len(names),
        "names": names,
    }
    (out_dir / "data.yaml").write_text(yaml.safe_dump(data_yaml, allow_unicode=True, sort_keys=False), "utf-8")
    images.drop(columns=["class_counts"], errors="ignore").to_csv(out_dir / "manifest.csv", index=False)
    return out_dir
