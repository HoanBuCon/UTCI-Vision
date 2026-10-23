# ADR-004: Detector YOLO11 — fine-tune từ trọng số pretrained

- **Trạng thái:** Accepted (nhóm duyệt 2026-10-22; bổ sung "fine-tune, không retrain" cùng ngày)
- **Người đề xuất:** TV1, TV3

## Bối cảnh
Ultralytics hỗ trợ nhiều đời YOLO với cùng API; nhóm chọn tập trung vào một mô hình. Dataset chỉ ~5,4 nghìn ảnh / 13,5 nghìn box —
quá ít để train detector từ đầu, và GPU của nhóm hạn chế (laptop 8 GB, quota Colab/Kaggle).

## Quyết định
- Dùng **YOLO11**, mặc định `yolo11s.pt`, `imgsz` 960, `fliplr=0` (lật ngang làm đổi nghĩa biển rẽ trái/phải).
- **Fine-tune, không train lại từ đầu:** khởi tạo từ trọng số **pretrained COCO** (`yolo11s.pt`) hoặc từ checkpoint của nhóm (`INIT_WEIGHTS`,
  vd. fine-tune tiếp khi có dữ liệu v2); AdamW `lr0=0.001`, cosine LR, warmup 3 epoch, ~80 epoch, early stopping.
  Không dùng file kiến trúc `.yaml` (khởi tạo ngẫu nhiên).
- `freeze`: 0 (fine-tune toàn bộ) mặc định; so sánh với 10 (đóng băng backbone) ở E3 cùng `n` vs `s`, `imgsz` 640 vs 960.
- `RESUME` chỉ để chạy tiếp một lần fine-tune bị ngắt (Colab), không phải lần mới.
- Không dùng YOLOv8/v12/v26 và các repo YOLO khác.

## Hệ quả
- (+) Hội tụ nhanh hơn, cần ít dữ liệu và GPU hơn; tận dụng đặc trưng học từ COCO.
- (+) Cùng họ mô hình với repo tham khảo; giấy phép AGPL-3.0 (ghi rõ trong báo cáo).
- (−) Báo cáo không có phần so sánh giữa các đời YOLO.
