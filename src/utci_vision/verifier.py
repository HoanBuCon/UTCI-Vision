"""[CV + ML] Bộ xác minh: đặc trưng vùng (CV) + LightGBM stacking trên dự đoán YOLO (FR-PIPE-05/06, FR-TRAIN-05).
Phụ trách: TV2 (đặc trưng, S2) · TV1 (mô hình, S3).

- Đặc trưng vùng [CV]: tỉ lệ pixel đỏ/xanh/vàng/trắng (mask HSV) · độ tròn 4πA/P², số đỉnh approxPolyDP, solidity,
  tỉ lệ khung của contour lớn nhất · 7 Hu moments (log) · HOG crop xám 32×32 (→ PCA) · độ nét (phương sai Laplacian).
- Mô hình [ML]: mỗi mẫu = một box YOLO ở tập val (proposal_conf thấp); đặc trưng = [điểm YOLO, siêu lớp + id lớp,
  kích thước/vị trí box, đặc trưng vùng, độ khớp màu/hình dạng với siêu lớp]; nhãn = 1 nếu khớp GT cùng lớp.
  Fit (không pretrained), hiệu chỉnh xác suất; đầu ra thay cho điểm YOLO.
Tham số: configs/verifier.yaml.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import pandas as pd

from .structures import BBox, Detection

COLORS = ("red", "blue", "yellow", "white")
# Nhóm đặc trưng (ablation E3: màu / +hình học / +HOG). Thứ tự = thứ tự vector của region_features (chưa gồm HOG).
FEATURE_GROUPS: dict[str, list[str]] = {
    "color": [f"{c}_{part}" for c in COLORS for part in ("all", "ring", "core")],
    "shape": ["circularity", "n_vertices", "solidity", "extent", "contour_area", "contour_aspect", "contour_found"],
    "hu": [f"hu{i}" for i in range(1, 8)],
    "quality": ["sharpness", "mean_v", "std_l"],
}
FEATURE_NAMES: list[str] = [name for names in FEATURE_GROUPS.values() for name in names]


def crop_region(image_bgr: np.ndarray, bbox: BBox, pad_ratio: float, size: int) -> np.ndarray:
    """Cắt box (nới `pad_ratio` mỗi phía, kẹp trong ảnh) và đưa về size×size."""
    h, w = image_bgr.shape[:2]
    x1, y1, x2, y2 = bbox
    px, py = (x2 - x1) * pad_ratio, (y2 - y1) * pad_ratio
    x1, y1 = int(max(0, np.floor(x1 - px))), int(max(0, np.floor(y1 - py)))
    x2, y2 = int(min(w, np.ceil(x2 + px))), int(min(h, np.ceil(y2 + py)))
    crop = image_bgr[y1 : max(y2, y1 + 1), x1 : max(x2, x1 + 1)]
    return cv2.resize(crop, (size, size), interpolation=cv2.INTER_AREA if crop.shape[0] > size else cv2.INTER_CUBIC)


def color_masks(crop_bgr: np.ndarray, ranges: dict[str, list]) -> dict[str, np.ndarray]:
    """Mask nhị phân theo các dải HSV trong configs/verifier.yaml (đỏ có 2 dải vì H quấn quanh 0/180)."""
    hsv = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2HSV)
    masks = {}
    for name in COLORS:
        m = np.zeros(hsv.shape[:2], np.uint8)
        for lo, hi in ranges[name]:
            m |= cv2.inRange(hsv, np.array(lo, np.uint8), np.array(hi, np.uint8))
        masks[name] = m > 0
    return masks


def _shape_features(mask: np.ndarray, approx_eps: float) -> tuple[list[float], np.ndarray]:
    """Đặc trưng hình học + 7 Hu moments (log) của contour ngoài lớn nhất trong `mask`."""
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [c for c in contours if cv2.contourArea(c) > 0]
    if not contours:
        return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], np.zeros(7)
    c = max(contours, key=cv2.contourArea)
    area, perimeter = cv2.contourArea(c), cv2.arcLength(c, True)
    hull_area = cv2.contourArea(cv2.convexHull(c))
    _, _, bw, bh = cv2.boundingRect(c)
    n_vertices = len(cv2.approxPolyDP(c, approx_eps * perimeter, True))
    total = float(mask.size)
    shape = [
        4 * np.pi * area / (perimeter**2 + 1e-9),  # 1 = hình tròn hoàn hảo
        float(n_vertices),  # 3 = tam giác, 4 = chữ nhật, nhiều = tròn
        area / (hull_area + 1e-9),
        area / (bw * bh + 1e-9),
        area / total,
        bw / (bh + 1e-9),
        1.0,
    ]
    hu = cv2.HuMoments(cv2.moments(c)).ravel()
    return shape, -np.sign(hu) * np.log10(np.abs(hu) + 1e-30)


def region_features(image_bgr: np.ndarray, bbox: BBox, cfg: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """[CV] Đặc trưng thủ công của một vùng -> (vector theo FEATURE_NAMES, HOG thô chưa giảm chiều).

    cfg = configs/verifier.yaml. Màu tính trên toàn crop, vành ngoài (viền biển) và lõi; hình học + Hu trên contour lớn
    nhất của mask đỏ/xanh/vàng (không có màu biển thì dùng ngưỡng Otsu trên ảnh xám); HOG trên crop xám size×size.
    """
    from skimage.feature import hog

    f = cfg["features"]
    crop = crop_region(image_bgr, bbox, cfg["build"]["crop_pad_ratio"], f["crop_size"])
    size = crop.shape[0]
    yy, xx = np.mgrid[:size, :size]
    r = np.hypot(xx - (size - 1) / 2, yy - (size - 1) / 2) / (size / 2)
    ring, core = (r > 0.6) & (r <= 1.0), r <= 0.6  # vùng sau khi nới pad: viền biển rơi vào vành 0.6–1.0

    masks = color_masks(crop, f["color_ranges"])
    color = [float(m[region].mean()) for m in masks.values() for region in (np.ones_like(m), ring, core)]

    sign_mask = masks["red"] | masks["blue"] | masks["yellow"]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    if sign_mask.mean() < 0.05:
        _, otsu = cv2.threshold(gray, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        sign_mask = otsu.astype(bool)
    sign_mask = cv2.morphologyEx(sign_mask.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    shape, hu = _shape_features(sign_mask, f["approx_eps"])

    lab_l = cv2.cvtColor(crop, cv2.COLOR_BGR2LAB)[..., 0]
    quality = [
        float(cv2.Laplacian(gray, cv2.CV_64F).var()),
        float(cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)[..., 2].mean() / 255.0),
        float(lab_l.std() / 255.0),
    ]

    h = f["hog"]
    hog_raw = hog(
        cv2.resize(gray, (h["size"], h["size"]), interpolation=cv2.INTER_AREA),
        orientations=h["orientations"],
        pixels_per_cell=tuple(h["pixels_per_cell"]),
        cells_per_block=tuple(h["cells_per_block"]),
        feature_vector=True,
    )
    return np.array(color + shape + list(hu) + quality, dtype=np.float32), hog_raw.astype(np.float32)


@dataclass
class VerifierBundle:
    """Lưu chung một file joblib: mô hình đã hiệu chỉnh + PCA cho HOG + tên đặc trưng + ngưỡng."""

    model: Any
    hog_pca: Any
    feature_names: list[str]
    threshold: float = 0.5


SUPERCLASSES = ["prohibitory", "warning", "mandatory", "info", "other"]
CONTEXT = ["yolo_score", "yolo_cls", "superclass", "log_w", "log_h", "aspect", "rel_cx", "rel_cy"]


def label_candidates(pb: np.ndarray, pc: np.ndarray, ps: np.ndarray, gt: np.ndarray, gc: np.ndarray) -> list[str]:
    """Ghép tham lam theo điểm giảm dần: tp | sai_lop | trung | dinh_vi_kem | nen (IoU ≥ 0.5 cho tp / sai lớp)."""
    from .evaluation.metrics import iou_matrix

    out = ["nen"] * len(pb)
    if not len(gt) or not len(pb):
        return out
    iou = iou_matrix(pb, gt)
    used: set[int] = set()
    for k in np.argsort(-ps):
        same = [j for j in range(len(gt)) if gc[j] == pc[k] and iou[k, j] >= 0.5]
        free = [j for j in same if j not in used]
        if free:
            used.add(max(free, key=lambda j: iou[k, j]))
            out[k] = "tp"
        elif same:
            out[k] = "trung"
        elif iou[k].max() >= 0.5:
            out[k] = "sai_lop"
        elif iou[k].max() >= 0.1:
            out[k] = "dinh_vi_kem"
    return out


def candidate_row(image_bgr: np.ndarray, det: Detection, cfg: dict[str, Any]) -> tuple[dict[str, float], np.ndarray]:
    """Đặc trưng ngữ cảnh YOLO + đặc trưng vùng thủ công cho một hộp."""
    from .config import load_classes

    h, w = image_bgr.shape[:2]
    x1, y1, x2, y2 = det.bbox
    feats, hog_raw = region_features(image_bgr, det.bbox, cfg)
    row = {
        "yolo_score": det.score,
        "yolo_cls": det.class_id,
        "superclass": SUPERCLASSES.index(load_classes()[det.class_id].superclass),
        "log_w": float(np.log1p(x2 - x1)),
        "log_h": float(np.log1p(y2 - y1)),
        "aspect": float((x2 - x1) / (y2 - y1 + 1e-9)),
        "rel_cx": float((x1 + x2) / 2 / w),
        "rel_cy": float((y1 + y2) / 2 / h),
        **dict(zip(FEATURE_NAMES, feats.tolist())),
    }
    return row, hog_raw


def build_dataset(yolo_weights: Path, split_dir: Path, cfg: dict[str, Any], limit: int | None = None) -> pd.DataFrame:
    """Chạy YOLO trên split -> đặc trưng + nhãn; một dòng / box, cột `image` để chia fold theo ảnh.

    HOG thô nằm ở cột `hog` (mảng) để `train` fit PCA cùng mô hình.
    """
    from ultralytics import YOLO

    from .data.labels import list_images, read_labels

    model = YOLO(str(yolo_weights))
    images = list_images(split_dir)[:limit]
    rows = []
    for path in images:
        img = cv2.imread(str(path))
        h, w = img.shape[:2]
        r = model.predict(img, conf=cfg["build"]["proposal_conf"], iou=0.5, max_det=300, verbose=False)[0]
        labels = read_labels(path.parent.parent / "labels" / f"{path.stem}.txt")
        gt = np.array([b.to_xyxy(w, h) for b in labels]).reshape(-1, 4)
        gc = np.array([b.class_id for b in labels], int)
        pb, pc, ps = r.boxes.xyxy.cpu().numpy(), r.boxes.cls.cpu().numpy().astype(int), r.boxes.conf.cpu().numpy()
        outcome = label_candidates(pb, pc, ps, gt, gc)
        for k in range(len(pb)):
            row, hog_raw = candidate_row(img, Detection(tuple(map(float, pb[k])), int(pc[k]), float(ps[k])), cfg)
            rows.append(
                {"image": path.name, "outcome": outcome[k], "y": int(outcome[k] == "tp"), "hog": hog_raw, **row}
            )
    return pd.DataFrame(rows)


def _matrix(df: pd.DataFrame, pca) -> np.ndarray:
    return np.hstack([df[CONTEXT + FEATURE_NAMES].to_numpy(np.float32), pca.transform(np.stack(df.hog.to_numpy()))])


def train(df: pd.DataFrame, run_dir: Path, cfg: dict[str, Any]) -> dict[str, float]:
    """GroupKFold theo ảnh; so sánh lightgbm / logreg / rf (E3); lưu run_dir/verifier.joblib (mô hình cấu hình)."""
    import joblib
    import lightgbm as lgb
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.decomposition import PCA
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    m = cfg["model"]
    pca = PCA(cfg["features"]["hog"]["pca_components"], random_state=0).fit(np.stack(df.hog.to_numpy()))
    x, y = _matrix(df, pca), df.y.to_numpy()
    candidates = {
        "lightgbm": lambda: lgb.LGBMClassifier(**m["lightgbm"], random_state=0, verbose=-1),
        "logreg": lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, class_weight="balanced")),
        "rf": lambda: RandomForestClassifier(400, class_weight="balanced", n_jobs=-1, random_state=0),
    }
    folds = min(m.get("cv_folds", 5), df.image.nunique())
    metrics: dict[str, float] = {"n_samples": float(len(df)), "n_positive": float(y.sum())}
    for name, make in candidates.items():
        oof = np.zeros(len(y))
        for tr, te in GroupKFold(folds).split(x, y, groups=df.image):
            oof[te] = make().fit(x[tr], y[tr]).predict_proba(x[te])[:, 1]
        metrics[f"auc_{name}"] = float(roc_auc_score(y, oof))
    metrics["auc_yolo_score"] = float(roc_auc_score(y, df.yolo_score))
    chosen = candidates[m["type"]]()
    if m.get("calibration", "none") != "none":
        chosen = CalibratedClassifierCV(chosen, method=m["calibration"], cv=folds)
    chosen.fit(x, y)
    run_dir.mkdir(parents=True, exist_ok=True)
    bundle = VerifierBundle(chosen, pca, CONTEXT + FEATURE_NAMES, threshold=0.5)
    joblib.dump(bundle, run_dir / "verifier.joblib")
    return metrics


class Verifier:
    def __init__(self, weights: Path, threshold: float | None = None):
        import joblib

        self.bundle: VerifierBundle = joblib.load(weights)
        self.threshold = self.bundle.threshold if threshold is None else threshold

    def verify(self, image_bgr: np.ndarray, detections: list[Detection]) -> list[Detection]:
        """score = xác suất đã hiệu chỉnh; verified = score ≥ threshold."""
        from dataclasses import replace

        if not detections:
            return []
        rows, hogs = zip(*(candidate_row(image_bgr, d, _feature_cfg()) for d in detections))
        df = pd.DataFrame(rows).assign(hog=list(hogs))
        prob = self.bundle.model.predict_proba(_matrix(df, self.bundle.hog_pca))[:, 1]
        return [replace(d, score=float(p), verified=bool(p >= self.threshold)) for d, p in zip(detections, prob)]


@lru_cache(maxsize=1)
def _feature_cfg() -> dict[str, Any]:
    """configs/verifier.yaml — cấu hình đặc trưng phải khớp lúc train."""
    from .config import load_config

    return load_config("verifier")
