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
        params = {**cfg["train"], **(cfg["smoke"] if smoke else {}), **(overrides or {})}
        results = model.train(data=str(data_yaml), project=str(run_dir), name="yolo", exist_ok=True, **params)
    if Path(model.trainer.best).exists():
        shutil.copy2(model.trainer.best, run_dir / "yolo11.pt")
    return {k: float(v) for k, v in getattr(results, "results_dict", {}).items()}


def validate(weights: Path, data_yaml: Path, imgsz: int, split: str = "val") -> dict[str, Any]:
    """mAP tổng + AP theo lớp (đánh giá nhanh trong notebook; test chính thức chạy local)."""
    raise NotImplementedError("TODO(TV3, S1)")


class Detector:
    def __init__(self, weights: str, imgsz: int, conf: float, iou: float, device: str | None, half: bool):
        self.imgsz, self.conf, self.iou, self.device, self.half = imgsz, conf, iou, device, half
        self.model = None  # TODO(TV3, S1): YOLO(weights) + warm-up 1 frame

    def detect(self, images_bgr: list[np.ndarray], conf: float | None = None) -> list[list[Detection]]:
        """Batch frame -> danh sách Detection mỗi frame (score = điểm YOLO, verified = None)."""
        raise NotImplementedError("TODO(TV3, S1)")
