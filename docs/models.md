# Trọng số mô hình

Trọng số **không** commit vào git. Bản đang dùng nằm ở `models/current/` (pipeline, API và Docker đọc thư mục này).
Mỗi lần fine-tune được nhập bằng `python scripts/import_run.py <thư-mục-run> --promote` (copy vào `models/<run_id>/` và `models/current/`, ghi `experiments/registry.csv`).

| Thành phần | File | run_id | Nền tảng | Metric chính | Link Drive |
|---|---|---|---|---|---|
| YOLO11 (fine-tune từ pretrained COCO) | `yolo11.pt` | — | — | — | — |
| Bộ xác minh LightGBM | `verifier.joblib` | — | — | — | — |
| VietOCR (đọc số + chữ) | pretrained `vgg_transformer` | — | — | — | (bản sao dự phòng) |
