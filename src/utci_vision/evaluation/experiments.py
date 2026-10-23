"""Thiết lập thí nghiệm dùng chung: ablation (E2), suy giảm ảnh (E4), đo FPS. Phụ trách: TV1, TV5."""

from __future__ import annotations

import copy
import time
from collections.abc import Callable, Iterable
from typing import Any

import cv2
import numpy as np

# ---------------------------------------------------------------- E2: tắt dần các khâu của cùng một pipeline
_LATER = ["verifier.enabled", "ocr.enabled"]
ABLATIONS: dict[str, list[str]] = {
    "yolo_only": ["quality.enabled", "enhance.enabled", "tracking.enabled", *_LATER],
    "+enhance": ["tracking.enabled", *_LATER],
    "+verifier": ["tracking.enabled", "ocr.enabled"],
    "full": [],
}


def apply_ablation(cfg: dict[str, Any], disabled: list[str]) -> dict[str, Any]:
    out = copy.deepcopy(cfg)
    for path in disabled:
        *parents, leaf = path.split(".")
        node = out
        for key in parents:
            node = node[key]
        node[leaf] = False
    return out


# ---------------------------------------------------------------- E4: suy giảm nhân tạo
def darken(img: np.ndarray, gamma: float = 2.5) -> np.ndarray:
    return cv2.LUT(img, ((np.arange(256) / 255.0) ** gamma * 255).astype(np.uint8))


def motion_blur(img: np.ndarray, ksize: int = 9) -> np.ndarray:
    kernel = np.zeros((ksize, ksize), np.float32)
    kernel[ksize // 2, :] = 1.0 / ksize
    return cv2.filter2D(img, -1, kernel)


def gaussian_noise(img: np.ndarray, sigma: float = 15, seed: int = 0) -> np.ndarray:
    noise = np.random.default_rng(seed).normal(0, sigma, img.shape)
    return (img.astype(np.float32) + noise).clip(0, 255).astype(np.uint8)


def rain(img: np.ndarray, drops: int = 400, seed: int = 0) -> np.ndarray:
    rng, out = np.random.default_rng(seed), img.copy()
    h, w = out.shape[:2]
    for _ in range(drops):
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h))
        cv2.line(out, (x, y), (x + 2, min(h - 1, y + int(rng.integers(8, 20)))), (200, 200, 200), 1)
    return cv2.blur(out, (3, 3))


DEGRADATIONS: dict[str, Callable[[np.ndarray], np.ndarray]] = {
    "dark": darken,
    "motion_blur": motion_blur,
    "noise": gaussian_noise,
    "rain": rain,
}


# ---------------------------------------------------------------- FPS
def measure_fps(process: Callable[[np.ndarray], object], frames: Iterable[np.ndarray], warmup: int = 10) -> dict:
    times = []
    for i, frame in enumerate(frames):
        start = time.perf_counter()
        process(frame)
        if i >= warmup:
            times.append(time.perf_counter() - start)
    if not times:
        return {"fps": 0.0, "ms_mean": 0.0, "ms_p95": 0.0, "frames": 0}
    ms = np.array(times) * 1000
    return {
        "fps": float(1000 / ms.mean()),
        "ms_mean": float(ms.mean()),
        "ms_p95": float(np.percentile(ms, 95)),
        "frames": len(ms),
    }
