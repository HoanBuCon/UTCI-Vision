# ADR-001: Một hệ thống — YOLO11 làm lõi, CV/ML/OCR bổ trợ theo track

- **Trạng thái:** Accepted (nhóm duyệt 2026-10-22)
- **Người đề xuất:** TV1
- **Thay thế:** bản nháp "3 chế độ Classic/Deep/Hybrid tách rời" và bản nháp "YOLO + CNN phân loại riêng + LightGBM" — đều bị loại

## Bối cảnh
Đề tài yêu cầu một **hệ thống** nhận diện biển báo có ứng dụng ML, DL và CV. Nhóm loại hướng tách 3 pipeline để so sánh
(không phải một sản phẩm) và loại CNN phân loại riêng (trùng việc với đầu phân loại của YOLO, tốn thời gian chạy và công bảo trì).
Yêu cầu bổ sung: chạy realtime trên web, đọc được chữ tiếng Việt trên biển và biển phụ.

## Quyết định
- **YOLO11** phát hiện + phân loại 32 lớp, chạy mỗi frame.
- **CV mỗi frame (rẻ):** đánh giá chất lượng → tăng cường chỉ khi cần; tracking Kalman + IoU, bỏ phiếu nhãn theo track.
- **Theo track, bất đồng bộ (đắt hơn, chạy ít lần):**
  - CV đặc trưng màu/hình dạng → **LightGBM** xác minh + hiệu chỉnh độ tin cậy.
  - CV chọn frame tốt nhất, cắt vùng số / vùng chữ, tìm biển phụ → **VietOCR** đọc cả số và chữ → regex hợp lệ hoá số (km/h, m, T) + từ điển sửa chữ.
  - (2026-10-23) Bỏ SVM chữ số riêng: VietOCR đọc số đúng trong thử nghiệm, bớt một mô hình phải huấn luyện và một tập dữ liệu chữ số.
- Mỗi khâu có cờ bật/tắt trong `configs/pipeline.yaml` (phục vụ ablation và đường lui hiệu năng).
- Mã nguồn tổ chức theo khâu: `enhance.py` [CV], `detector.py` [DL], `tracking.py` [CV], `verifier.py` [CV+ML],
  `ocr.py` [CV+DL], điều phối ở `pipeline.py` (2026-10-23: bỏ thư mục `cv/`, `ml/`, `dl/` chia theo kỹ thuật).

## Hệ quả
- (+) Mỗi kỹ thuật làm việc YOLO không làm được: ảnh tối, dương tính giả, đọc số, đọc chữ, ổn định video.
- (+) Chỉ YOLO nằm trên đường găng realtime; các khâu khác được chia đều theo track.
- (+) Ablation E2 đo trực tiếp đóng góp của từng khâu.
- (−) Thứ tự huấn luyện: YOLO trước, rồi bộ xác minh (cần dự đoán của YOLO trên val).
- (−) OCR phụ thuộc kích thước biển; biển xa sẽ không có chữ.
- (−) Thành phần ML chính duy nhất là bộ xác minh LightGBM — giữ ở mức Must và phải có số liệu ablation chứng minh đóng góp.
