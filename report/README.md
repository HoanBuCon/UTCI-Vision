# Báo cáo

Phụ trách: **TV4** (TV2 hỗ trợ). Định dạng Word hoặc LaTeX — chốt ở Planning Sprint 1 (TBD-2).

```
report/
├── sprint/            # Báo cáo mốc: sprint1.md ... sprint6.md (dùng mẫu bên dưới)
├── final/             # Báo cáo cuối kỳ (main.tex hoặc .docx)
├── figures/           # Hình xuất từ notebook/scripts (PNG/SVG, đặt tên figNN_mo-ta.png)
└── slides/            # Slide thuyết trình
```

## Mẫu báo cáo mốc sprint (1–2 trang)

```markdown
# Báo cáo Sprint N — <tên sprint> (dd/mm – dd/mm)

## 1. Mục tiêu sprint
## 2. Kết quả đạt được (theo thẻ Trello, đánh dấu Done / Chưa xong)
## 3. Số liệu chính (trích experiments/registry.csv: run_id, metric)
## 4. Hình minh hoạ (1–3 hình)
## 5. Vấn đề & rủi ro, quyết định đã chốt (ADR / CHANGE-REQ)
## 6. Kế hoạch sprint tiếp theo
## 7. Đóng góp từng thành viên (TV1..TV5)
```

## Dàn ý báo cáo cuối kỳ (đề xuất)

1. Giới thiệu: bài toán, ý nghĩa, mục tiêu, phạm vi
2. Cơ sở lý thuyết: không gian màu, CLAHE/gamma; hình thái học, contour, Hu moments, HOG; Kalman & ghép IoU; YOLO11 & transfer learning / fine-tune; OCR (VietOCR, transformer); Gradient Boosting (LightGBM), stacking, hiệu chỉnh xác suất; metric (IoU, mAP, F1, CER)
3. Dữ liệu: nguồn, EDA, vấn đề phát hiện, quy trình lọc & chia lại (Data card)
4. Phương pháp: pipeline thống nhất theo luồng xử lý (CV → DL → tracking → tác vụ theo track: xác minh ML, đọc số, OCR), web + Docker
5. Thực nghiệm: môi trường (3 nền tảng fine-tune), E1–E7, ablation từng khâu, phân tích lỗi
6. Ứng dụng demo
7. Kết luận & hướng phát triển
8. Tài liệu tham khảo · Phụ lục (phân công, kế hoạch sprint)
