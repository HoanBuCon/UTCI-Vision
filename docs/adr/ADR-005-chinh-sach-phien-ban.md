# ADR-005: Không khoá torch/CUDA — chỉ khoá thư viện dùng chung

- **Trạng thái:** Accepted (nhóm duyệt 2026-10-22)

## Bối cảnh
Mỗi thành viên có GPU/driver khác nhau (hoặc không có GPU); Colab/Kaggle đã cài sẵn torch theo GPU của chúng.
Khoá một bản torch + CUDA cho cả nhóm sẽ làm hỏng môi trường của một số người.

## Quyết định
1. `requirements.txt` khoá **phiên bản chính xác** các thư viện dùng chung và **không chứa** torch, torchvision, `nvidia-*`, triton.
2. Mỗi người tự cài torch theo hướng dẫn pytorch.org; yêu cầu tối thiểu `torch >= 2.4` (Ultralytics loại trừ 2.4.0 trên Windows).
3. Thứ tự: torch → `pip install -r requirements.txt` → `pip install --no-deps vietocr==0.3.13`
   (VietOCR khoá cứng `imgaug==0.4.0`, `pillow==10.2.0`, `albumentations==1.4.2`… không hợp numpy 2; phụ thuộc thật sự cần cho suy luận đã nằm trong requirements).
4. `make check-env` in phiên bản torch/CUDA/GPU và cảnh báo khi dưới mức tối thiểu; `make freeze` sinh `requirements.lock` đã lọc gói GPU.
5. Mọi lần huấn luyện ghi môi trường (torch, CUDA, GPU, nền tảng) vào `run_record.json` → `experiments/registry.csv`.
6. Docker là nơi duy nhất cố định torch: image CPU dùng torch CPU; image GPU dựa trên `pytorch/pytorch:2.14.1-cuda12.6-cudnn9-runtime`.

## Hệ quả
- (+) Ai cũng cài được trên máy mình; notebook cloud dùng torch có sẵn.
- (−) Kết quả có thể lệch nhẹ giữa các máy → số liệu chính thức trong báo cáo lấy từ một nền tảng cố định, ghi rõ môi trường.
