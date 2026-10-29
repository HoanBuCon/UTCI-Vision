"""Đọc/ghi nhãn định dạng YOLO (class cx cy w h, chuẩn hoá 0..1) và chuyển đổi toạ độ."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

IMG_EXTS = (".jpg", ".jpeg", ".png", ".bmp")


@dataclass
class YoloBox:
    class_id: int
    cx: float
    cy: float
    w: float
    h: float

    def to_xyxy(self, img_w: int, img_h: int) -> tuple[float, float, float, float]:
        x1 = (self.cx - self.w / 2) * img_w
        y1 = (self.cy - self.h / 2) * img_h
        x2 = (self.cx + self.w / 2) * img_w
        y2 = (self.cy + self.h / 2) * img_h
        return x1, y1, x2, y2

    @property
    def area(self) -> float:
        return self.w * self.h

    def is_valid(self, num_classes: int) -> bool:
        in_range = all(0.0 <= v <= 1.0 for v in (self.cx, self.cy)) and 0.0 < self.w <= 1.0 and 0.0 < self.h <= 1.0
        return in_range and 0 <= self.class_id < num_classes


def parse_label_line(line: str) -> YoloBox:
    parts = line.split()
    if len(parts) != 5:
        raise ValueError(f"Dòng nhãn cần 5 giá trị, nhận {len(parts)}: {line!r}")
    return YoloBox(int(parts[0]), *(float(v) for v in parts[1:]))


def read_labels(path: str | Path) -> list[YoloBox]:
    path = Path(path)
    if not path.exists():
        return []
    return [parse_label_line(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_labels(path: str | Path, boxes: list[YoloBox]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{b.class_id} {b.cx:.6f} {b.cy:.6f} {b.w:.6f} {b.h:.6f}" for b in boxes]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def remap_labels(src: str | Path, dst: str | Path, mapping: dict[int, int]) -> None:
    """Ghi file nhãn với id lớp đổi theo `mapping` (id gốc -> id mô hình); file nguồn thiếu -> file rỗng (ảnh nền)."""
    write_labels(dst, [YoloBox(mapping[b.class_id], b.cx, b.cy, b.w, b.h) for b in read_labels(src)])


def xyxy_to_yolo(class_id: int, box: tuple[float, float, float, float], img_w: int, img_h: int) -> YoloBox:
    x1, y1, x2, y2 = box
    return YoloBox(class_id, (x1 + x2) / 2 / img_w, (y1 + y2) / 2 / img_h, (x2 - x1) / img_w, (y2 - y1) / img_h)


def label_path_for(image_path: str | Path) -> Path:
    """.../<split>/images/abc.jpg -> .../<split>/labels/abc.txt"""
    image_path = Path(image_path)
    return image_path.parent.parent / "labels" / (image_path.stem + ".txt")


def list_images(split_dir: str | Path) -> list[Path]:
    images_dir = Path(split_dir) / "images"
    return sorted(p for p in images_dir.iterdir() if p.suffix.lower() in IMG_EXTS)
