# Trọng số mô hình

Trọng số **không** commit vào git. Bản đang dùng nằm ở `models/current/` (pipeline, API và Docker đọc thư mục này).
Mỗi lần fine-tune được nhập bằng `python scripts/import_run.py <thư-mục-run> --promote` (copy vào `models/<run_id>/` và `models/current/`, ghi `experiments/registry.csv`).
Thư mục run đầy đủ (biểu đồ, `results.csv`, checkpoint) để ở `runs_out/<run_id>/` (cũng không commit).

Máy mới: tải thư mục run từ Drive về `runs_out/` rồi chạy
`python scripts/import_run.py runs_out/20261029-1030_yolo11s_960 --promote --exp BASELINE`.

Các script đánh giá (`analyze_run.py`, `verifier_feasibility.py`, `compare_traditional_dl.py`, `enhance_robustness.py`)
mặc định dùng `configs/pipeline.yaml > detector.weights` = `models/current/yolo11.pt`; truyền đường dẫn `.pt` để đánh giá run khác.

| Thành phần | File | run_id | Nền tảng | Metric chính | Link Drive |
|---|---|---|---|---|---|
| YOLO11s (fine-tune từ pretrained COCO, imgsz 960, 80 epoch) | `yolo11.pt` (19 MB) | `20261029-1030_yolo11s_960` | Colab, Tesla T4 | test mAP@50 0,905 · mAP@50:95 0,684 ([đánh giá](danh_gia/S1_baseline_yolo11s_960.md)) | `MyDrive/UTCI_VISION/runs/20261029-1030_yolo11s_960/` |
| Bộ xác minh LightGBM (tuỳ chọn, mặc định tắt — T1; API vẫn nạp để web bật theo từng request) | `verifier.joblib` (7 MB) | `scripts/fit_verifier.py` | local | OOF AUC 0,945 | — |
| Bộ phân loại CV truyền thống HOG + histogram HSV → SVM RBF, 27 lớp + lớp nền (trang Demo CV, So sánh) | `hog_svm.joblib` (33 MB) | `scripts/train_hog_svm.py` (C = 10, ~5 phút CPU) | local | val: accuracy biển 0,880 · nhận đúng nền 0,971 | — |
| VietOCR (đọc số + chữ) | `models/vietocr/vgg_transformer.pth` (152 MB) + `vgg_transformer.yml` | pretrained | — | Định tính (không có nhãn chữ — C-08) | tải từ vocr.vn lần đầu; chép sang máy khác để chạy offline |

VietOCR: lần chạy đầu tự tải trọng số từ vocr.vn; để chạy offline (Docker, máy demo) chép `vgg_transformer.pth` + `vgg_transformer.yml`
vào `models/vietocr/` — `configs/ocr.yaml > reader` trỏ tới hai file này.

Ảnh mẫu cho web (`configs/samples.yaml`) lấy từ `dataset/processed/v1/test/images` — Docker mount thư mục này chỉ đọc;
thiếu thư mục thì web chỉ cho tải ảnh lên. Số liệu tĩnh của web (`web/public/data/*.json`) sinh bằng `python scripts/export_web_data.py`.
