# Tóm tắt EDA dữ liệu biển báo

## Tổng quan theo tập

| Tập | Số ảnh | Ảnh không bbox | Số bbox | bbox/ảnh TB |
|---|---|---|---|---|
| train | 4157 | 76 | 9976 | 2.40 |
| valid | 1076 | 32 | 3020 | 2.81 |
| test | 220 | 10 | 482 | 2.19 |

- Tổng: 5453 ảnh, 13478 bbox, 32 lớp.
- Kích thước bbox: small (<32px) 53.6% · medium (32–96px) 40.2% · large (≥96px) 6.2%.
- Độ phân giải phổ biến nhất: 960×540 (2347 ảnh); 4 độ phân giải khác nhau.
- Lớp nhiều nhất: Gioi han toc do (1705); ít nhất: Gioi han trong luong (31); tỉ lệ mất cân bằng 55.0×.
- Lớp **Gioi han toc do** (đầu vào OCR): train 1208, valid 449, test 48 bbox.
- ⚠ 19 lớp có <10 bbox trong tập test (kết quả benchmark theo lớp kém tin cậy): Ben xe buyt, Cam di thang va re phai, Cam quay dau, Cam re phai, Cam re trai va phai, Cam re trai va quay dau xe, Cho ngoat nguy hiem, Cho quay xe, Chu y chuong ngai vat, Duong bi thu hep, Duong giao nhau, Duong mot chieu, Giao nhau voi duong sat co rao chan, Gioi han trong luong, Go giam toc phia truoc, Kiem tra, Noi giao nhau chay theo vong xuyen, Tre em, Vach sang duong cho nguoi di bo.

Hình: `figures/fig1..fig6` (PNG 300 dpi + PDF). Bảng chi tiết: `class_stats.csv`.