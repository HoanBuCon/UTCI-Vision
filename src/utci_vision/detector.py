"""[DL] Detector YOLO11: fine-tune từ trọng số pretrained (FR-TRAIN-04) + suy luận trong pipeline (FR-PIPE-03). Phụ trách: TV3.

Fine-tuning, không train lại từ đầu: khởi tạo từ `yolo11{n,s}.pt` (pretrained COCO) hoặc một checkpoint
của nhóm (`init_weights`), có thể đóng băng backbone (`freeze`). Ultralytics import trễ — torch do người dùng tự cài.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import numpy as np

from .structures import Detection


def train_params(cfg: dict[str, Any], overrides: dict[str, Any] | None = None, smoke: bool = False) -> dict[str, Any]:
    """configs/yolo.yaml > train <- overrides của notebook <- smoke (smoke luôn thắng: 1 epoch dù notebook đặt EPOCHS)."""
    return {**cfg["train"], **(overrides or {}), **(cfg["smoke"] if smoke else {})}


def finetune(
    data_yaml: Path,
    run_dir: Path,
    cfg: dict[str, Any],
    overrides: dict[str, Any] | None = None,
    smoke: bool = False,
    init_weights: Path | None = None,
    resume: Path | None = None,
) -> dict[str, float]:
    """Fine-tune theo configs/yolo.yaml; copy best.pt -> run_dir/yolo11.pt; trả metric val.

    init_weights: checkpoint của nhóm để fine-tune tiếp (mặc định: pretrained COCO `cfg["model"]`).
    resume: last.pt của chính lần chạy bị ngắt (Colab) — tiếp tục, không phải lần fine-tune mới.
    """
    from ultralytics import YOLO

    if resume is not None:
        model = YOLO(str(resume))
        results = model.train(resume=True)
    else:
        model = YOLO(str(init_weights or cfg["model"]))
        results = model.train(
            data=str(data_yaml), project=str(run_dir), name="yolo", exist_ok=True, **train_params(cfg, overrides, smoke)
        )
    if Path(model.trainer.best).exists():
        shutil.copy2(model.trainer.best, run_dir / "yolo11.pt")
    return {k: float(v) for k, v in getattr(results, "results_dict", {}).items()}


def validate(
    weights: Path, data_yaml: Path, imgsz: int, split: str = "val", device: str | int | None = None, batch: int = 8
) -> dict[str, Any]:
    """mAP tổng + AP@50 theo lớp bằng Ultralytics val (đánh giá nhanh trong notebook; test chính thức chạy local)."""
    from ultralytics import YOLO

    model = YOLO(str(weights))
    box = model.val(
        data=str(data_yaml), imgsz=imgsz, split=split, device=device, batch=batch, plots=False, verbose=False
    ).box
    return {
        "map50": float(box.map50),
        "map50_95": float(box.map),
        "precision": float(box.mp),
        "recall": float(box.mr),
        "ap50_per_class": {model.names[int(c)]: float(ap) for c, ap in zip(box.ap_class_index, box.ap50)},
    }


class Detector:
    """Bọc YOLO11 đã fine-tune cho suy luận: nạp một lần, warm-up, dự đoán theo batch."""

    def __init__(
        self,
        weights: str | Path,
        imgsz: int,
        conf: float,
        iou: float,
        device: str | int | None = None,
        half: bool = True,
    ):
        from ultralytics import YOLO

        from .config import resolve

        self.model = YOLO(str(resolve(weights)))
        self.imgsz, self.conf, self.iou, self.device = imgsz, conf, iou, device
        self.half = half and str(device) != "cpu"
        self.detect([np.zeros((imgsz, imgsz, 3), np.uint8)])  # warm-up: lần chạy đầu chậm do khởi tạo CUDA

    def detect(self, images_bgr: list[np.ndarray], conf: float | None = None) -> list[list[Detection]]:
        """Batch frame BGR -> danh sách Detection mỗi frame (score = điểm YOLO, verified = None)."""
        results = self.model.predict(
            images_bgr,
            imgsz=self.imgsz,
            conf=self.conf if conf is None else conf,
            iou=self.iou,
            device=self.device,
            quantize=16 if self.half else None,  # FP16 (Ultralytics 8.4 thay `half` bằng `quantize`)
            verbose=False,
        )
        out = []
        for r in results:
            boxes = r.boxes
            xyxy = boxes.xyxy.cpu().numpy()
            cls = boxes.cls.cpu().numpy().astype(int)
            score = boxes.conf.cpu().numpy()
            out.append([Detection(tuple(map(float, b)), int(c), float(s)) for b, c, s in zip(xyxy, cls, score)])
        return out
