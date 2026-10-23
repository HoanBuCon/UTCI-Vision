"""utci_vision.evaluation: metric, ablation, suy giảm ảnh."""

from __future__ import annotations

import numpy as np
import pytest

from utci_vision.config import load_config
from utci_vision.evaluation.experiments import ABLATIONS, DEGRADATIONS, apply_ablation
from utci_vision.evaluation.metrics import evaluate_detections, iou
from utci_vision.structures import Detection


def test_iou():
    assert iou((0, 0, 10, 10), (0, 0, 10, 10)) == pytest.approx(1.0)
    assert iou((0, 0, 10, 10), (5, 0, 15, 10)) == pytest.approx(1 / 3)
    assert iou((0, 0, 1, 1), (2, 2, 3, 3)) == 0.0


def test_map_perfect_and_wrong_class():
    gts = [[(1, (10, 10, 50, 50))], [(2, (0, 0, 20, 20))]]
    perfect = [[Detection((10, 10, 50, 50), 1, 0.9)], [Detection((0, 0, 20, 20), 2, 0.8)]]
    assert evaluate_detections(perfect, gts, 3)["map50"] == pytest.approx(1.0)
    res = evaluate_detections([[Detection((10, 10, 50, 50), 0, 0.9)], []], gts, 3)
    assert res["map50"] == pytest.approx(0.0) and res["recall"] == 0.0


def test_apply_ablation_disables_flags_without_mutating():
    cfg = load_config("pipeline")
    out = apply_ablation(cfg, ABLATIONS["yolo_only"])
    assert out["verifier"]["enabled"] is False and out["tracking"]["enabled"] is False
    assert cfg["verifier"]["enabled"] is True


def test_ablation_flags_exist_in_pipeline_config():
    cfg = load_config("pipeline")
    for flags in ABLATIONS.values():
        apply_ablation(cfg, flags)  # KeyError nếu cờ không tồn tại


def test_degradations_keep_shape():
    img = np.random.default_rng(0).integers(0, 255, (40, 60, 3), dtype=np.uint8)
    for fn in DEGRADATIONS.values():
        out = fn(img)
        assert out.shape == img.shape and out.dtype == np.uint8
