# Nhận xét EDA & làm sạch dữ liệu — Sprint 1 (TV5)

Bộ dữ liệu: Roboflow `merge_real-time-viet-nam-traffic-dtctn-2` v1 (CC BY 4.0), định dạng YOLO, 32 lớp.
Hình: `figures/fig1..fig6` (PNG 300 dpi + PDF vector cho LaTeX). Số liệu chi tiết: `summary.md`, `class_stats.csv`.

## 1. Tổng quan

| Tập | Số ảnh | Ảnh không bbox | Số bbox | bbox/ảnh |
|---|---|---|---|---|
| train | 4157 | 76 | 9976 | 2.40 |
| valid | 1076 | 32 | 3020 | 2.81 |
| test | 220 | 10 | 482 | 2.19 |
| **Tổng** | **5453** | **118** | **13478** | 2.47 |

## 2. Các phát hiện chính (dùng cho báo cáo)

1. **Mất cân bằng lớp mạnh (55×)** — Hình 1. Nhiều nhất: *Gioi han toc do* (1705 bbox), *Cam dung va do xe* (1615); ít nhất: *Gioi han trong luong* (31), *Giao nhau voi duong sat co rao chan* (48).
2. **Phân chia train/valid/test không đều giữa các lớp** — Hình 1:
   - *Cam re trai va phai*: train 4 · valid 87 · test 0; *Giao nhau voi duong sat co rao chan*: train 6 · valid 42 · test 0 → mô hình gần như không được học hai lớp này.
   - *Cam di thang va re phai* và *Kiem tra*: chỉ có ở train (0 valid, 0 test) → không đánh giá được.
   - 19/32 lớp có < 10 bbox trong tập test → mAP theo lớp trên test kém tin cậy.
3. **Vật thể nhỏ chiếm đa số** — Hình 2, 6: 53.6% bbox có cạnh < 32 px (COCO "small"), 40.2% medium, chỉ 6.2% large. Trung vị cạnh bbox ~29 px.
4. **Độ phân giải không đồng nhất** — Hình 3: 960×540 (2347), 1622×626 (2262, ảnh panorama/góc rộng), 1920×1080 (805), 540×960 (39, ảnh dọc).
5. **Vị trí biển báo** tập trung ở nửa trên và bên phải khung hình (lề đường bên phải) — Hình 5.
6. **Lớp Gioi han toc do (đầu vào OCR)**: train 1208 · valid 449 · test 48 bbox.

## 3. Kết quả duyệt 118 ảnh không bbox (`review/review_unlabeled.csv`)

| Quyết định | train | valid | test | Tổng |
|---|---|---|---|---|
| `bg` – ảnh nền thật, giữ lại | 37 | 11 | 5 | 53 |
| `relabel` – **có biển thuộc 32 lớp nhưng bị thiếu nhãn** | 29 | 21 | 5 | 55 |
| `exclude` – loại | 10 | 0 | 0 | 10 |

- Gần **một nửa (55/118)** ảnh "không nhãn" thực ra chứa biển báo (thường là biển cấm đỗ/dừng, tam giác cảnh báo, biển tròn đỏ) → đây là **nhãn thiếu**, không phải ảnh nền. Để nguyên sẽ dạy mô hình bỏ qua biển (train) và tính sai FP (valid/test). Danh sách: `relabel_todo.txt`.
- 10 ảnh `exclude`: một chuỗi khung hình dọc 540×960 bị **xoay 90°**, gần trùng nhau, có biển chưa gán nhãn.
- Ảnh có biển *không thuộc 32 lớp* (biển "giám sát camera", biển chỉ dẫn có chữ, biển "hết hạn chế") được giữ làm `bg` — đây là mẫu âm tốt.
- 3 ảnh đánh dấu "cần xem lại" trong cột `note` (idx 004, 072, 075 trong file CSV).

## 4. Ảnh gần trùng (`review/review_dups.csv`, dHash ≤ 4)

- 464 cụm / 1555 ảnh, hầu hết là **khung hình video liên tiếp trong cùng một tập** → không gây rò rỉ, giữ nguyên (`ok`).
- Chỉ 4 cụm nằm giữa train ↔ valid, **0 cụm chạm tới test**. Kiểm tra thủ công: 2 cụm là cùng một cảnh (C0002, C0004) → loại bản ở valid; 2 cụm khớp nhầm/khác thời điểm (C0001, C0003) → giữ.

## 5. `excluded.txt`
12 ảnh: 10 ảnh xoay (train) + 2 ảnh valid trùng với train. Định dạng `<đường dẫn tương đối>\t<lý do>`.

## 6. Kiểm tra contact-sheet theo lớp (`contact_sheets/`, `contact_sheet_issues.csv`)

Đã xem 32 contact-sheet (tối đa 48 crop ngẫu nhiên/lớp). Đa số lớp sạch (04, 06, 08, 10, 13, 16, 17, 21, 24, 26, 30, 31). Các vấn đề chính:

- **Nhãn sai rõ ràng** (~13 trường hợp trong mẫu): mặt sau biển tròn bị gán *Cam dung va do xe* (đã đối chiếu ảnh gốc 0770); tam giác ngược (nhường đường) gán *Duong giao nhau*; biển X đường sắt không rào chắn gán *Giao nhau voi duong sat co rao chan*; bảng chữ gán *Phai di vong sang ben phai*; tam giác vàng gán *Duong mot chieu*…
- **Định nghĩa lớp không nhất quán**: *Gioi han chieu cao* trộn biển tròn với bảng xanh "Chiều cao an toàn"; *Bien chi dan huong di* trộn biển hiệu lệnh tròn với bảng chỉ dẫn; *Vong xuyen* trộn tam giác cảnh báo với biển tròn xanh.
- **Thiếu đa dạng**: *Cam di thang va re phai*, *Kiem tra*, *Cam re trai va quay dau xe* gần như chỉ đến từ 1 đoạn video → mô hình dễ học thuộc cảnh, không tổng quát hoá.
- **Nhiễu do bbox quá nhỏ**: nhiều bbox 5–10 px vẫn được gán lớp cụ thể.
- **Liên quan OCR**: lớp *Gioi han toc do* gồm cả biển tốc độ trên bảng phân làn (nền xanh) và nhiều crop mờ không đọc được số; *Gioi han trong luong* (vd "10T", "3,5") có hình dạng giống hệt biển tốc độ → khi gán nhãn OCR cần thêm trạng thái "không đọc được" và kiểm tra nhầm lẫn giữa hai lớp này.

Vì chỉ xem mẫu 48 crop/lớp, số lỗi thật trong toàn bộ 13 478 bbox có thể nhiều hơn.

## 7. Đề xuất cho nhóm
- **TV3 (huấn luyện YOLO11)**: dùng `imgsz` ≥ 960 (vật thể nhỏ); bỏ các ảnh trong `excluded.txt`; nếu chưa kịp gán nhãn bổ sung thì **bỏ tạm cả 55 ảnh trong `relabel_todo.txt`** thay vì để nhãn rỗng. Sửa đường dẫn trong `data.yaml` (`../train/images` → `train/images`).
- **TV1 (Tech Lead)**: cân nhắc chia lại train/valid/test theo kiểu phân tầng (stratified, theo nhóm video để tránh rò rỉ) vì 4 lớp hầu như vắng mặt ở train hoặc test.
- **TV5 (Benchmark/OCR)**: tập test chỉ có 48 biển tốc độ → nên dùng thêm 449 biển tốc độ của valid khi đánh giá OCR.
