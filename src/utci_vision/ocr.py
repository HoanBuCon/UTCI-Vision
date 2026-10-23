"""[CV + DL] Đọc số và chữ tiếng Việt trên biển / biển phụ (FR-PIPE-07..11).
Phụ trách: TV2 (cắt vùng, S3–S4) · TV3 (VietOCR, S3) · TV1 (hậu xử lý, S3–S4).

1. Cắt vùng [CV]: vùng số (đĩa trắng trong viền đỏ) · dòng chữ (phóng to, CLAHE, nắn nghiêng, projection profile)
   · biển phụ (tấm chữ nhật sáng ngay dưới biển chính) · frame tốt nhất của track (diện tích × độ nét).
2. Nhận dạng [DL]: VietOCR pretrained `vgg_transformer`. Đã kiểm chứng 2026-10-22 (vietocr 0.3.13 `--no-deps`,
   torch 2.14.1 CPU): "Trừ xe buýt", "6h - 22h" đúng; "KIỂM TRA" -> "KIỀM TRA"; ~120–290 ms/dòng trên CPU.
3. Hậu xử lý (luật): regex trích số + hợp lệ hoá theo đơn vị · khớp mờ với từ điển (rapidfuzz) · trích nghĩa
   (khung giờ, khoảng cách, loại xe) · bỏ phiếu qua nhiều lần đọc của track.
Tham số: configs/ocr.yaml.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .structures import BBox, SignText, SignValue

# ---------------------------------------------------------------- 1. cắt vùng [CV]


def value_region(crop_bgr: np.ndarray, cfg: dict[str, Any]) -> np.ndarray | None:
    """Vùng chứa số (đã phóng to); None nếu crop quá nhỏ / không tìm được viền."""
    raise NotImplementedError("TODO(TV2, S3)")


def text_lines(crop_bgr: np.ndarray, cfg: dict[str, Any]) -> list[np.ndarray]:
    raise NotImplementedError("TODO(TV2, S4)")


def find_sub_sign(image_bgr: np.ndarray, sign_bbox: BBox, cfg: dict[str, Any]) -> BBox | None:
    raise NotImplementedError("TODO(TV2, S4)")


def frame_score(crop_bgr: np.ndarray) -> float:
    raise NotImplementedError("TODO(TV2, S4)")


# ---------------------------------------------------------------- 2. nhận dạng [DL]


class TextReader:
    """Bọc VietOCR. Cách dùng thư viện:

    cfg = vietocr.tool.config.Cfg.load_config_from_name("vgg_transformer"); cfg["device"] = "cuda:0" | "cpu"
    text, prob = vietocr.tool.predictor.Predictor(cfg).predict(pil_image, return_prob=True)
    """

    def __init__(self, cfg: dict[str, Any]):
        self.cfg = cfg
        self.predictor = None  # TODO(TV3, S3): nạp VietOCR; hỗ trợ trọng số local khi offline

    def read(self, images_bgr: list[np.ndarray]) -> list[tuple[str, float]]:
        """Mỗi ảnh (vùng số hoặc dòng chữ) -> (chuỗi, xác suất)."""
        raise NotImplementedError("TODO(TV3, S3)")


# ---------------------------------------------------------------- 3. hậu xử lý


def parse_value(raw: str, unit: str, valid_values: dict[str, Any]) -> SignValue | None:
    """Chuỗi "50" + đơn vị km/h -> SignValue(50, "km/h"); None nếu không có số hợp lệ cho đơn vị đó."""
    raise NotImplementedError("TODO(TV1, S3)")


def correct_text(raw: str, lexicon: list[str], min_similarity: int) -> str:
    raise NotImplementedError("TODO(TV1, S4)")


def parse_meaning(text: str) -> dict[str, Any]:
    """vd. {"time_ranges": [["06:00", "22:00"]], "distance_m": 100, "except_vehicles": ["xe buýt"]}"""
    raise NotImplementedError("TODO(TV1, S4)")


def vote(readings: list[SignText] | list[SignValue]) -> SignText | SignValue | None:
    raise NotImplementedError("TODO(TV1, S4)")
