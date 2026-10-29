# Đánh giá baseline YOLO11s-960 (Sprint 1)

- **run_id:** `20261029-1030_yolo11s_960` · **Tác giả run:** TV3 · **Đánh giá:** 29/10/2026
- **Số liệu gốc:** thư mục [`S1_baseline_yolo11s_960/`](S1_baseline_yolo11s_960/) (CSV) · tái lập ở [mục 10](#10-tái-lập)

## Tóm tắt

Baseline **tốt và đáng tin trong phạm vi dữ liệu hiện có**: test mAP50 ≈ 0,89–0,91, mAP50-95 ≈ 0,68 (CI 95% ±0,025),
khâu phát hiện chạy ≈ 55 FPS. Hai giới hạn chính:

1. **Biển nhỏ < 16 px** (17% số biển): chỉ 62% được nhận đúng, 33% bị bỏ sót.
2. **Kết quả test lạc quan so với triển khai thực tế**: trên phần ảnh test ít giống tập huấn luyện nhất,
   recall giảm còn 0,81 và precision còn 0,75 (so với 0,98 / 0,94 ở phần giống nhất).

## 1. Thiết lập thực nghiệm

| Hạng mục | Giá trị |
|---|---|
| Dữ liệu | `processed/v1`, 27 lớp (ADR-009), SHA-256 zip `40854cb1…6cc0`; train / val / test = 3 707 / 853 / 826 ảnh |
| Cách chia | Theo cụm ảnh gần trùng (pHash 8×8, Hamming ≤ 6), phân tầng theo lớp + độ phân giải (ADR-002) |
| Mô hình | YOLO11s fine-tune từ pretrained COCO, imgsz 960, batch 8, 80 epoch, AdamW lr0 0,001, `fliplr = 0`, mosaic tắt 15 epoch cuối |
| Môi trường | Google Colab, Tesla T4, Python 3.13, torch 2.11 + CUDA 13.0, Ultralytics 8.4.183 · commit `4182dbb` (develop) |
| Thời gian | 2 giờ 52 phút |
| Số lần chạy | **1** (seed 42) — chưa có lần chạy đối chứng |

**Phương pháp đánh giá:**
- Ultralytics `val` trên val và test (chỉ số chuẩn, ngưỡng conf tối ưu theo F1).
- Tính lại mAP độc lập (ghép dự đoán như Ultralytics) và **bootstrap 500 lần theo ảnh** trên test → CI 95%.
- **Ghép ở conf 0,25** — ngưỡng hiển thị của pipeline — cho từng biển thật: đúng lớp / sai lớp / bỏ sót, IoU ≥ 0,5.
- Phân tích theo kích thước, theo lớp (CI Wilson cho recall) và theo độ tương đồng với tập huấn luyện.

## 2. Quá trình huấn luyện

- Loss train và val giảm đều đến epoch 80; **val loss không tăng lại** → không quá khớp.
- mAP50-95 (val): 0,645 (epoch 30) → 0,672 (epoch 50) → 0,685 (epoch 80); 15 epoch cuối chỉ +0,003 → **gần bão hoà**,
  train thêm epoch trên cùng dữ liệu dự kiến chỉ được ≈ +0,01.
- Bước giảm loss train quanh epoch 65 là do tắt mosaic (`close_mosaic: 15`), không phải bất thường.

## 3. Kết quả tổng

| Chỉ số (test) | Ultralytics | Tính lại | CI 95% (bootstrap) |
|---|---|---|---|
| mAP50 | 0,905 | 0,892 | [0,868; 0,917] |
| mAP50-95 | 0,684 | 0,676 | [0,657; 0,702] |
| Precision @ conf 0,25 | — | 0,860 | [0,842; 0,878] |
| Recall @ conf 0,25 | — | 0,893 | [0,875; 0,913] |

- Val (Ultralytics): mAP50 0,894, mAP50-95 0,683 — **tương đương test**, không có dấu hiệu chọn mô hình quá khớp val.
- Hai cách tính lệch ≈ 0,01 do khác letterbox khi suy luận; nên báo **"mAP50 ≈ 0,89–0,91"**.
- Precision 0,93 của Ultralytics là ở ngưỡng tối ưu; **ở conf 0,25 thực tế là 0,86**.
- Đường F1–confidence có vùng đỉnh rộng (F1 ≈ 0,85–0,88 trong khoảng conf 0,25–0,75) → kết quả ít nhạy với ngưỡng.

## 4. Theo kích thước biển (val + test, conf 0,25)

| Cạnh biển | Số biển | Đúng lớp | Sai lớp | Bỏ sót |
|---|---|---|---|---|
| < 16 px | 702 | **0,617** | 0,056 | **0,328** |
| 16–32 px | 1 427 | 0,922 | 0,036 | 0,043 |
| 32–64 px | 1 261 | 0,964 | 0,013 | 0,023 |
| ≥ 64 px | 636 | 0,975 | 0,003 | 0,022 |

Biển ≥ 16 px: đúng ≈ 95%. Lỗi tập trung ở biển nhỏ; nhầm lớp chỉ chiếm phần nhỏ.

## 5. Theo lớp

Chi tiết 27 lớp: [`class_review.csv`](S1_baseline_yolo11s_960/class_review.csv) (conf 0,25, val + test) và
[`ultralytics_val.csv`](S1_baseline_yolo11s_960/ultralytics_val.csv) (AP theo lớp).

- 24/27 lớp có recall ≥ 0,81. Ba lớp yếu đều có nguyên nhân xác định:

| Lớp | n | Recall | CI 95% | Precision | Recall (≥ 16 px) | Tỉ lệ biển < 16 px | Nguyên nhân |
|---|---|---|---|---|---|---|---|
| Vạch sang đường cho người đi bộ | 30 | 0,57 | 0,39–0,73 | 0,81 | 1,00 | 0,57 | Biển nhỏ |
| Giới hạn chiều cao | 65 | 0,68 | 0,56–0,78 | 0,75 | 0,84 | 0,34 | Biển nhỏ |
| Biển chỉ dẫn hướng đi | 126 | 0,70 | 0,61–0,77 | **0,60** | 0,76 | 0,18 | Định nghĩa lớp lẫn lộn (bảng chỉ dẫn + biển tròn xanh) |

- Lượng dữ liệu tương quan yếu với chất lượng lớp (Spearman 0,16–0,32 giữa số cụm cảnh huấn luyện và recall/AP).
  Các lớp hiếm nhất (44–55 cụm) vẫn đạt recall 0,81–0,97 nhưng **CI rộng** (cận dưới 0,63–0,83) do chỉ 23–31 biển đánh giá.
- Cặp nhầm lớp lớn nhất mỗi cặp ≤ 6% số biển của lớp: Biển gộp làn ↔ Biển chỉ dẫn hướng đi; Cấm dừng và đỗ xe ↔ Cấm đỗ xe;
  Giới hạn tốc độ → Biển cấm phương tiện.
- **Không dùng ma trận nhầm lẫn do Ultralytics 8.4 vẽ**: ma trận này ghép cả dự đoán conf 0,001 (vd. 655 dự đoán cho
  163 biển "Cấm đỗ xe") nên đường chéo bị kéo thấp sai (0,39 so với ≈ 0,94 thực tế ở conf 0,25).

## 6. Theo độ tương đồng với tập huấn luyện (test)

Khoảng cách pHash từ mỗi ảnh test tới ảnh train gần nhất: trung vị 14 bit / 64 (hai ảnh ngẫu nhiên: 32);
**0%** ảnh ≤ 6 (đúng thiết kế chia theo cụm). Chia 3 nhóm (chỉ ảnh có biển; precision tính cả dự đoán thừa trên ảnh nền):

| Nhóm | Ảnh | Biển | Tỉ lệ biển < 16 px | Recall | Recall (≥ 16 px) | Precision |
|---|---|---|---|---|---|---|
| Giống train (≤ 10) | 243 | 667 | 0,12 | 0,978 | 0,978 | 0,942 |
| Trung bình (11–14) | 271 | 746 | 0,21 | 0,875 | 0,956 | 0,877 |
| Khác train (≥ 15) | 265 | 604 | 0,20 | **0,805** | **0,893** | **0,749** |

Kể cả khi loại biển nhỏ, kết quả vẫn giảm rõ theo mức "lạ" của cảnh; precision giảm mạnh nhất — **cảnh lạ sinh
nhiều phát hiện sai trên nền**. Điểm test tổng hợp được nâng bởi khoảng một phần ba ảnh có ảnh "anh em" khá giống trong
train (cùng tuyến đường, cùng camera).

## 7. Tốc độ

Khâu phát hiện (`Detector.detect`, imgsz 960, FP16, batch 1, ảnh đã nạp sẵn trong RAM) trên RTX 4060 Laptop:
**54,6 FPS** (trung bình 18,3 ms/khung). Chưa gồm tracking, bộ xác minh, OCR và đọc/giải mã video.

## 8. Đánh giá độ tin cậy

| Loại | Vấn đề | Mức ảnh hưởng |
|---|---|---|
| Ngoại suy (external validity) | Test cùng nguồn video / thành phố / camera với train; mục 6 cho thấy hiệu năng giảm theo mức lạ của cảnh | **Cao** — chưa có bằng chứng trên video ngoài dataset |
| Thống kê | 1 lần chạy, 1 seed, chưa có cấu hình đối chứng (640, freeze…); lớp hiếm chỉ 23–31 biển đánh giá | Trung bình — chênh lệch < 0,025 mAP50 nằm trong sai số |
| Nhãn | TV5 ghi nhận 23 vấn đề nhãn có hệ thống; 55 ảnh thiếu nhãn đang bị loại khỏi v1 | Trung bình — làm sai cả huấn luyện lẫn phép đo |
| Chỉ số | mAP tính theo khung hình; mục tiêu thật là nhận ra biển trong video (recall theo track) — chưa đo | Trung bình |
| Tốc độ | FPS chỉ của khâu phát hiện trên một GPU | Thấp với S1, cần đo end-to-end ở S4 |

## 9. Kết luận

**Có thể khẳng định**
- Mô hình học đúng: hội tụ, không quá khớp, val và test nhất quán.
- Trên dữ liệu cùng nguồn: mAP50 ≈ 0,89–0,91 (CI 95% ±0,025); biển ≥ 16 px nhận đúng ≈ 95%.
- Khâu phát hiện đủ nhanh cho thời gian thực trên GPU laptop tầm trung.

**Chưa thể khẳng định**
- Hiệu năng trên tuyến đường / camera mới. Ước lượng thô từ nhóm "khác train": recall ≈ 0,81, precision ≈ 0,75 — và vẫn có thể thấp hơn.
- Lớp hiếm tốt ngang lớp lớn.
- imgsz 960 tốt hơn 640.
- Toàn hệ thống đạt thời gian thực.

**Câu đề xuất cho báo cáo**

> Baseline YOLO11s (imgsz 960) đạt mAP50 = 0,89–0,91 và mAP50-95 ≈ 0,68 trên tập test chia theo cụm ảnh gần trùng
> (CI 95% ±0,025, bootstrap theo ảnh), chạy 55 FPS ở khâu phát hiện. Hiệu năng giảm rõ với biển < 16 px (recall 0,62)
> và với cảnh ít tương đồng tập huấn luyện (precision 0,75), cho thấy kết quả test lạc quan so với triển khai thực tế;
> cần đánh giá trên video ngoài tập dữ liệu.

**Việc tiếp theo** (theo thứ tự ưu tiên): bộ video test ngoài dataset · dữ liệu v2 (gán lại nhãn, định nghĩa lại
"Biển chỉ dẫn hướng đi", thêm ảnh nền khó) · thí nghiệm độ phân giải cho biển nhỏ (960 / 1280 / train trên ô cắt) ·
≥ 2 seed cho cấu hình chốt · đo recall theo track trên video.

## 10. Tái lập

```bash
python scripts/analyze_run.py <run_dir>/yolo11.pt --out reports/eval/20261029-1030_yolo11s_960
```

Cần `dataset/processed/v1` đúng bản 27 lớp (SHA zip ở mục 1). Script in toàn bộ bảng ở mục 3–6 và ghi CSV vào `--out`;
CSV trong [`S1_baseline_yolo11s_960/`](S1_baseline_yolo11s_960/) là bản làm tròn 4 chữ số của lần chạy ngày 29/10/2026
(RTX 4060 Laptop, torch 2.14.1 + CUDA 12.6). Tốc độ đo bằng
`python scripts/evaluate.py --author TV5 benchmark --yolo-only --source dataset/processed/v1/test --weights <run_dir>/yolo11.pt --device 0`.
