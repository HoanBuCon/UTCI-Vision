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

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from .structures import BBox, SignText, SignValue

# ---------------------------------------------------------------- 1. cắt vùng [CV]


def _clahe_bgr(img: np.ndarray, clip: float = 2.0, tile: int = 4) -> np.ndarray:
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    lab[..., 0] = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile)).apply(lab[..., 0])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def value_region(crop_bgr: np.ndarray, cfg: dict[str, Any]) -> np.ndarray | None:
    """Vùng chứa số (đĩa trong viền đỏ, đã phóng to + CLAHE); None nếu crop quá nhỏ để đọc."""
    v = cfg["value"]
    h, w = crop_bgr.shape[:2]
    if min(h, w) < v["min_crop_height"]:
        return None
    r = v["inner_disc_ratio"]
    y0, x0 = int(h * (1 - r) / 2), int(w * (1 - r) / 2)
    inner = crop_bgr[y0 : h - y0, x0 : w - x0]
    # chỉ giữ dải giữa theo chiều dọc — số nằm ngang giữa biển, tránh viền đỏ trên/dưới bị đọc thành ký tự
    band = inner[int(inner.shape[0] * 0.18) : int(inner.shape[0] * 0.82)]
    up = cv2.resize(band, None, fx=v["upscale"], fy=v["upscale"], interpolation=cv2.INTER_CUBIC)
    return _clahe_bgr(up)


def _deskew(gray: np.ndarray) -> np.ndarray:
    _, ink = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    pts = cv2.findNonZero(ink)
    if pts is None or len(pts) < 20:
        return gray
    angle = cv2.minAreaRect(pts)[2]
    angle = angle - 90 if angle > 45 else angle
    if abs(angle) < 1 or abs(angle) > 15:  # chỉ nắn nghiêng nhẹ; góc lớn thường là do nhiễu
        return gray
    h, w = gray.shape
    m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(gray, m, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def text_lines(crop_bgr: np.ndarray, cfg: dict[str, Any]) -> list[np.ndarray]:
    """Tách các dòng chữ của biển (phóng to -> CLAHE -> nắn nghiêng -> projection profile theo hàng)."""
    t = cfg["text"]
    if crop_bgr.shape[0] < t["min_crop_height"]:
        return []
    up = cv2.resize(crop_bgr, None, fx=t["upscale"], fy=t["upscale"], interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(_clahe_bgr(up, t["clahe"]["clip_limit"], t["clahe"]["tile_grid"]), cv2.COLOR_BGR2GRAY)
    if t.get("deskew", True):
        gray = _deskew(gray)
    _, ink = cv2.threshold(gray, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if ink.mean() > 0.5:  # chữ tối trên nền sáng -> đảo để "mực" = 1
        ink = 1 - ink
    h, w = gray.shape
    margin = int(h * 0.04)  # bỏ viền biển trên / dưới
    ink[:margin], ink[h - margin :] = 0, 0
    rows = ink.mean(axis=1) > 0.04
    lines, start = [], None
    for y, on in enumerate([*rows, False]):
        if on and start is None:
            start = y
        elif not on and start is not None:
            seg_h = y - start
            # dòng chữ: không quá mỏng (nhiễu, vạch kẻ) và không quá cao (biểu tượng, hình vẽ trên biển chỉ dẫn)
            if 0.06 * h <= seg_h <= 0.35 * h:
                pad = max(2, int(seg_h * 0.25))
                lines.append(cv2.cvtColor(gray[max(0, start - pad) : min(h, y + pad)], cv2.COLOR_GRAY2BGR))
            start = None
    return lines


def find_sub_sign(image_bgr: np.ndarray, sign_bbox: BBox, cfg: dict[str, Any]) -> BBox | None:
    """Tấm chữ nhật sáng (nền trắng) ngay dưới biển chính; None nếu không có."""
    s = cfg["sub_sign"]
    img_h, img_w = image_bgr.shape[:2]
    x1, y1, x2, y2 = sign_bbox
    w, h = x2 - x1, y2 - y1
    sx1, sx2 = int(max(0, x1 - 0.5 * w)), int(min(img_w, x2 + 0.5 * w))
    sy1, sy2 = int(min(img_h, y2)), int(min(img_h, y2 + s["search_below_ratio"] * h))
    if sy2 - sy1 < 6 or sx2 - sx1 < 6:
        return None
    hsv = cv2.cvtColor(image_bgr[sy1:sy2, sx1:sx2], cv2.COLOR_BGR2HSV)
    white = ((hsv[..., 1] < 60) & (hsv[..., 2] > 150)).astype(np.uint8)
    white = cv2.morphologyEx(white, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best = None
    for c in contours:
        bx, by, bw, bh = cv2.boundingRect(c)
        if bw < 0.6 * w or bh < 0.2 * h or bw / max(bh, 1) < s["min_aspect"]:
            continue
        fill = white[by : by + bh, bx : bx + bw].mean()
        if fill >= s["min_fill_white"] and (best is None or bw * bh > best[2] * best[3]):
            best = (bx, by, bw, bh)
    if best is None:
        return None
    bx, by, bw, bh = best
    return (float(sx1 + bx), float(sy1 + by), float(sx1 + bx + bw), float(sy1 + by + bh))


def frame_score(crop_bgr: np.ndarray) -> float:
    """Điểm chọn frame tốt nhất của track: diện tích × độ nét (phương sai Laplacian)."""
    gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)
    return float(gray.size * cv2.Laplacian(gray, cv2.CV_64F).var())


# ---------------------------------------------------------------- 2. nhận dạng [DL]


class TextReader:
    """Bọc VietOCR (`vgg_transformer`). Trọng số local ở cfg["reader"]["weights"]; thiếu thì tải pretrained."""

    def __init__(self, cfg: dict[str, Any]):
        from PIL import Image  # noqa: F401 — kiểm tra sớm phụ thuộc
        from vietocr.tool.config import Cfg
        from vietocr.tool.predictor import Predictor

        from .config import resolve

        self.cfg = cfg
        r = cfg["reader"]
        local_cfg = resolve(r["config_file"]) if r.get("config_file") else None
        if local_cfg is not None and local_cfg.exists():  # chạy offline (Docker, máy demo không có mạng)
            vcfg = Cfg.load_config_from_file(str(local_cfg))
        else:
            vcfg = Cfg.load_config_from_name(r["config_name"])  # tải base.yml + cấu hình mô hình từ vocr.vn
            if local_cfg is not None and local_cfg.parent.exists():
                vcfg.save(str(local_cfg))
        weights = r.get("weights")
        if weights and resolve(weights).exists():
            vcfg["weights"] = str(resolve(weights))
        vcfg["device"] = _device(r.get("device", "auto"))
        vcfg["predictor"]["beamsearch"] = False
        vcfg["cnn"]["pretrained"] = (
            False  # trọng số ImageNet của backbone thừa (bị nạp đè) — tránh tải 548 MB lúc khởi động
        )
        self.predictor = Predictor(vcfg)

    def read(self, images_bgr: list[np.ndarray]) -> list[tuple[str, float]]:
        """Mỗi ảnh (vùng số hoặc dòng chữ) -> (chuỗi, xác suất)."""
        from PIL import Image

        out = []
        for img in images_bgr:
            text, prob = self.predictor.predict(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), return_prob=True)
            out.append((text.strip(), float(prob)))
        return out


def _device(name: str) -> str:
    if name != "auto":
        return name
    try:
        import torch

        return "cuda:0" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


# ---------------------------------------------------------------- 3. hậu xử lý


_NUMBER = re.compile(r"\d+(?:[.,]\d+)?")


def parse_value(raw: str, unit: str, valid_values: dict[str, Any]) -> SignValue | None:
    """Chuỗi "50" + đơn vị km/h -> SignValue(50, "km/h"); None nếu không có số hợp lệ cho đơn vị đó."""
    rule = valid_values.get(unit)
    if rule is None:
        return None
    for token in _NUMBER.findall(raw.replace("O", "0").replace("o", "0")):
        number = float(token.replace(",", "."))
        ok = number in rule if isinstance(rule, list) else rule["min"] <= number <= rule["max"]
        if ok:
            return SignValue(number=number, unit=unit)
    return None


def load_lexicon(path: str | Path) -> list[str]:
    from .config import resolve

    p = resolve(path)
    if not p.exists():
        return []
    return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")]


def correct_text(raw: str, lexicon: list[str], min_similarity: int) -> str:
    """Khớp mờ toàn chuỗi với từ điển (không phân biệt hoa thường); giữ nguyên nếu không đủ giống."""
    if not raw or not lexicon:
        return raw
    from rapidfuzz import fuzz, process

    match = process.extractOne(raw.upper(), [w.upper() for w in lexicon], scorer=fuzz.ratio)
    if match and match[1] >= min_similarity:
        return lexicon[match[2]]
    return raw


_TIME = re.compile(r"(\d{1,2})\s*(?:h|giờ|:)\s*(\d{2})?\s*(?:-|–|đến)\s*(\d{1,2})\s*(?:h|giờ|:)?\s*(\d{2})?", re.I)
_DIST = re.compile(r"(\d+(?:[.,]\d+)?)\s*(km|m)\b", re.I)
_EXCEPT = re.compile(r"\btrừ\b\s*(.+)", re.I)


def parse_meaning(text: str) -> dict[str, Any]:
    """vd. {"time_ranges": [["06:00", "22:00"]], "distance_m": 100, "except_vehicles": ["xe buýt"]}"""
    out: dict[str, Any] = {}
    ranges = [[f"{int(a):02d}:{b or '00'}", f"{int(c):02d}:{d or '00'}"] for a, b, c, d in _TIME.findall(text)]
    if ranges:
        out["time_ranges"] = ranges
    rest = _TIME.sub(" ", text)
    if m := _DIST.search(rest):
        value = float(m.group(1).replace(",", "."))
        out["distance_m"] = value * 1000 if m.group(2).lower() == "km" else value
    if m := _EXCEPT.search(text):
        vehicles = [v.strip(" .,;").lower() for v in re.split(r",|và|;", _TIME.sub("", m.group(1))) if v.strip(" .,;")]
        if vehicles:
            out["except_vehicles"] = vehicles
    return out


def vote(readings: list[SignText] | list[SignValue]) -> SignText | SignValue | None:
    """Chọn kết quả có tổng độ tin cậy lớn nhất qua các lần đọc của cùng một track."""
    if not readings:
        return None
    totals: dict[Any, float] = defaultdict(float)
    best: dict[Any, Any] = {}
    for r in readings:
        key = (r.number, r.unit) if isinstance(r, SignValue) else r.text
        totals[key] += r.confidence
        if key not in best or r.confidence > best[key].confidence:
            best[key] = r
    return best[max(totals, key=totals.get)]


# ---------------------------------------------------------------- 4. ghép các bước cho một biển


def read_sign(
    image_bgr: np.ndarray, bbox: BBox, has_value: bool, unit: str | None, has_text: bool,
    reader: TextReader, cfg: dict[str, Any], lexicon: list[str],
) -> tuple[SignValue | None, SignText | None, SignText | None, dict[str, np.ndarray]]:  # fmt: skip
    """-> (giá trị số, chữ trên biển, chữ biển phụ, ảnh trung gian cho chế độ Giải thích)."""
    x1, y1, x2, y2 = (int(round(v)) for v in bbox)
    crop = image_bgr[max(0, y1) : y2, max(0, x1) : x2]
    debug: dict[str, np.ndarray] = {}
    value = text = sub = None
    if crop.size == 0:
        return value, text, sub, debug
    if has_value and unit:
        region = value_region(crop, cfg)
        if region is not None:
            debug["value_region"] = region
            raw, prob = reader.read([region])[0]
            value = parse_value(raw, unit, cfg["value"]["valid_values"])
            if value is not None:
                value.confidence = prob
    if has_text:
        lines = text_lines(crop, cfg)
        if lines:
            debug["text_lines"] = np.vstack(
                [cv2.resize(ln, (300, max(1, int(300 * ln.shape[0] / ln.shape[1])))) for ln in lines]
            )
            reads = reader.read(lines)
            reads = [(t, pr) for t, pr in reads if t and pr >= cfg["postprocess"]["min_confidence"]]
            raw = " ".join(t for t, _ in reads)
            fixed = correct_text(raw, lexicon, cfg["postprocess"]["min_similarity"])
            text = (
                None
                if not reads
                else SignText(
                    raw=raw, text=fixed, confidence=float(np.mean([p for _, p in reads])), parsed=parse_meaning(fixed)
                )
            )
    if cfg["sub_sign"]["enabled"]:
        sub_box = find_sub_sign(image_bgr, bbox, cfg)
        if sub_box is not None:
            sx1, sy1, sx2, sy2 = (int(v) for v in sub_box)
            sub_crop = image_bgr[sy1:sy2, sx1:sx2]
            lines = text_lines(sub_crop, {**cfg, "text": {**cfg["text"], "min_crop_height": 12}})
            if lines:
                debug["sub_sign"] = sub_crop
                reads = [(t, pr) for t, pr in reader.read(lines) if t and pr >= cfg["postprocess"]["min_confidence"]]
                raw = " ".join(t for t, _ in reads)
                if raw:
                    fixed = correct_text(raw, lexicon, cfg["postprocess"]["min_similarity"])
                    sub = SignText(
                        raw=raw,
                        text=fixed,
                        confidence=float(np.mean([p for _, p in reads])),
                        parsed=parse_meaning(fixed),
                    )
    return value, text, sub, debug
