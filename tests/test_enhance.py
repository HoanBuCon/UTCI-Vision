"""utci_vision.enhance: đánh giá chất lượng frame + tăng cường thích nghi."""

from __future__ import annotations

import numpy as np
import pytest

from utci_vision.config import load_config
from utci_vision.enhance import FrameQuality, assess, auto_gamma, enhance, gamma_correct, needed_ops

CFG = load_config("pipeline")


def textured(mean: int, amplitude: int, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base = np.full((240, 640, 3), mean, np.int16)
    base[:, ::40] += amplitude  # sọc dọc tạo tương phản
    return np.clip(base + rng.integers(-3, 4, base.shape), 0, 255).astype(np.uint8)


def test_assess_dark_vs_bright():
    dark, bright = assess(textured(30, 40)), assess(textured(170, 40))
    assert dark.mean_v < CFG["quality"]["dark_mean_v"] < bright.mean_v
    assert 0 <= dark.std_l <= 1 and dark.laplacian_var >= 0


def test_needed_ops_follow_thresholds():
    q = CFG["quality"]
    assert needed_ops(FrameQuality(0.6, 0.3, 100), q) == set()
    assert needed_ops(FrameQuality(0.1, 0.3, 100), q) == {"gamma", "clahe"}
    assert needed_ops(FrameQuality(0.6, 0.01, 100), q) == {"clahe"}
    assert needed_ops(FrameQuality(0.6, 0.3, q["noisy_laplacian"] + 1), q) == {"denoise"}


def test_auto_gamma_brightens_dark_image():
    img = textured(40, 30)
    g = auto_gamma(img, 0.5, 0.4, 3.0)
    assert g > 1
    assert gamma_correct(img, g).mean() > img.mean()
    assert gamma_correct(img, 1.0) == pytest.approx(img, abs=1)


def test_enhance_no_ops_is_identity_and_keeps_shape():
    img = textured(40, 30)
    assert enhance(img, set(), CFG["enhance"]) is img
    out = enhance(img, {"gamma", "clahe", "denoise"}, CFG["enhance"])
    assert out.shape == img.shape and out.dtype == np.uint8
    assert assess(out).mean_v > assess(img).mean_v
