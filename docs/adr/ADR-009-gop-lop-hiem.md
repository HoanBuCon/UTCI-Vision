# ADR-009: Gộp 6 lớp hiếm vào lớp "Biển báo khác" (32 → 27 lớp)

- **Trạng thái:** Accepted · thay mục 3 của ADR-002 (TBD-1 chốt sớm, không chờ Review S3)
- **Người đề xuất:** TV1 · **Ngày:** 2026-10-29

## Bối cảnh
Thống kê trên `processed/v1` (sau lọc 67 ảnh, chia lại theo cụm gần trùng): 13 476 box, lớp nhiều nhất 1 705,
ít nhất 31 (lệch 55×). Do ảnh trích từ video, số box không phản ánh lượng dữ liệu thật — đếm **cụm cảnh độc lập**
(pHash, Hamming ≤ 6) cho từng lớp:

| Lớp gốc | Tên | Box | Cụm cảnh | Cụm ở test |
|---|---|---|---|---|
| 11 | Cấm rẽ trái và phải | 91 | 54 | 9 |
| 5 | Cấm đi thẳng và rẽ phải | 77 | 43 | 4 |
| 12 | Cấm rẽ trái và quay đầu xe | 232 | 38 | 1 |
| 27 | Kiểm tra | 56 | 36 | 8 |
| 25 | Giới hạn trọng lượng | 31 | 31 | 5 |
| 22 | Giao nhau với đường sắt có rào chắn | 48 | 25 | 7 |

26 lớp còn lại có 63–998 cụm. Nhóm trên quá ít cảnh để học ổn định, AP theo lớp không đáng tin (test 1–9 cụm),
và một số dễ nhầm với lớp phổ biến cùng dạng (12 ↔ 8, 10; 25 ↔ 24, 23; 5, 11 ↔ 9, 10).

## Quyết định
1. Chốt tập nhãn **trước khi** fine-tune baseline, theo tiêu chí đặt trước: lớp **< 60 cụm cảnh độc lập** bị gộp.
2. 6 lớp trên **gộp** vào lớp mới `Biển báo khác` (id 26, siêu lớp `other`) — không xoá ảnh, không bỏ nhãn:
   - Xoá ảnh chứa các lớp này mất 431 ảnh (8%), kéo theo hàng trăm box của lớp tốt (6, 4, 29, 7…).
   - Bỏ nhãn nhưng giữ ảnh dạy mô hình coi biển là nền → hại các lớp cùng dạng.
3. Ánh xạ nằm duy nhất ở `configs/classes.yaml > raw_ids` (id lớp gốc Roboflow → id mô hình);
   `scripts/data.py split` đổi id khi dựng `processed/<version>`; `audit` vẫn chạy trên id gốc.
4. 26 lớp giữ lại được đánh số lại liên tục 0–25 theo thứ tự cũ.

## Hệ quả
- (+) Mọi lớp của mô hình có ≥ 63 cụm cảnh; không mất ảnh/box nào (13 476 box, 535 box ở lớp gộp).
- (+) Đảo ngược được: tách một lớp khỏi `raw_ids` của `Biển báo khác` khi đủ dữ liệu (dataset v2+), dựng lại, fine-tune tiếp.
- (−) Không còn đọc số tải trọng (lớp 25, đơn vị T) và chữ "KIỂM TRA" (lớp 27) — hiển thị "Biển báo khác".
- (−) Lớp gộp đa dạng về hình dạng (tròn đỏ, tam giác) → có thể khó học; theo dõi AP và confusion matrix ở baseline.
- (−) Số liệu không so sánh trực tiếp được với kết quả 32 lớp của repo tham khảo.
