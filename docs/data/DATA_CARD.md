# Data Card — UTCI-VISION dataset v1

> Chủ sở hữu: **TV5**. Điền dần trong Sprint 1–2; mọi số liệu lấy từ `reports/data/` và `dataset/processed/v1/split_report.csv`.

## 1. Nguồn
| Mục | Giá trị |
|---|---|
| Tên | merge_Real-time Viet Nam Traffic Dtctn 2 (v1, xuất 2026-10-21) |
| URL | https://universe.roboflow.com/nguyns-workspace-17a6o/merge_real-time-viet-nam-traffic-dtctn-2-a7emf |
| Giấy phép | CC BY 4.0 — phải ghi nguồn trong báo cáo |
| Gốc dữ liệu | Gộp Kaggle VN Traffic Sign + Zalo AI Challenge 2020 (theo repo tham khảo) |
| Định dạng | YOLO (class cx cy w h, chuẩn hoá) · 32 lớp gốc → 27 lớp mô hình sau gộp (ADR-009) |

## 2. Thống kê dữ liệu gốc (`python scripts/data.py audit --dedup`)
| | train | valid | test |
|---|---|---|---|
| Ảnh | 4 157 | 1 076 | 220 |
| Box | 9 976 | 3 020 | 482 |
| Ảnh không nhãn | 76 | 32 | 10 |

- Ảnh hỏng: 0 · Nhãn sai định dạng: 0 · Box toạ độ không hợp lệ: 0
- Box rất nhỏ (< 0,05% diện tích ảnh): 4 041 / 13 478 (30%)
- Cụm gần trùng: 530 cụm / 2 033 ảnh; 4 cụm vắt qua nhiều tập
- 6/32 lớp không có trong test gốc

## 3. Quy trình lọc (điền khi thực hiện)
| Bước | Tiêu chí | Số ảnh/box bị ảnh hưởng | Người duyệt |
|---|---|---|---|
| Duyệt ảnh không nhãn | Giữ nếu thật sự không có biển trong 32 lớp | | TV5 |
| Duyệt contact-sheet theo lớp | Sửa/loại nhãn sai | | TV5 |
| Ảnh loại bỏ | Ghi vào `reports/data/excluded.txt` kèm lý do | | TV5 |
| Xác nhận siêu lớp | `configs/classes.yaml` khớp hình thật | | TV5 |
| Chia lại | `python scripts/data.py split` (ADR-002) | | TV5 + TV1 |

## 4. Thống kê sau lọc — processed/v1
(dán `split_report.csv` tóm tắt + biểu đồ phân bố lớp)

## 5. Gói dữ liệu & dữ liệu phụ
| Mục | Giá trị |
|---|---|
| `utci_v1.zip` — SHA-256 | |
| Upload Drive (Colab) / Kaggle Dataset `utci-v1` | |
| Crop lớp có số/chữ (`crops_v1`, để gán nhãn) | |
| Crop có nhãn giá trị số (đánh giá đọc số) | |
| Crop có nhãn chữ OCR (gồm biển phụ) | |
| Video thử (nguồn, giấy phép) | |

## 6. Hạn chế đã biết
- Mất cân bằng lớp ~55× (31 → 1 705 box).
- Phần lớn biển rất nhỏ (trung vị ≈ 25 px) — giới hạn recall và khả năng đọc số/chữ với biển ở xa.
- Lớp "Biển cấm phương tiện" gộp nhiều biển cấm khác nhau.
