# Sprint 1 — Khởi động & nền tảng (23/10 – 30/10/2026) · Bài KT 1

> Cập nhật: thứ Năm 29/10/2026. Sprint kết thúc **sáng thứ Sáu 30/10** (Review → Retro → Planning S2).
> Nguồn: Trello (đọc ngày 29/10), GitHub `HoanBuCon/UTCI-Vision`, sản phẩm TV5 tại `H:\Downloads\dataset_traffic_sigh`.

## 1. Mục tiêu sprint (nhắc lại)

Cả 5 người chạy được môi trường; dữ liệu được audit + duyệt; 3 notebook chạy SMOKE; có fine-tune baseline YOLO11s
và benchmark FPS; khung API + web + Docker chạy được; chốt schema JSON; khung báo cáo + Chương 1 cho **Bài KT 1**.

## 2. Tình trạng tại 29/10

| # | Thẻ | Người | Điểm | Trạng thái | Ghi chú |
|---|---|---|---|---|---|
| 1 | Sprint 1 Planning & Kickoff | ALL | 1 | ✅ Xong | |
| 2 | Đưa khung mã nguồn lên repo + CI | TV1 | 3 | ✅ Xong | PR #1 đã merge vào `develop` |
| 3 | Workshop phương án + chốt schema JSON API | TV1 | 2 | 🏗️ Đang làm | Chưa chốt schema |
| 4 | Smoke test notebook trên Kaggle | TV1 | 1 | ⬜ Chưa làm | |
| 5 | Hiện thực Detector + validate | TV3 | 3 | ⬜ Chưa làm | **Chặn** thẻ 13 (benchmark) |
| 6 | 3 notebook fine-tune: SMOKE local + hướng dẫn | TV3 | 3 | ⬜ Chưa làm | Có hoạt động 29/10 |
| 7 | Fine-tune baseline YOLO11s trên dữ liệu gốc | TV3 | 3 | ⬜ Chưa làm | |
| 8 | Khung API + web + Docker chạy được | TV3 | 2 | ⬜ Chưa làm | Mã đã có trong repo, chỉ cần chạy + xác nhận |
| 9 | Cài môi trường + khung frontend dev | TV2 | 2 | ⬜ Chưa làm | |
| 10 | Spike CV: chất lượng & tăng cường ảnh | TV2 | 3 | ⬜ Chưa làm | |
| 11 | Audit, EDA & duyệt dữ liệu | TV5 | 5 | ✅ Xong | Đã kiểm tra, xem §3 |
| 12 | Xác nhận classes.yaml | TV5 | 2 | ✅ Xong | Chưa đưa vào repo |
| 13 | Smoke test Colab + benchmark FPS mốc S1 | TV5 | 3 | 🏗️ Đang làm | Bị chặn bởi thẻ 5 |
| 14 | Khung báo cáo & Chương 1 | TV4 | 5 | ⬜ Chưa làm | **Cần cho Bài KT 1** |
| 15 | Báo cáo mốc S1 | TV4 | 1 | ⬜ Chưa làm | **Cần cho Bài KT 1** |
| 16 | Sprint 1 Review & Retro | ALL | 1 | ⬜ 30/10 | |

**Tiến độ: 4/16 thẻ xong, 11/40 điểm (28%).** TV5 xong toàn bộ phần chính; TV2, TV3, TV4 chưa bắt đầu thẻ nào.

## 3. Kiểm tra sản phẩm TV5

### 3.1 Kết luận: **Đạt — vượt yêu cầu** cho thẻ 11 và 12

| Yêu cầu trên thẻ | Kết quả | Đánh giá |
|---|---|---|
| Biểu đồ phân bố lớp / kích thước / độ phân giải | 6 hình (PNG 300 dpi + PDF cho LaTeX), `summary.md`, `class_stats.csv` | ✅ Số liệu khớp với audit độc lập (5 453 ảnh, 13 478 box, mất cân bằng 55×) |
| Duyệt 118 ảnh không nhãn + mẫu cụm gần trùng | `review_unlabeled.csv`: 53 nền thật · **55 thiếu nhãn** · 10 loại; `review_dups.csv`: 4 cụm vắt train↔valid, 0 chạm test | ✅ Đã kiểm: 67 đường dẫn tồn tại, 55 ảnh đúng là không có nhãn |
| Contact-sheet theo lớp | 32 sheet + `contact_sheet_issues.csv` (23 vấn đề) | ✅ Đã xem lại sheet lớp 7: đúng là có nhiều **mặt sau biển tròn** bị gán "Cấm dừng và đỗ xe" |
| `excluded.txt` | 12 ảnh (10 ảnh xoay 90° + 2 ảnh valid trùng train) | ✅ |
| Gửi hình EDA cho TV4 | `EDA.zip` (17 file) | ✅ Có gói; cần TV4 xác nhận đã nhận |
| classes.yaml: QCVN, has_value, has_text | Điền đủ mã QCVN 32 lớp + `class_meta.csv` có ghi chú | ✅ |

### 3.2 Phát hiện quan trọng (đưa vào báo cáo)
1. **55/118 ảnh "không nhãn" thực ra thiếu nhãn** → để nguyên sẽ dạy YOLO bỏ qua biển.
2. **Lỗi nhãn có hệ thống**: mặt sau biển tròn gán lớp 7; tam giác ngược gán "Đường giao nhau"; biển X đường sắt không rào chắn gán lớp 22…
3. **Định nghĩa lớp lẫn lộn**: lớp 2 (bảng chỉ dẫn + biển tròn xanh R.301), lớp 23 (biển tròn + bảng xanh), lớp 28 (tam giác + tròn xanh).
4. **Thiếu đa dạng**: lớp 5, 12, 27 gần như từ một đoạn video duy nhất.
5. 53,6% box < 32 px → giữ `imgsz` 960.
6. **Chốt tập nhãn 27 lớp (29/10, ADR-009)**: đếm cụm cảnh độc lập theo lớp — 6 lớp (5, 11, 12, 22, 25, 27) chỉ có
   25–54 cụm → gộp vào "Biển báo khác". Id lớp gốc 32 → id mô hình 27 qua `classes.yaml > raw_ids`; dựng lại
   `processed/v1` + `utci_v1.zip` trước khi chạy baseline (lớp 2, 23, 28 ở mục 3 là id **gốc**).

### 3.3 Việc cần xử lý để đưa vào repo
| # | Việc | Người | Khi nào |
|---|---|---|---|
| D1 | PR cập nhật `configs/classes.yaml` theo bản TV5 (lớp 2: mandatory→info, lớp 3: info→mandatory, sửa `has_text` lớp 2/3/14/16/19, mã QCVN) | TV5 | 29/10 |
| D2 | `excluded.txt` của TV5 dùng dạng `<đường dẫn>\t<lý do>` nhưng `scripts/data.py split` đang đọc **nguyên dòng làm tên ảnh** → sẽ không loại được ảnh nào. Sửa `split` để đọc cột đầu và bỏ dòng `#` | TV3 (TV1 review) | S2, trước khi chia lại |
| D3 | Quyết định 55 ảnh thiếu nhãn: **v1 loại tạm** (theo đề xuất TV5), gán nhãn bổ sung trên Roboflow ở S2 → v2 | TV1 chốt, TV5 làm | Review 30/10 |
| D4 | Lỗi nhãn có hệ thống (lớp 7, 18, 22…): tạo thẻ S2 "Sửa nhãn lỗi theo contact-sheet" | TV5 | Planning S2 |
| D5 | Lớp lẫn lộn 2/23/28: ảnh hưởng bộ xác minh (dựa vào màu/hình dạng của siêu lớp) → ADR-002 ghi rõ cách xử lý (tách hoặc chấp nhận) | TV1 | S2 |
| D6 | Chuyển `eda_data.py` vào repo thành `scripts/eda.py` (dùng `utci_vision.data`), hình đặt ở `report/figures/`. Không đưa `check_image.py`, `check_labels.py` (script dùng một lần, đường dẫn cứng `D:\…`) | TV5 | S2 |
| D7 | Cập nhật `docs/data/DATA_CARD.md` §2–§3 bằng số liệu TV5 | TV5 | S2 |

## 4. Lộ trình còn lại đến Review (29/10 → sáng 30/10)

Chỉ còn khoảng một ngày. Ưu tiên theo thứ tự: **(1) đủ hồ sơ cho Bài KT 1 → (2) mọi người chạy được môi trường → (3) chạy baseline qua đêm**.

### Thứ Năm 29/10

| Giờ | Ai | Việc | Hoàn thành khi |
|---|---|---|---|
| Sáng | TV4 | Khung báo cáo theo template + **Chương 1** (bài toán, mục tiêu, phạm vi) | File trên Drive/Overleaf, TV1 đã xem |
| Sáng | TV4 | Báo cáo mốc S1 theo `report/README.md`: dùng số liệu EDA của TV5, trạng thái §2 | Bản nháp gửi nhóm trước 20:00 |
| Sáng | TV3 | `make env venv` → tự cài torch → `make install check-env`; `make up` mở được `localhost:18080` | Đóng thẻ 8 |
| Sáng | TV2 | Như TV3 + `cd web && npm run dev` (cổng 15173) gọi được `/api/v1/health` | Đóng thẻ 9 |
| Chiều | TV3 | `Detector.detect` + `validate`; sửa `data.yaml` gốc (`../train/images` → `train/images`) | Thẻ 5 xong |
| Chiều | TV3 | **Khởi chạy fine-tune baseline** YOLO11s 640 trên dữ liệu gốc, bỏ ảnh trong `excluded.txt` (notebook local hoặc Kaggle), chạy qua đêm | Có `best.pt` sáng 30/10 |
| Chiều | TV5 | PR D1 (`classes.yaml`); smoke test `train_colab.ipynb` với `SMOKE=True` | Thẻ 13 phần smoke xong |
| Chiều | TV1 | Smoke test `train_kaggle.ipynb`; review PR của TV5/TV3 | Thẻ 4 xong |
| Tối 20:00 | TV1 + TV2 + TV3 | Workshop 45 phút: phương án, thống nhất `api/schemas.py` ↔ `web/src/api/types.ts` | Thẻ 3 xong |
| Tối | TV2 | Spike CV trên 30 ảnh tối/ngược sáng (lấy từ contact-sheet TV5), đề xuất ngưỡng | Thẻ 10 xong hoặc chuyển S2 |

### Thứ Sáu 30/10 (sáng)

| Giờ | Ai | Việc |
|---|---|---|
| Trước 08:00 | TV3 | Import run baseline (`scripts/import_run.py … --promote`), ghi mAP@50 vào báo cáo mốc |
| Trước 08:00 | TV5 | Benchmark FPS YOLO11s bằng `best.pt` baseline (nếu thẻ 5 xong) |
| 08:00 | TV4 | Chốt báo cáo mốc S1 — **nộp Bài KT 1** |
| Review 30' | ALL | Demo: EDA + phát hiện dữ liệu (TV5) · repo/CI + web chạy Docker (TV1/TV3) · baseline (TV3) |
| Retro 20' | ALL | Giữ / Bỏ / Thử — vì sao 3 người chưa bắt đầu thẻ nào ở S1 |
| Planning 45' | ALL | Chốt D3, chuyển thẻ dở sang S2 (§5), giảm tải S2 |

## 5. Phương án nếu chưa xong trước Review

| Thẻ | Nếu dở dang | Xử lý ở S2 |
|---|---|---|
| 5 Detector + validate (TV3) | Chuyển S2, ưu tiên số 1 | Chặn baseline, benchmark, API ảnh |
| 7 Baseline (TV3) | Chuyển S2 | Gộp vào thẻ "Fine-tune YOLO11 trên v1 — E3" (chạy cả baseline gốc lẫn v1) |
| 6 Notebook SMOKE local (TV3) · 4 Kaggle (TV1) · 13 Colab + benchmark (TV5) | Chuyển S2 | Làm đầu S2, trước khi fine-tune chính thức |
| 10 Spike CV (TV2) | Gộp vào thẻ S2 "enhance.py" | Không tính thêm điểm |
| 14–15 Báo cáo (TV4) | **Không được dở** — bắt buộc cho Bài KT 1 | |

**Giảm tải S2 để bù:** S2 hiện 41 điểm (TV3 = 10). Nếu thẻ 5, 6, 7 chuyển sang, TV3 sẽ quá tải → đề xuất:
- TV1 nhận thẻ "Pipeline khung + POST /detect/image" của TV3 ở S2, hoặc đẩy sang S3.
- TV5 (đang nhẹ việc) nhận thêm D2 và hỗ trợ TV3 chạy fine-tune trên Kaggle/Colab.

## 6. Rủi ro hiện tại

| Rủi ro | Ảnh hưởng | Phương án |
|---|---|---|
| TV3 là điểm nghẽn (4 thẻ chưa làm, nhiều thẻ khác phụ thuộc) | Trễ baseline, benchmark, API | Chia việc như §5; TV3 ưu tiên thẻ 5 → 7 |
| Nhãn dữ liệu kém hơn dự kiến (55 thiếu nhãn + lỗi hệ thống) | mAP thấp, kết luận sai | Loại tạm ở v1, sửa nhãn ở S2 (D3, D4); ghi rõ trong báo cáo |
| Bài KT 1 thiếu kết quả mô hình | Điểm mốc thấp | Báo cáo tập trung vào phương án + EDA (đã đủ); baseline là phần cộng thêm nếu chạy kịp |
