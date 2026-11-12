# Đánh giá hệ thống đầy đủ — E1, E2, E4, T3 (Sprint 3)

- **Ngày:** 12/11/2026 · **Trọng số:** YOLO11s `20261029-1030_yolo11s_960` (`models/current`) · bộ xác minh `models/current/verifier.joblib`
  (fit trên val bằng `scripts/fit_verifier.py`) · **Dữ liệu:** test `processed/v1` (826 ảnh, 2 017 biển) · **Thiết bị:** RTX 4060 Laptop
- **Tái lập:** `python scripts/evaluate.py detect [--ablation] [--degrade dark]` · `python scripts/evaluate.py small`
- **Chỉ số chính:** P / R / F1 **tại điểm vận hành của pipeline** (conf 0,25; đúng lớp, IoU ≥ 0,5). mAP ở đây tính trên *đầu ra*
  pipeline (đã cắt ở ngưỡng hiển thị) nên thấp hơn mAP của Ultralytics — chỉ dùng để so giữa các cấu hình.
- Bảng CSV: [`S3_he_thong/`](S3_he_thong/) · registry: `E1-20261112-154019`, `E2-20261112-153307`, `E4-20261112-153536`,
  `E4-20261112-154103`, `T3-20261112-153705`.

## Cấu hình mặc định sau đánh giá (E1)

`configs/pipeline.yaml`: tăng cường thích nghi **bật**, YOLO11s **suy luận imgsz 1280** (theo T3), bộ xác minh **tắt**, OCR bật.

| Tập | Precision | Recall | F1 | Recall < 16 px | 16–32 | 32–64 | ≥ 64 | ms / ảnh |
|---|---|---|---|---|---|---|---|---|
| Test | 0,862 | **0,917** | **0,889** | **0,734** | 0,941 | 0,976 | 0,958 | 22,5 |
| Test làm tối (γ 2,5) | 0,884 | 0,866 | 0,875 | 0,662 | 0,860 | 0,948 | 0,958 | 34,8 |

So với baseline S1 (imgsz 960, không tăng cường): recall 0,893 → 0,917, recall biển < 16 px 0,634 → 0,734 (**đạt NFR-ACC-06 ≥ 0,70**),
precision giữ nguyên.

## E2 — Đóng góp từng khâu (ablation, imgsz 960)

| Cấu hình | Test thường: P / R / F1 | Test làm tối γ 2,5: P / R / F1 |
|---|---|---|
| YOLO thuần | 0,861 / 0,893 / 0,877 | 0,905 / 0,813 / 0,856 |
| + tăng cường thích nghi [CV] | 0,860 / 0,893 / 0,876 | 0,885 / **0,854** / **0,869** |
| + bộ xác minh [CV + ML], ngưỡng 0,5 | **0,946** / 0,841 / 0,891 | **0,960** / 0,796 / 0,871 |

("full" trùng "+ bộ xác minh" vì theo vết không áp dụng cho ảnh tĩnh.)

- **Tăng cường thích nghi:** không đổi trên ảnh thường (chỉ kích hoạt ở ~3% ảnh), **+0,041 recall** trên ảnh tối — khớp T4.
- **Bộ xác minh:** precision +0,085 nhưng recall −0,052 (vượt giới hạn −0,03), F1 +0,014. Đây là dịch chuyển điểm vận hành;
  T1 đã cho thấy ở **cùng** recall bộ xác minh không hơn điểm YOLO. Giữ **mặc định tắt**; bật khi ưu tiên ít báo nhầm.

## T3 — Biển nhỏ không cần train lại

| Cách suy luận | Precision | Recall | Recall < 16 px | ms / ảnh |
|---|---|---|---|---|
| imgsz 960 (như lúc train) | 0,861 | 0,893 | 0,634 | 18,6 |
| **imgsz 1280** | **0,861** | **0,917** | **0,737** | 21,4 |
| imgsz 960 + cắt ô 640 (kiểu SAHI) | 0,749 | 0,932 | 0,784 | 46,5 |

Suy luận ở 1280 với trọng số train ở 960 tăng recall biển nhỏ 10 điểm mà **không mất precision**, chậm thêm ~15% →
chọn làm mặc định. Cắt ô cho recall cao nhất nhưng precision giảm 0,11 và chậm 2,5× → chỉ nên dùng cho ảnh tĩnh độ phân giải
cao khi người dùng cần (FR-PIPE-15, `Detector.detect_tiled`). Recall biển ≥ 64 px giảm nhẹ ở 1280 (0,976 → 0,958).

## Chưa đo được
- **E6 (độ ổn định nhãn ± theo vết):** cần video đường phố thật (FR-DATA-10); công cụ `evaluate.py flicker --source <video>` đã sẵn.
  Video ghép từ ảnh test không hợp lệ cho E6 (chuyển cảnh mỗi vài frame).
- **E5 (đọc số / chữ):** không có nhãn (C-08) — chỉ định tính: trên ảnh test, đọc đúng "40 km/h", "60 km/h", "2,0 m"; chữ trên
  biển nhỏ thường bị loại do độ tin cậy VietOCR < 0,75.
- **FPS end-to-end qua web:** WebSocket trên **CPU** đạt 9,3 FPS (YOLO 960, ~90 ms/khung); chưa đo lại trên GPU qua web.

## Hạn chế
Một lần chạy; bộ xác minh fit trên val (cùng tập đã dùng chọn epoch YOLO); E2 / E4-ablation đo ở imgsz 960 (trước khi đổi
mặc định sang 1280), E1 ở 1280; ảnh tối là giả lập.
