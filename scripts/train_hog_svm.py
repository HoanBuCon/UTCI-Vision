"""Huấn luyện bộ phân loại CV truyền thống: HOG + histogram HSV -> SVM (RBF), 27 lớp biển + lớp "nền". Phụ trách: TV2.

    python scripts/train_hog_svm.py [--out models/current/hog_svm.joblib] [--max-background 6000]

- Mẫu biển: crop biển thật (GT) của train (fit) và val (chọn C).
- Mẫu "nền": vùng ứng viên của bộ phát hiện màu + hình dạng (traditional.color_shape_candidates) trên ảnh train / val
  **không** trùng biển thật nào (IoU < 0.1) — để pipeline truyền thống loại được biển quảng cáo, mái tôn, đèn...
- Nhãn nền = số lớp (27). Kết quả: accuracy val (biển), tỉ lệ nhận đúng nền.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import cv2
import numpy as np

from utci_vision.config import load_classes, load_config, resolve
from utci_vision.data.labels import list_images, read_labels
from utci_vision.evaluation.metrics import iou_matrix
from utci_vision.traditional import ClassicClassifier, classic_features, color_shape_candidates, padded_crop


def collect(split: str, color_ranges: dict, det_cfg: dict, background_label: int, max_bg: int, seed: int = 0):
    root = resolve(load_config("data")["processed_dir"]) / split
    crops, labels, bg = [], [], []
    for path in list_images(root):
        img = cv2.imread(str(path))
        h, w = img.shape[:2]
        gts = read_labels(path.parent.parent / "labels" / f"{path.stem}.txt")
        boxes = np.array([b.to_xyxy(w, h) for b in gts]).reshape(-1, 4)
        for b, box in zip(gts, boxes):
            c = padded_crop(img, tuple(box))
            if c.size:
                crops.append(c)
                labels.append(b.class_id)
        cands, _ = color_shape_candidates(img, color_ranges, det_cfg)
        if cands:
            cb = np.array([c.bbox for c in cands])
            overlap = iou_matrix(cb, boxes).max(1) if len(boxes) else np.zeros(len(cb))
            bg += [padded_crop(img, tuple(b)) for b, o in zip(cb, overlap) if o < 0.1]
    rng = np.random.default_rng(seed)
    bg = [bg[i] for i in rng.permutation(len(bg))[:max_bg] if bg[i].size]
    return crops + bg, np.array(labels + [background_label] * len(bg))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=Path("models/current/hog_svm.joblib"))
    parser.add_argument("--max-background", type=int, default=6000)
    args = parser.parse_args()
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC

    ver = load_config("verifier")["features"]
    det_cfg = load_config("traditional")["detect"]
    bg_label = len(load_classes())
    t0 = time.time()
    x_tr_crops, y_tr = collect("train", ver["color_ranges"], det_cfg, bg_label, args.max_background)
    x_val_crops, y_val = collect("val", ver["color_ranges"], det_cfg, bg_label, args.max_background // 4)
    x_tr, x_val = classic_features(x_tr_crops, ver["hog"]), classic_features(x_val_crops, ver["hog"])
    print(
        f"train {len(y_tr)} (nền {int((y_tr == bg_label).sum())}) · val {len(y_val)} (nền {int((y_val == bg_label).sum())}) · {time.time() - t0:.0f} s"
    )

    best = None
    for c in (3.0, 10.0):
        m = make_pipeline(StandardScaler(), SVC(C=c, kernel="rbf", gamma="scale", class_weight="balanced")).fit(
            x_tr, y_tr
        )
        pred = m.predict(x_val)
        sign = y_val != bg_label
        acc_sign, acc_bg = float((pred[sign] == y_val[sign]).mean()), float((pred[~sign] == bg_label).mean())
        print(f"  C={c:g}: accuracy biển (val) {acc_sign:.3f} · nhận đúng nền {acc_bg:.3f}")
        if best is None or acc_sign + acc_bg > best[0]:
            best = (acc_sign + acc_bg, c, acc_sign, acc_bg)
    _, c, acc_sign, acc_bg = best
    # mô hình cuối có xác suất (Platt) để hiển thị độ tin cậy trên web
    model = make_pipeline(
        StandardScaler(),
        SVC(C=c, kernel="rbf", gamma="scale", class_weight="balanced", probability=True, random_state=0),
    ).fit(x_tr, y_tr)
    clf = ClassicClassifier(
        model, ver["hog"], {"C": c, "val_accuracy_sign": acc_sign, "val_accuracy_background": acc_bg}
    )
    out = resolve(args.out)
    clf.save(out)
    print(json.dumps(clf.metrics, indent=2), f"\n-> {out} · {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
