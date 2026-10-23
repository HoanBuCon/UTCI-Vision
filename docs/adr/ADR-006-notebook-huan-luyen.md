# ADR-006: Fine-tune qua 3 notebook Local / Colab / Kaggle sinh từ một template

- **Trạng thái:** Accepted (nhóm duyệt 2026-10-22)

## Bối cảnh
Thành viên fine-tune ở nhiều nơi (GPU cá nhân, Google Colab, Kaggle). Mọi việc không cần GPU nên chạy bằng mã nguồn local để dễ review và kiểm thử.

## Quyết định
- **Fine-tune / fit** (YOLO11 từ pretrained, bộ xác minh LightGBM; tuỳ chọn export ONNX) chỉ chạy trong
  `notebooks/train/train_{local,colab,kaggle}.ipynb`. Repo được `git clone` từ https://github.com/HoanBuCon/UTCI-Vision trên Colab/Kaggle.
- Ba notebook **sinh tự động** từ `notebooks/train/_template.py` bằng `python scripts/build_notebooks.py`; ô gắn thẻ `[local]`, `[colab]`, `[kaggle]`
  chỉ có trong notebook tương ứng. Không sửa tay file `.ipynb` (pre-commit, CI và test kiểm tra).
- Notebook chỉ là lớp vỏ: logic nằm ở `utci_vision.detector.finetune`, `utci_vision.verifier`, `utci_vision.training`; tham số ở `configs/`.
- Mỗi lần chạy sinh `<run_id>/` (trọng số + `run_record.json` có môi trường torch/CUDA/GPU); ở local `python scripts/import_run.py … --promote`
  nhập về `models/` và ghi registry chính thức.
- Mọi việc không huấn luyện (dữ liệu, đánh giá test, API, web, Docker) chạy bằng `scripts/` ở local; `make` chỉ dùng cho DevOps (ADR-007).
- Chế độ `SMOKE=True` để kiểm tra mỗi nền tảng chạy hết các ô trong vài phút.

## Hệ quả
- (+) Ba nền tảng luôn đồng bộ; review qua `.py` thay vì JSON notebook.
- (−) Phải chạy `python scripts/build_notebooks.py` sau mỗi lần sửa template.
