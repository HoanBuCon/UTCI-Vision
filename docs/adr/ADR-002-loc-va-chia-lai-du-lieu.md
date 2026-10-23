# ADR-002: Lọc và chia lại dữ liệu theo cụm gần trùng

- **Trạng thái:** Proposed (TV5 chốt ở Sprint 1 Review, áp dụng Sprint 2)
- **Người đề xuất:** TV1, TV5 · **Ngày:** 2026-10-22

## Bối cảnh
Kết quả `python scripts/data.py audit --dedup` trên dataset gốc (5 453 ảnh, 13 478 box):
- 6/32 lớp không có mẫu trong test gốc; 2 lớp ("Kiểm tra", "Cấm đi thẳng và rẽ phải") không có trong cả valid lẫn test.
- Phân bố lớp giữa các tập rất lệch (vd. "Cấm rẽ trái và phải": train 4 / valid 87).
- Test gốc 100% ảnh 1622×626; train chủ yếu 960×540.
- 530 cụm ảnh gần trùng (pHash, Hamming ≤ 6) chứa 2 033 ảnh; 4 cụm nằm vắt qua nhiều tập.

## Quyết định
1. Gộp 3 tập gốc → loại ảnh trong `reports/data/excluded.txt` (TV5 duyệt) → chia lại 70/15/15
   bằng iterative stratification theo **lớp + độ phân giải**, đơn vị chia là **cụm gần trùng**.
2. Seed cố định 42; kết quả là `dataset/processed/v1` + `manifest.csv` + `split_report.csv`.
3. Lớp < 50 mẫu (Giới hạn trọng lượng 31, Giao nhau với đường sắt 48): **giữ lại** ở v1, báo cáo riêng;
   xem xét gộp/loại sau khi có AP theo lớp ở Sprint 3 (TBD-1).
4. Mọi phép đo trong báo cáo dùng `processed/v1`. Baseline Sprint 1 trên dữ liệu gốc chỉ để tham chiếu.
5. Vai trò từng tập trong pipeline thống nhất (ADR-001): **train** → YOLO11; **val** → chọn tham số + huấn luyện
   bộ xác minh LightGBM trên dự đoán của YOLO (stacking — YOLO chưa thấy val); **test** → chỉ đánh giá toàn hệ thống.

## Hệ quả
- (+) Đánh giá được cả 32 lớp; không rò rỉ giữa các tập.
- (−) Số liệu không so sánh trực tiếp được với repo tham khảo (khác split) — ghi rõ trong báo cáo.
