"""utci_vision.data: nhãn YOLO, gom ảnh gần trùng, chia lại, crop."""

from __future__ import annotations

import cv2
import numpy as np
import pandas as pd
import pytest

from utci_vision.data.crops import build_crops
from utci_vision.data.dedup import cluster_near_duplicates
from utci_vision.data.labels import YoloBox, parse_label_line, read_labels, write_labels, xyxy_to_yolo
from utci_vision.data.split import grouped_stratified_split, materialize, read_exclusions


def test_label_roundtrip(tmp_path):
    boxes = [YoloBox(3, 0.5, 0.5, 0.1, 0.2), YoloBox(24, 0.1, 0.9, 0.05, 0.05)]
    write_labels(tmp_path / "a.txt", boxes)
    assert read_labels(tmp_path / "a.txt") == pytest.approx(boxes)
    assert read_labels(tmp_path / "missing.txt") == []


def test_parse_label_rejects_polygon():
    with pytest.raises(ValueError):
        parse_label_line("1 0.1 0.1 0.2 0.2 0.3 0.3")


def test_xyxy_yolo_conversion():
    b = xyxy_to_yolo(5, (100, 50, 200, 150), 400, 200)
    assert b.to_xyxy(400, 200) == pytest.approx((100, 50, 200, 150))
    assert b.is_valid(32) and not YoloBox(40, 0.5, 0.5, 0.1, 0.1).is_valid(32)


def test_dedup_clusters_near_hashes():
    base = np.random.default_rng(0).integers(0, 2, 64).astype(bool)
    near = base.copy()
    near[:2] = ~near[:2]
    clusters = cluster_near_duplicates(np.stack([base, near, ~base]), max_hamming=4)
    assert clusters[0] == clusters[1] != clusters[2]


def test_grouped_split_keeps_groups_together_and_covers_classes():
    rng = np.random.default_rng(1)
    rows = []
    for g in range(80):
        vec = np.zeros(4)
        vec[g % 4] = 1
        rows += [{"dup_cluster": g, "class_counts": vec} for _ in range(int(rng.integers(1, 4)))]
    df = pd.DataFrame(rows)
    split = grouped_stratified_split(df, 4, {"train": 0.7, "val": 0.15, "test": 0.15})
    assert (df.assign(s=split).groupby("dup_cluster")["s"].nunique() == 1).all()
    per_class = df.assign(s=split, c=[int(v.argmax()) for v in df["class_counts"]]).groupby("c")["s"].nunique()
    assert (per_class == 3).all()  # mọi lớp có mặt ở cả 3 tập


def test_crops_only_selected_classes(tmp_path):
    (tmp_path / "images").mkdir()
    cv2.imwrite(str(tmp_path / "images" / "a.jpg"), np.zeros((100, 200, 3), np.uint8))
    write_labels(tmp_path / "labels" / "a.txt", [YoloBox(24, 0.5, 0.5, 0.3, 0.4), YoloBox(1, 0.2, 0.2, 0.2, 0.3)])
    stats = build_crops(tmp_path, tmp_path / "out", classes=[24], pad_ratio=0.1, min_side=10)
    assert stats["crops"] == 1 and (tmp_path / "out" / "24").exists() and not (tmp_path / "out" / "1").exists()


def test_read_exclusions_parses_tab_reason_and_comments(tmp_path):
    f = tmp_path / "excluded.txt"
    f.write_text("# ghi chú\ntrain/images/a.jpg\tlý do\n\nvalid/images/b.jpg\n", encoding="utf-8")
    assert read_exclusions([f]) == {"a.jpg", "b.jpg"}


def test_exclusion_lists_in_repo_point_to_real_names():
    from utci_vision.config import load_config, resolve

    names = read_exclusions([resolve(p) for p in load_config("data")["split"]["exclude_lists"]])
    assert len(names) == 67 and all(n.endswith(".jpg") for n in names)


def test_materialize_remaps_class_ids_and_clears_stale_build(tmp_path):
    raw = tmp_path / "raw" / "train"
    (raw / "images").mkdir(parents=True)
    for name in ("a", "b"):
        cv2.imwrite(str(raw / "images" / f"{name}.jpg"), np.zeros((10, 10, 3), np.uint8))
    write_labels(raw / "labels" / "a.txt", [YoloBox(5, 0.5, 0.5, 0.2, 0.2), YoloBox(1, 0.2, 0.2, 0.1, 0.1)])
    out = tmp_path / "v1"
    (out / "train" / "labels").mkdir(parents=True)
    (out / "data.yaml").write_text("nc: 32\n")
    (out / "train" / "labels.cache").write_bytes(b"old")
    images = pd.DataFrame(
        {"path": [str(raw / "images" / "a.jpg"), str(raw / "images" / "b.jpg")], "s": ["train", "val"]}
    )
    materialize(images, "s", out, ["x", "y", "other"], {1: 0, 5: 2})
    assert [b.class_id for b in read_labels(out / "train" / "labels" / "a.txt")] == [2, 0]
    assert (out / "val" / "labels" / "b.txt").read_text() == ""  # ảnh nền
    assert not (out / "train" / "labels.cache").exists() and "nc: 3" in (out / "data.yaml").read_text()


def test_materialize_refuses_to_delete_unknown_dir(tmp_path):
    (tmp_path / "keep.txt").write_text("x")
    with pytest.raises(FileExistsError):
        materialize(pd.DataFrame({"path": [], "s": []}), "s", tmp_path, ["x"], {})
