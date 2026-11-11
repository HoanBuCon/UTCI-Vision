# Thử nghiệm khả thi: bộ xác minh đặc trưng thủ công (T0 + T1)

- **Ngày:** 11/11/2026 · **Trọng số:** YOLO11s-960 `20261029-1030_yolo11s_960` (baseline S1) · **Dữ liệu:** `processed/v1` (không chỉnh sửa)
- **Tái lập:** `python scripts/verifier_feasibility.py` (mặc định trọng số `models/current/yolo11.pt`) (đặc trưng: `utci_vision.verifier.region_features`)
- **Câu hỏi:** đề xuất "phương pháp truyền thống = bộ xác minh HOG + màu + hình dạng + Hu → LightGBM" (04_BAO_CAO_DE_XUAT §6.3)
  có tăng được precision của YOLO không, và có đạt mục tiêu G2 (precision ≥ 0,90, recall giảm ≤ 0,03) không?

## Kết luận

**Chưa khả thi ở dạng hiện tại.** Bộ xác minh chạy đúng nhưng **không vượt được điểm tin cậy của chính YOLO**:

- Ở **cùng recall** với YOLO @0,25: ΔPrecision = +0,005 [CI95 −0,012; +0,022] — **không có ý nghĩa thống kê**.
- Với ngưỡng chọn trên val: P 0,864 → 0,878 (+0,014 [CI95 +0,005; +0,025]), R 0,893 → 0,891 — có ý nghĩa nhưng phần lớn
  do dịch điểm vận hành; **xa mục tiêu 0,90**.
- Mức cải thiện lớn nhất ở cảnh **ít giống ảnh train**: P 0,758 → 0,783 (+0,025, chưa có CI riêng).

## T0 — Dư địa

| Tập | Ngưỡng | Precision | Recall | Dự đoán sai: nền / sai lớp / định vị kém |
|---|---|---|---|---|
| val | 0,25 | 0,868 | 0,895 | 71% / 24% / 4% (273) |
| val | 0,10 | 0,785 | 0,910 | 70% / 24% / 6% (500) |
| test | 0,25 | 0,864 | 0,893 | 68% / 25% / 6% (284) |
| test | 0,10 | 0,790 | 0,916 | 71% / 21% / 8% (491) |

- Dư địa về lý thuyết lớn: ~70% dự đoán sai là **nền** — đúng loại lỗi màu / hình dạng có thể nhận ra. Trần của bộ xác minh
  chỉ loại bỏ: precision 1,0 với recall tối đa 0,916.
- Nhưng **điểm YOLO đã phân biệt đúng / sai rất tốt (AUC 0,941)** — đó là mức bộ xác minh phải vượt.

## T1 — Ablation tập đặc trưng (fit trên ứng viên val, đánh giá test)

| Tập đặc trưng | AUC | AP ứng viên | P cùng recall (R 0,893) | P / R ngưỡng val |
|---|---|---|---|---|
| **YOLO thuần** (điểm YOLO) | **0,941** | **0,983** | 0,864 | 0,864 / 0,893 |
| Ngữ cảnh YOLO (điểm, lớp, kích thước, vị trí) — đối chứng | 0,929 | 0,977 | 0,864 | 0,886 / 0,879 |
| + màu HSV | 0,933 | 0,979 | 0,863 | 0,880 / 0,881 |
| + màu + hình học + Hu | 0,935 | 0,982 | 0,859 | 0,875 / 0,887 |
| + màu + hình học + Hu + HOG | 0,935 | 0,980 | **0,876** | 0,872 / 0,895 |
| Đầy đủ (+ độ nét, độ sáng) | 0,934 | 0,979 | 0,866 | 0,878 / 0,891 |
| Chỉ đặc trưng thủ công (không có điểm YOLO) | 0,856 | 0,953 | 0,832 | 0,842 / 0,888 |

ΔP ở cùng recall (bootstrap 1 000 lần theo ảnh): đầy đủ − YOLO +0,005 [−0,012; +0,022]; đầy đủ − ngữ cảnh +0,007 [−0,009; +0,025];
+HOG − YOLO +0,010 [−0,006; +0,025]. Đặc trưng quan trọng nhất: điểm YOLO chiếm 58% gain; HOG-PCA, Hu, độ sáng mỗi đặc trưng 1–2%.

| Nhóm ảnh test (pHash tới ảnh train gần nhất) | Biển | P / R YOLO @0,25 | P / R xác minh |
|---|---|---|---|
| Giống train (≤ 10) | 667 | 0,945 / 0,981 | 0,946 / 0,979 |
| Trung bình (11–14) | 746 | 0,881 / 0,879 | 0,896 / 0,877 |
| Khác train (≥ 15) | 604 | 0,758 / 0,815 | 0,783 / 0,811 |

## Giải thích

1. **Đặc trưng thủ công có tín hiệu** (AUC 0,856 khi đứng một mình, xa mức ngẫu nhiên 0,5) nhưng **trùng lặp** với thông tin
   CNN đã học — biển đã qua YOLO với điểm cao hầu như luôn có màu / hình dạng đúng.
2. **Thiếu mẫu âm để học:** chỉ 500 dự đoán sai trên val (so với 1 828 đúng). Không thể lấy thêm từ train (YOLO đã học thuộc
   train nên ít báo sai) nếu không đổi dữ liệu (thêm ảnh nền khó — đang chờ duyệt).
3. Lợi ích tập trung ở cảnh lạ — nơi điểm YOLO kém tin cậy hơn — nhưng nhóm này chỉ có 604 biển nên chưa đủ để kết luận.

## Hạn chế của thử nghiệm
- Val đã dùng để chọn epoch tốt nhất của YOLO (ảnh hưởng nhỏ); test chưa dùng cho bất kỳ lựa chọn nào.
- Dự đoán "trùng" tính là sai (bảo thủ); 1 lần chạy LightGBM (random_state 0), siêu tham số mặc định trong `configs/verifier.yaml`.
- Chưa thử: hiệu chỉnh mục tiêu (biển / không phải biển thay vì đúng lớp), phân loại lại lớp bằng đặc trưng thủ công.

## Đề xuất hướng đi (cần nhóm quyết định)
- **A. Giữ bộ xác minh trong pipeline như kết quả ablation trung thực** (+0,014 precision, có ý nghĩa ở ngưỡng val; không có ý nghĩa
  ở cùng recall) — hợp lệ về khoa học nhưng yếu để làm điểm nhấn của phần "phương pháp truyền thống".
- **B. Đặt phương pháp truyền thống vào vai trò có thể chứng minh rõ hơn:** E8 (HOG+SVM / SIFT-BoVW+SVM vs YOLO phân loại theo
  kích thước) — so sánh trực tiếp, không phụ thuộc điểm YOLO; tăng cường ảnh trên ảnh tối (T4); theo vết trên video.
- **C. Cải thiện bộ xác minh:** cần thêm mẫu âm (ảnh nền khó — phụ thuộc đề xuất dataset v2 đang chờ duyệt) hoặc đổi mục tiêu
  sang "biển / không phải biển".
