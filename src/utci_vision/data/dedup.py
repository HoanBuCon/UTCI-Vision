"""Phát hiện ảnh gần trùng bằng perceptual hash và gom cụm (FR-DATA-03).

Ảnh dashcam liên tiếp hoặc bản augment của cùng một ảnh gốc phải nằm cùng một tập
khi chia train/val/test, nếu không kết quả test sẽ bị "rò rỉ" (cao ảo).
"""

from __future__ import annotations

from pathlib import Path

import imagehash
import numpy as np
from PIL import Image

HASHERS = {"phash": imagehash.phash, "dhash": imagehash.dhash, "ahash": imagehash.average_hash}


def compute_hashes(paths: list[Path], method: str = "phash", hash_size: int = 8) -> np.ndarray:
    """(N, hash_size*hash_size) mảng bool."""
    hasher = HASHERS[method]
    rows = []
    for p in paths:
        with Image.open(p) as im:
            rows.append(hasher(im.convert("RGB"), hash_size=hash_size).hash.flatten())
    return np.array(rows, dtype=bool)


def _find(parent: np.ndarray, i: int) -> int:
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


def cluster_near_duplicates(hashes: np.ndarray, max_hamming: int = 6, chunk: int = 128) -> np.ndarray:
    """Union-find trên các cặp có khoảng cách Hamming <= max_hamming. Trả về id cụm cho từng ảnh."""
    n = len(hashes)
    parent = np.arange(n)
    packed = hashes.astype(np.uint8)
    for start in range(0, n, chunk):
        block = packed[start : start + chunk]
        # (chunk, N) khoảng cách Hamming
        dist = (block[:, None, :] != packed[None, :, :]).sum(axis=2)
        rows, cols = np.nonzero(dist <= max_hamming)
        for r, c in zip(rows + start, cols):
            if r < c:
                ra, rb = _find(parent, r), _find(parent, c)
                if ra != rb:
                    parent[rb] = ra
    return np.array([_find(parent, i) for i in range(n)])
