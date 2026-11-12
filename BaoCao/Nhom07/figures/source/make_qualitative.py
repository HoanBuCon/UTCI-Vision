"""Sinh ảnh minh hoạ định tính cho báo cáo bằng chính mã nguồn của hệ thống (không chỉnh tay).

Chạy từ gốc repo (cần dataset/processed/v1 và models/current):
    .venv/Scripts/python BaoCao/Nhom07/figures/source/make_qualitative.py
Ra:
  figures/qual/*.jpg          ảnh trung gian (dùng làm ảnh nhỏ trong sơ đồ draw.io)
  figures/ch3_dinh_tinh.pdf   YOLO vs CV truyền thống trên 3 ảnh mẫu
  figures/ch3_anh_toi.pdf     ảnh làm tối (γ 3,5): không tăng cường vs tăng cường thích nghi
  figures/ch2_cv_buoc.pdf     các bước của pipeline CV truyền thống trên một ảnh
"""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import yaml  # noqa: E402

from utci_vision import traditional as tr  # noqa: E402
from utci_vision.config import load_classes, load_config  # noqa: E402
from utci_vision.enhance import assess, enhance, needed_ops  # noqa: E402
from utci_vision.evaluation.experiments import darken  # noqa: E402
from utci_vision.pipeline import Recognizer, load_components  # noqa: E402
from utci_vision.visualize import draw  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
FIG = Path(__file__).resolve().parents[1]
QUAL = FIG / "qual"
QUAL.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": "Arial", "font.size": 8.5, "pdf.fonttype": 42,
                     "savefig.bbox": "tight", "savefig.pad_inches": 0.02})

samples = {s["id"]: s for s in yaml.safe_load((ROOT / "configs/samples.yaml").read_text(encoding="utf8"))["samples"]}
img_dir = ROOT / "dataset/processed/v1/test/images"


def load(sid: str) -> np.ndarray:
    return cv2.imread(str(img_dir / samples[sid]["file"]))


def save_jpg(name: str, img: np.ndarray, max_w: int = 900) -> None:
    h, w = img.shape[:2]
    if w > max_w:
        img = cv2.resize(img, (max_w, int(h * max_w / w)), interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(QUAL / f"{name}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 88])


def rgb(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


pipe_cfg = load_config("pipeline")
comps = load_components(pipe_cfg)
print({k: v for k, v in comps.status.items()})
classes = load_classes()
background = len(classes)
ver = load_config("verifier")["features"]
tcfg = load_config("traditional")["detect"]
log: dict[str, object] = {}


def run_dl(img: np.ndarray, enhance_on: bool = True, ocr: bool = False):
    cfg = json.loads(json.dumps(pipe_cfg))
    cfg["enhance"]["enabled"] = enhance_on
    cfg["ocr"]["enabled"] = ocr
    return Recognizer(cfg, comps, video=False).process(img, debug=True)


def run_cv(img: np.ndarray):
    q = assess(img, pipe_cfg["quality"]["downscale_width"])
    ops = needed_ops(q, pipe_cfg["quality"])
    work = enhance(img, ops, pipe_cfg["enhance"]) if ops else img
    dets, cands, info = tr.detect(work, comps.classic, ver["color_ranges"], tcfg)
    return work, [d for d in dets if d.class_id != background], cands, info


# ---------------------------------------------------------------- 1. YOLO vs CV trên 3 ảnh mẫu
rows = ["nhieu_bien1", "da_dang2", "bien_nho1"]
fig, axs = plt.subplots(len(rows), 2, figsize=(6.6, 5.6))
for r, sid in enumerate(rows):
    img = load(sid)
    deep = run_dl(img)
    work, cv_dets, cands, _ = run_cv(img)
    a, b = draw(img, deep.detections), draw(work, cv_dets)
    save_jpg(f"{sid}_yolo", a)
    save_jpg(f"{sid}_cv", b)
    log[sid] = {"gt_signs": samples[sid]["signs"], "yolo": len(deep.detections), "cv_candidates": len(cands),
                "cv_detections": len(cv_dets), "yolo_ms": deep.latency_ms.get("detector")}
    for c, (im, title) in enumerate([(a, f"YOLO11s: {len(deep.detections)} biển"),
                                      (b, f"CV truyền thống: {len(cv_dets)} biển")]):
        axs[r, c].imshow(rgb(im))
        axs[r, c].set_title(f"({chr(97 + 2 * r + c)}) {title}", fontsize=8.5)
        axs[r, c].axis("off")
fig.tight_layout(h_pad=0.6, w_pad=0.4)
fig.savefig(FIG / "ch3_dinh_tinh.pdf", dpi=220)
plt.close(fig)

# ---------------------------------------------------------------- 2. ảnh tối: tăng cường thích nghi
src = load("da_dang3")
dark = darken(src, 3.5)
no = run_dl(dark, enhance_on=False)
yes = run_dl(dark, enhance_on=True)
enh = yes.debug.get("images", {}).get("enhanced", dark)
log["toi"] = {"sample": "da_dang3", "gt_signs": samples["da_dang3"]["signs"], "khong_tang_cuong": len(no.detections),
              "tang_cuong": len(yes.detections), "ops": yes.debug.get("ops"), "quality": yes.debug.get("quality")}
save_jpg("toi_goc", dark)
save_jpg("toi_tang_cuong", enh)
fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.0))
for ax, im, t in [(axs[0], draw(dark, no.detections), f"(a) Không tăng cường: {len(no.detections)} biển"),
                  (axs[1], draw(enh, yes.detections), f"(b) Tăng cường thích nghi: {len(yes.detections)} biển")]:
    ax.imshow(rgb(im))
    ax.set_title(t, fontsize=8.5)
    ax.axis("off")
fig.tight_layout(w_pad=0.4)
fig.savefig(FIG / "ch3_anh_toi.pdf", dpi=220)
plt.close(fig)

# ---------------------------------------------------------------- 3. các bước CV truyền thống (một ảnh)
sid = "da_dang2"
img = load(sid)
work, cv_dets, cands, info = run_cv(img)
masks = tr.overlay_masks(work, info["masks"])
cand_img = tr.draw_candidates(work, cands)
save_jpg("cv_input", img)
save_jpg("cv_masks", masks)
save_jpg("cv_candidates", cand_img)
save_jpg("cv_result", draw(work, cv_dets))
crops = [tr.padded_crop(work, c.bbox) for c in cands]
cls, prob = comps.classic.predict([c for c in crops if c.size])
order = sorted(range(len(cands)), key=lambda i: (int(cls[i]) == background, -(cands[i].bbox[2] - cands[i].bbox[0])))
picked = order[:3]
VN_COLOR = {"red": "đỏ", "blue": "xanh", "yellow": "vàng"}
cells = []
for j, i in enumerate(picked):
    crop = cv2.resize(crops[i], (128, 128), interpolation=cv2.INTER_CUBIC)
    hog = tr.hog_image(crops[i], ver["hog"])
    sift, n_kp = tr.sift_keypoints(crops[i])
    name = classes[int(cls[i])].name_vi if int(cls[i]) != background else "nền"
    cells.append((crop, hog, sift, n_kp, name, float(prob[i]), cands[i]))
    cv2.imwrite(str(QUAL / f"cv_crop{j}.jpg"), crop)
    cv2.imwrite(str(QUAL / f"cv_hog{j}.jpg"), hog if hog.ndim == 3 else cv2.cvtColor(hog, cv2.COLOR_GRAY2BGR))
    cv2.imwrite(str(QUAL / f"cv_sift{j}.jpg"), sift)
log["cv_steps"] = {"sample": sid, "candidates": len(cands), "detections": len(cv_dets), "ms": info["ms"],
                   "cells": [{"class": c[4], "score": round(c[5], 3), "color": c[6].color, "shape": c[6].shape,
                              "sift_kp": c[3]} for c in cells]}

fig = plt.figure(figsize=(6.6, 2.6))
gs = fig.add_gridspec(2, 1, height_ratios=[1.4, 1], hspace=0.3)
top = gs[0].subgridspec(1, 3, wspace=0.04)
for k, (im, t) in enumerate([(masks, "(a) Mặt nạ màu HSV sau hình thái học"),
                             (cand_img, f"(b) Ứng viên theo hình dạng: {len(cands)}"),
                             (draw(work, cv_dets), f"(c) Sau HOG + màu + SVM: {len(cv_dets)} biển")]):
    ax = fig.add_subplot(top[k])
    ax.imshow(rgb(im))
    ax.set_title(t, fontsize=7.8)
    ax.axis("off")
bot = gs[1].subgridspec(1, 9, wspace=0.08)
for j, (crop, hog, sift, n_kp, name, p, c) in enumerate(cells):
    for k, (im, t) in enumerate([(crop, f"{VN_COLOR[c.color]} / {c.shape}"), (hog, "HOG"), (sift, f"SIFT: {n_kp} điểm")]):
        ax = fig.add_subplot(bot[3 * j + k])
        ax.imshow(rgb(im) if im.ndim == 3 else im, cmap="gray")
        ax.set_title(t, fontsize=6.6)
        ax.axis("off")
        if k == 1:
            ax.text(0.5, -0.12, f"SVM: {name} ({p:.2f})".replace(".", ","), transform=ax.transAxes, ha="center",
                    va="top", fontsize=6.6)
fig.text(0.5, -0.04, "(d) Vùng ứng viên, ảnh HOG, điểm SIFT và lớp do SVM dự đoán", ha="center", fontsize=7.8)
fig.savefig(FIG / "ch2_cv_buoc.pdf", dpi=220)
plt.close(fig)

# ---------------------------------------------------------------- 4. đọc số (OCR) + ảnh cho sơ đồ hệ thống
img = load("co_so1")
res = run_dl(img, ocr=True)
save_jpg("ocr_input", img)
save_jpg("ocr_result", draw(img, res.detections))
for k, v in res.debug.get("images", {}).items():
    if k != "enhanced":
        cv2.imwrite(str(QUAL / f"ocr_{k}.jpg"), v)
log["ocr"] = {"sample": "co_so1",
              "detections": [{"class": classes[d.class_id].name_vi, "score": round(d.score, 3), "value": d.value,
                              "text": d.text} for d in res.detections],
              "crops": sorted(k for k in res.debug.get("images", {}) if k != "enhanced")}
(QUAL / "log.json").write_text(json.dumps(log, ensure_ascii=False, indent=1, default=str), encoding="utf8")
print(json.dumps(log, ensure_ascii=False, indent=1, default=str))
