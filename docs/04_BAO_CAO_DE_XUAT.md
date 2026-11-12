# Hệ thống nhận diện biển báo giao thông (UTCI-Vision) — Báo cáo đề xuất kỹ thuật

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.1 — 12/11/2026 (cập nhật sau thử nghiệm khả thi; bản 1.0: 11/11/2026) |
| Học phần | Thị giác máy tính |
| Nhóm | 5 thành viên (TV1–TV5) — phân vai ở §9 |
| Liên quan | [00_PHUONG_AN](00_PHUONG_AN.md) · [02_SRS](02_SRS.md) · [03_SPRINT_PLAN](03_SPRINT_PLAN.md) · [danh_gia/S1_baseline](danh_gia/S1_baseline_yolo11s_960.md) · [research/](research/README.md) |

## Tóm tắt

Đề tài xây dựng **hệ thống nhận diện biển báo giao thông đường bộ Việt Nam** từ ảnh, video và webcam, chạy dưới dạng web
(Docker). Theo yêu cầu học phần, hệ thống dùng **hai nhóm phương pháp có vai trò thật và đo được**:

1. **Học sâu** — YOLO11s fine-tune từ trọng số COCO để *phát hiện + phân loại* 27 lớp biển; VietOCR đọc số / chữ.
2. **Thị giác máy tính truyền thống & trích xuất đặc trưng thủ công** — tăng cường ảnh thích nghi; **trích xuất đặc
   trưng HOG + màu HSV + hình học contour + Hu moments** cho *bộ xác minh* (LightGBM) loại phát hiện sai;
   theo vết Kalman + IoU; cắt vùng số / chữ.

Baseline YOLO11s-960 đã đạt **mAP@50 ≈ 0,89–0,91** trên test (CI 95% ±0,025), 55 FPS ở khâu phát hiện. Phân tích cho
thấy hai điểm yếu có số đo: **biển < 16 px** (recall 0,62) và **cảnh ít giống tập huấn luyện** (precision 0,75). Đề xuất
này dùng chính hai điểm yếu đó để định vị phương pháp truyền thống (xác minh để tăng precision) và các thí nghiệm còn lại.

## 0. Cập nhật 12/11/2026 — quyết định sau thử nghiệm khả thi

**Ràng buộc mới (C-08):** dataset đóng băng ở `processed/v1` — không bổ sung ảnh, không gán thêm / sửa nhãn. Video chỉ dùng để demo
và đo độ ổn định nhãn (E6). Mọi cải thiện từ đây đến từ **phương pháp**.

**Kết quả thử nghiệm với trọng số baseline** ([T0/T1](danh_gia/S3_T0_T1_kha_thi_bo_xac_minh.md), [E8/T4](danh_gia/S3_E8_T4_phuong_phap_truyen_thong.md)):

| Thử nghiệm | Kết quả | Hệ quả |
|---|---|---|
| T1 — bộ xác minh đặc trưng thủ công + LightGBM | Không vượt điểm YOLO ở cùng recall (ΔP +0,005, CI95 −0,012…+0,022) | Thành khâu **tuỳ chọn, mặc định tắt**; báo cáo như kết quả ablation |
| T4 — tăng cường thích nghi trên ảnh xấu | Ảnh rất tối: recall 0,686 → **0,822**; không hại ảnh gốc / nhiễu / mờ | **Khâu CV truyền thống chính** trong pipeline |
| E8 — HOG + màu / SIFT + SVM vs YOLO | HOG + màu 91,0% vs YOLO 92,4%; ngang YOLO trên biển < 16 px đã tìm thấy; SIFT 71,1% | **Chương so sánh** hai phương pháp |

**Phương pháp truyền thống sau cập nhật:** (1) tăng cường ảnh thích nghi, (2) theo vết Kalman + IoU + bỏ phiếu nhãn, (3) HOG / màu /
SIFT + SVM làm phương pháp phân loại đối chứng (E8), (4) bộ xác minh làm ablation, (5) xử lý vùng cho OCR. Các mục trong báo cáo
mâu thuẫn với mục này được đánh dấu *(thay bởi §0)*.

---

## 1. Bài toán

### 1.1 Phát biểu
- **Đầu vào:** ảnh tĩnh, video, luồng webcam (đường phố Việt Nam, góc nhìn từ xe / người đi đường).
- **Đầu ra:** với mỗi biển — hộp bao, lớp (27 lớp, tên tiếng Việt, mã QCVN 41:2019), độ tin cậy đã hiệu chỉnh,
  `track_id` (video), giá trị số (km/h, m) và chữ trên biển / biển phụ khi đọc được.
- **Đặc thù khó:** biển rất nhỏ (trung vị cạnh 30 px; 54% < 32 px), mất cân bằng lớp (22×), nhiều biển giống nhau chỉ khác
  chi tiết bên trong (Cấm đỗ xe / Cấm dừng và đỗ xe), nền đô thị nhiều vật thể giống biển (biển quảng cáo, đèn), yêu cầu
  thời gian thực.

### 1.2 Ràng buộc
| Ràng buộc | Nội dung |
|---|---|
| Phương pháp | Bắt buộc **CV truyền thống / trích xuất đặc trưng truyền thống** bên cạnh **học sâu**, mỗi phương pháp có vai trò thật và kết quả đánh giá riêng |
| Thời gian | 6 sprint × 1 tuần (23/10 → 04/12/2026); hiện đang ở Sprint 3 (06–13/11) |
| Nhân lực | 5 thành viên |
| Hạ tầng | GPU cá nhân (RTX 4060 Laptop), Google Colab, Kaggle; demo bắt buộc chạy được trên CPU qua Docker |
| Huấn luyện | Chỉ fine-tune từ trọng số pretrained, qua 3 notebook (ADR-006) |

## 2. Hiện trạng dự án (11/11/2026)

| Hạng mục | Trạng thái | Bằng chứng |
|---|---|---|
| Repo, CI, Makefile, Docker (CPU/GPU), cổng custom | ✅ Xong | `make ci` xanh (48 test); `make up` → web 18080 + API healthy |
| Dữ liệu: audit, lọc 67 ảnh, chia lại theo cụm, gộp lớp, đóng gói | ✅ Xong (v1, 27 lớp) | `processed/v1`, `utci_v1.zip` (SHA `40854cb…`), ADR-002, ADR-009 |
| Tăng cường ảnh thích nghi (`enhance.py`) | ✅ Xong, chưa nối vào pipeline | ngưỡng chọn từ thống kê 5 453 ảnh |
| Detector + validate + 3 notebook | ✅ Xong | smoke local, baseline trên Colab |
| Baseline YOLO11s-960 + đánh giá khách quan | ✅ Xong | [danh_gia/S1_baseline](danh_gia/S1_baseline_yolo11s_960.md), `scripts/analyze_run.py` |
| Benchmark FPS khâu phát hiện | ✅ Xong | 54,6 FPS (RTX 4060 Laptop, 960, FP16) |
| Bộ xác minh: đặc trưng vùng + LightGBM | ❌ Chưa (khung) | `verifier.py` còn `NotImplementedError` |
| Theo vết Kalman + IoU | ❌ Chưa | `tracking.py` |
| Đọc số / OCR / biển phụ | ❌ Chưa | `ocr.py` |
| Pipeline đầy đủ, `POST /detect/image`, job video | ❌ Chưa | `pipeline.py`, `api/jobs.py` |
| Bộ đánh giá E1 (`evaluate.py detect`), trang Ảnh/Video | ❌ Chưa | — |

**Nhận định:** các thẻ Sprint 2 phía *pipeline* (đặc trưng vùng, pipeline khung, E1, trang Ảnh) chưa được merge vào
`develop`. Phần học sâu đã vượt mục tiêu; phần CV truyền thống — chính là yêu cầu bắt buộc của giảng viên — đang chậm
nhất. §9 đề xuất sắp xếp lại ưu tiên để đóng lỗ hổng này trước Sprint 4.

## 3. Dữ liệu

### 3.1 Nguồn & xử lý
- Roboflow *merge Real-time Viet Nam Traffic Dtctn 2* (CC BY 4.0), gộp từ Kaggle VN Traffic Sign và **Zalo AI Challenge
  2020** (ảnh 1622×626 từ Google Street View — chiếm 41% dataset).
- Dữ liệu gốc: 5 453 ảnh, 13 478 box, 32 lớp; 37% ảnh thuộc cụm gần trùng; 6/32 lớp không có trong test gốc.
- Đã xử lý: loại 12 ảnh lỗi + tạm loại 55 ảnh thiếu nhãn (TV5); **chia lại 70/15/15 theo cụm pHash**, phân tầng theo
  lớp + độ phân giải (ADR-002); **gộp 6 lớp < 60 cụm cảnh vào "Biển báo khác"** (ADR-009) → **27 lớp**.

### 3.2 Thống kê `processed/v1` (27 lớp)
| | train | val | test | tổng |
|---|---|---|---|---|
| Ảnh | 3 707 | 853 | 826 | 5 386 (53 ảnh nền) |
| Box | 9 450 | 2 009 | 2 017 | 13 476 |

- Kích thước biển: trung vị cạnh **30 px**; **18,3% < 16 px**; **53,7% < 32 px**.
- Độ phân giải: 960×540 (44%), 1622×626 (41%), 1920×1080 (15%), 540×960 (< 1%).
- Siêu lớp: biển cấm 57% · nguy hiểm 18% · hiệu lệnh 13% · chỉ dẫn 9% · "khác" 4%.
- Mất cân bằng: 1 705 (Giới hạn tốc độ) → 76 (Chỗ quay xe) box, **22×** (trước gộp: 55×).

| Lớp | Siêu lớp | Box (train/val/test) | Cụm cảnh | Cạnh trung vị | % < 16 px |
|---|---|---|---|---|---|
| Giới hạn tốc độ | cấm | 1 705 (1194/256/255) | 581 | 29 | 14 |
| Cấm dừng và đỗ xe | cấm | 1 615 | 998 | 28 | 18 |
| Biển cấm phương tiện | cấm | 1 376 | 721 | 31 | 10 |
| Cấm đỗ xe | cấm | 1 093 | 797 | 30 | 10 |
| Cấm đi ngược chiều | cấm | 995 | 733 | **17** | **48** |
| Biển gộp làn đường theo phương tiện | hiệu lệnh | 810 | 494 | 50 | 17 |
| Phải đi vòng sang bên phải | hiệu lệnh | 788 | 577 | **19** | **43** |
| Giao nhau với đường không ưu tiên | nguy hiểm | 557 | 480 | 32 | 16 |
| Biển báo khác (6 lớp gộp) | khác | 535 | 227 | 38 | 1 |
| Đi chậm | nguy hiểm | 454 | 297 | 42 | 6 |
| Biển chỉ dẫn hướng đi | chỉ dẫn | 429 | 251 | 27 | 27 |
| Đường người đi bộ cắt ngang | nguy hiểm | 420 | 327 | 34 | 12 |
| Chỗ ngoặt nguy hiểm | nguy hiểm | 367 | 195 | 39 | 4 |
| Cấm rẽ trái | cấm | 335 | 196 | 36 | 17 |
| Đường một chiều | chỉ dẫn | 283 | 168 | 29 | 13 |
| Bến xe buýt | chỉ dẫn | 268 | 191 | 42 | 12 |
| Cấm rẽ phải | cấm | 246 | 162 | 45 | 11 |
| Giới hạn chiều cao | cấm | 217 | 152 | **20** | **38** |
| Gồ giảm tốc phía trước | nguy hiểm | 187 | 107 | 28 | 18 |
| Cấm quay đầu | cấm | 145 | 93 | 37 | 16 |
| Đường giao nhau | nguy hiểm | 104 | 76 | 42 | 2 |
| Trẻ em | nguy hiểm | 103 | 81 | 31 | 11 |
| Chú ý chướng ngại vật | nguy hiểm | 98 | 73 | 30 | 15 |
| Vạch sang đường cho người đi bộ | chỉ dẫn | 98 | 95 | **19** | **45** |
| Nơi giao nhau chạy theo vòng xuyến | hiệu lệnh | 93 | 79 | 30 | 20 |
| Đường bị thu hẹp | nguy hiểm | 79 | 73 | 30 | 10 |
| Chỗ quay xe | chỉ dẫn | 76 | 63 | 21 | 38 |

### 3.3 Vấn đề còn lại & kế hoạch tinh chỉnh *(thay bởi §0: không thực hiện — dataset đóng băng, các vấn đề dưới đây được báo cáo như hạn chế)*
| Vấn đề (có số đo) | Hành động | Phụ trách |
|---|---|---|
| 55 ảnh thiếu nhãn đang bị loại | Gán nhãn bổ sung, đưa lại vào dataset | TV5 |
| 23 lỗi nhãn có hệ thống (mặt sau biển gán lớp "Cấm dừng và đỗ xe", tam giác ngược gán "Đường giao nhau"…) | Sửa nhãn theo `docs/data/review/contact_sheet_issues.csv` | TV5 |
| "Biển chỉ dẫn hướng đi" trộn bảng chỉ dẫn với biển tròn xanh → precision 0,60 | Định nghĩa lại theo QCVN (tách / chuyển nhãn) | TV5 + TV1 |
| Precision giảm còn 0,75 trên cảnh ít giống train (dương tính giả trên nền) | Thêm **ảnh nền khó** (biển quảng cáo, mặt sau biển, đèn) với nhãn rỗng | TV5 |
| Test cùng nguồn với train → kết quả lạc quan | Tạo **tập test ngoài phân phối (OOD)**: ≥ 2 video / ≥ 300 frame tuyến đường mới, gán nhãn | TV5 |
| Lớp hiếm có CI rộng | Thêm **cảnh mới** (không thêm frame trùng) cho Chỗ quay xe, Vạch sang đường, Đường một chiều | TV5 |

*(Không áp dụng — không có v2.)* Quy tắc giữ lớp sau v2 (chốt trước, tránh chọn theo kết quả): gộp vào "Biển báo khác" nếu một lớp có ≥ 20 biển ≥ 16 px
để đánh giá **và** cận trên CI 95% của recall < 0,75 **và** lỗi không do kích thước / nhãn sai.

## 4. Tổng quan nghiên cứu liên quan

Danh mục đầy đủ, link và bản PDF: [research/README.md](research/README.md).

### 4.1 Phương pháp truyền thống
- **Màu + hình dạng** là hướng kinh điển: phân đoạn ngưỡng trong một không gian màu, rồi kiểm tra hình dạng trên vùng
  ứng viên. GTSDB (Houben et al., 2013) đánh giá Viola-Jones (Haar), **HOG + LDA** và thuật toán chuyên biệt dùng màu +
  hình dạng (Hough-like voting) [R2].
- **HOG** (Dalal & Triggs, 2005) [R1] là đặc trưng thủ công mạnh nhất cho biển: trên GTSRB, HOG + LDA ≈ 95,7% so với CNN
  ≈ 99,5–99,7%; nghiên cứu gần đây với HOG-SVM đạt 89,65–91,25% tuỳ tiền xử lý [R3]. Khoảng cách này đo trên crop **lớn,
  rõ**; với biển nhỏ khoảng cách sẽ lớn hơn.
- **Kết hợp**: phân đoạn màu trước CNN giảm dương tính giả và thời gian tính; HOG/SURF bổ trợ CNN nâng độ chính xác với
  ít tham số [R5, R7].

### 4.2 Học sâu & biển nhỏ
- Họ YOLO là chuẩn thực tế cho phát hiện thời gian thực [R8]. Các cải tiến cho biển nhỏ trên TT100K: thêm đầu phát hiện độ
  phân giải cao (P2), hợp nhất đa tỉ lệ (STC-YOLO +9,3% mAP so với YOLOv5; ESA-YOLO dựa YOLO11n +3,8% mAP@50) [R10–R12].
- **SAHI** (suy luận cắt lát) tăng AP +5–7% cho vật thể nhỏ, +12–15% khi fine-tune trên lát cắt [R9]. Giải pháp Zalo AI
  2020 — trùng nguồn ảnh với dự án — dùng **cắt ô ảnh** vì biển rất nhỏ [R14].

### 4.3 Biển báo Việt Nam
- Các công trình 2024 dùng YOLOv5 trên dataset tự thu: 10 lớp biển nguy hiểm (> 11 138 ảnh) [R16]; module nhúng Jetson
  [R15]. [R15] ghi nhận mô hình train trên GTSRB **không chuyển được** sang biển Việt Nam, và phương pháp truyền thống
  nhanh nhưng kém bền với ánh sáng / góc nhìn / che khuất.
- Số liệu các bài khác dataset, khác cách chia và khác chỉ số → chỉ dùng làm bối cảnh, không so sánh trực tiếp.

### 4.4 Tổng quát hoá, theo vết, xác minh
- Mô hình biển báo thường giảm mạnh khi sang vùng / bối cảnh mới [R20]; Mapillary dùng lớp `other-sign` cho biển ngoài
  danh mục [R19] — tiền lệ cho lớp "Biển báo khác".
- Trên video, **recall cao dễ đạt, precision mới khó**; Šegvić et al. tăng precision bằng chuỗi theo vết + một **giai đoạn
  phân biệt (xác minh) riêng** [R23]. SORT (Kalman + IoU) [R22] là chuẩn theo vết nhẹ.

### 4.5 Bài học cho thiết kế
| Phát hiện từ nghiên cứu | Áp dụng |
|---|---|
| Học sâu vượt xa đặc trưng thủ công ở **phân loại** | Học sâu làm lõi phát hiện + phân loại |
| Màu / hình dạng / HOG hiệu quả để **loại dương tính giả** | Phương pháp truyền thống làm **bộ xác minh**, nhắm điểm yếu precision 0,75 đã đo |
| Biển nhỏ là nút thắt chính; cắt ô / SAHI / độ phân giải cao giúp | Thí nghiệm độ phân giải (E3), SAHI cho ảnh tĩnh |
| Precision trên video cần theo vết + xác minh | Kalman + IoU + bỏ phiếu nhãn theo track |
| Kết quả cùng nguồn lạc quan | Tập test OOD + phân tích theo độ tương đồng |

## 5. Mục tiêu

| # | Mục tiêu | Chỉ số | Hiện tại (baseline) | Mục tiêu v1.0 |
|---|---|---|---|---|
| G1 | Phát hiện + phân loại tốt trên dữ liệu cùng nguồn | mAP@50 / mAP@50:95 test | 0,89–0,91 / 0,68 | ≥ 0,88 / ≥ 0,68 (giữ, không giảm khi thêm khâu) |
| G2 | ~~Phương pháp truyền thống tăng precision~~ *(thay bởi §0: T1 không đạt)* → **Tăng cường giữ recall khi ảnh tối** | Recall test làm tối γ 3,5 | 0,686 (không tăng cường) | ≥ 0,80 (T4: 0,822), ảnh gốc giảm ≤ 0,005 |
| G3 | Bền hơn trên cảnh lạ | Precision trên nhóm ảnh test "khác train" (không có tập OOD — C-08) | 0,758 | Báo cáo kèm CI |
| G4 | Biển nhỏ (không train lại: imgsz 1280 / SAHI) | Recall biển < 16 px (conf 0,25) | 0,62 | ≥ 0,70 |
| G5 | So sánh có căn cứ hai phương pháp | Bảng E8 (truyền thống vs học sâu theo kích thước) | — | Có, kèm CI |
| G6 | Thời gian thực | FPS web (GPU) / ảnh tĩnh CPU | 55 FPS (chỉ detector) | ≥ 20 FPS end-to-end / ≤ 1,5 s |
| G7 | Đọc giá trị số | Định tính (không có nhãn giá trị — C-08) | — | Ví dụ đúng / sai trong báo cáo |
| G8 | Tái lập | Số liệu truy về registry + script | `analyze_run.py` | 100% |

## 6. Phương pháp đề xuất

### 6.1 Kiến trúc tổng thể
```
Frame ─► [CV]  Đánh giá chất lượng (V, L, Laplacian) ─► gamma + CLAHE + lọc song phương (chỉ khi cần)
      ─► [DL]  YOLO11s (960): phát hiện + phân loại 27 lớp, conf thấp 0,10 để giữ recall
      ─► [CV]  Theo vết: Kalman + ghép IoU, xác nhận sau ≥ 3 frame, bỏ phiếu nhãn
      ─► Theo track (chạy nền):
            [CV ĐẶC TRƯNG + ML]  HOG · màu HSV · hình học contour · Hu moments ─► LightGBM xác minh
            [CV + DL]            cắt vùng số ─► VietOCR ─► regex hợp lệ hoá (50 km/h, 3.5 m)
            [CV + DL]            frame tốt nhất ─► vùng chữ / biển phụ ─► VietOCR ─► từ điển
      ─► API ─► Web
```

### 6.2 Phương pháp 1 — Học sâu
| Thành phần | Thiết kế | Căn cứ |
|---|---|---|
| Detector | **YOLO11s** fine-tune từ COCO; imgsz 960; AdamW lr0 0,001; 80 epoch; `fliplr = 0` (biển trái/phải đổi nghĩa); mosaic, mixup | Baseline đạt 0,89–0,91 mAP@50, 55 FPS; hội tụ, không quá khớp |
| Biển nhỏ | E3: 960 vs **1280** vs **huấn luyện trên ô cắt** ở độ phân giải gốc; SAHI chỉ cho ảnh tĩnh | 33% biển < 16 px bị bỏ sót; [R9, R14] |
| OCR | VietOCR pretrained (transformer), đọc cả số và chữ tiếng Việt | Không cần SVM chữ số riêng (FR-TRAIN-06 Dropped) |
| Bỏ khỏi cấu hình | `copy_paste` (cần nhãn segment, vô tác dụng với nhãn bbox) | — |

### 6.3 Phương pháp 2 — Thị giác máy tính truyền thống & trích xuất đặc trưng thủ công

**(a) Bộ xác minh dựa trên đặc trưng thủ công** *(thay bởi §0: khâu tuỳ chọn, mặc định tắt — T1 không vượt điểm YOLO)*. Với mỗi hộp YOLO (conf ≥ 0,10),
cắt vùng (pad 10%) và trích:

| Nhóm | Đặc trưng | Kỹ thuật | Tri thức QCVN mã hoá |
|---|---|---|---|
| Màu | Tỉ lệ pixel đỏ / xanh / vàng / trắng; tỉ lệ viền vs lõi | Ngưỡng HSV (2 dải cho đỏ) | Cấm: viền đỏ; hiệu lệnh: nền xanh; nguy hiểm: nền vàng |
| Hình học | Độ tròn 4πA/P², số đỉnh `approxPolyDP`, solidity, tỉ lệ khung | Contour lớn nhất sau Otsu / mask màu | Tròn / tam giác / chữ nhật |
| Mô men | 7 Hu moments (log) | Mô men chuẩn hoá | Hình dạng bất biến tỉ lệ |
| Hoa văn trong | **HOG** 32×32, 9 hướng, ô 8×8 → PCA 16 chiều | Gradient histogram [R1] | Mũi tên, chữ P gạch, số |
| Chất lượng | Phương sai Laplacian, độ sáng | — | Biết vùng nhoè / tối để giảm tin cậy |
| Ngữ cảnh | Điểm YOLO, lớp, kích thước / vị trí hộp | — | — |

- **Huấn luyện (stacking):** mẫu = hộp YOLO dự đoán trên **val** (YOLO chưa thấy), nhãn 1 nếu khớp GT cùng lớp IoU ≥ 0,5;
  LightGBM `class_weight=balanced`, CV 5 fold, hiệu chỉnh isotonic. Test chỉ dùng để đánh giá.
- **Đầu ra:** xác suất "đúng" thay cho điểm YOLO; ngưỡng chọn trên val để recall giảm ≤ 0,03.
- **Vì sao đặt ở khâu xác minh, không làm khâu phát hiện chính:** trên dữ liệu này, SIFT tìm được < 5 điểm khoá ở **93%**
  biển < 16 px và 25% biển 16–32 px (đo trên 2 017 biển test), nên đặc trưng điểm khoá không dùng được cho đa số biển; HOG
  tính dày đặc trên lưới cố định nên vẫn cho vector đầy đủ, nhưng phân loại 27 lớp bằng đặc trưng thủ công kém CNN
  [R3, §4.1]. Ngược lại, câu hỏi "vùng này có màu / hình dạng / hoa văn của biển lớp X không?" là việc đặc trưng thủ công
  làm tốt và **bổ trợ** đúng điểm yếu đã đo của YOLO (dương tính giả trên nền lạ).

**(b) Tăng cường ảnh thích nghi — khâu truyền thống chính** (đã cài; T4 xác nhận): đánh giá chất lượng trên ảnh thu nhỏ; chỉ áp dụng gamma tự động + CLAHE trên
kênh L (LAB) + lọc song phương khi ảnh tối / tương phản thấp / nhiễu (ngưỡng từ thống kê 5 453 ảnh: 1,7% / 1,3% / 0,6% ảnh).

**(c) Theo vết Kalman + IoU** (SORT [R22]): trạng thái [cx, cy, s, r] + vận tốc; ghép Hungarian theo IoU; track xác nhận
sau ≥ 3 frame; nhãn = bỏ phiếu có trọng số theo xác suất xác minh → ổn định nhãn, mỗi biển báo một lần, chọn frame tốt
cho OCR.

**(d) Xử lý vùng cho OCR:** đĩa trắng trong viền đỏ (vùng số), phóng to + CLAHE + nắn nghiêng `minAreaRect` (dòng chữ),
tìm tấm chữ nhật sáng dưới biển chính (biển phụ).

### 6.4 Thí nghiệm
| Mã | Câu hỏi | Thiết kế | Chỉ số |
|---|---|---|---|
| E1 | Hệ thống tốt đến đâu? | Test v1 + tập OOD | mAP@50, mAP@50:95, P/R @ điểm vận hành (CI bootstrap), theo lớp, theo kích thước, theo độ tương đồng |
| E2 | Mỗi khâu đóng góp bao nhiêu? | Ablation: YOLO → + tăng cường → + **xác minh** → + theo vết | ΔPrecision, ΔRecall, ΔmAP, Δflicker, ΔFPS |
| E3 | Cấu hình YOLO & bộ xác minh | YOLO: imgsz 960 / 1280 / ô cắt (± freeze); xác minh: LogReg / RF / LightGBM; **tập đặc trưng: màu / +hình học / +HOG / đầy đủ** | mAP, recall < 16 px, FPS; AUC, precision @ recall cố định |
| E4 | Độ bền | Tối, mờ, nhiễu, mưa nhân tạo ± tăng cường | ΔmAP |
| E5 | Đọc số / chữ | VietOCR ± cắt vùng CV, vs EasyOCR | Accuracy giá trị, CER, exact match |
| E6 | Ổn định video | ± theo vết | Flicker rate |
| E7 | Giải thích | Feature importance LightGBM, ảnh trung gian | — |
| **E8** | **Truyền thống vs học sâu khi phân loại** | Crop biển GT (train → fit, test → đánh giá): **HOG + SVM**, **SIFT-BoVW + SVM**, YOLO (độ chính xác lớp trên cùng crop) | Accuracy / macro-F1 **theo nhóm kích thước** (< 16, 16–32, 32–64, ≥ 64 px), thời gian / crop |

Quy tắc báo cáo: CI 95% bootstrap theo ảnh cho chỉ số tổng, CI Wilson cho tỉ lệ theo lớp; số liệu truy về
`experiments/registry.csv`; đo bằng `scripts/analyze_run.py` để mọi run so sánh cùng thước đo. **Không dùng ma trận nhầm
lẫn của Ultralytics 8.4** (ghép cả dự đoán conf 0,001) — thay bằng ghép ở điểm vận hành.

## 7. Công nghệ

| Lớp | Công nghệ | Lý do |
|---|---|---|
| Học sâu | PyTorch (tự cài theo GPU), **Ultralytics YOLO11 8.4.183**, VietOCR 0.3.13 | Chuẩn thực tế cho phát hiện thời gian thực; OCR tiếng Việt có dấu |
| CV truyền thống | **OpenCV 4.14** (HSV, contour, Hu, CLAHE, Kalman), **scikit-image** (HOG), imagehash (pHash) | Thư viện chuẩn, đủ toàn bộ kỹ thuật ở §6.3 |
| Học máy | **LightGBM 4.7**, scikit-learn (SVM, PCA, hiệu chỉnh xác suất, LogReg/RF cho E3) | Nhanh, xử lý đặc trưng dị loại, có feature importance |
| Dữ liệu / đánh giá | numpy, pandas, Ultralytics metrics, bootstrap tự viết | Tái lập, có CI |
| Huấn luyện | 3 notebook sinh từ một template (Local / Colab / Kaggle) | ADR-006 |
| Ứng dụng | FastAPI + WebSocket; React + TypeScript + Vite; Nginx; Docker Compose (CPU / GPU) | ADR-003; cổng custom ADR-007 |
| Chất lượng | ruff, pytest (48 test), `tsc --noEmit`, CI GitHub; Conventional Commits, PR về `develop` | `docs/quy_uoc.md` |

## 8. Kế hoạch đánh giá thành công

Tiêu chí chấp nhận cho phần phương pháp (bổ sung SRS §7):
1. Bảng **E2** cho thấy đóng góp của khâu truyền thống (xác minh) với CI; nếu không cải thiện, báo cáo trung thực là kết
   quả âm kèm phân tích lỗi.
2. Bảng **E8** so sánh truyền thống vs học sâu theo kích thước biển.
3. Kết quả trên **tập OOD** bên cạnh test cùng nguồn.

## 9. Kế hoạch thực hiện (Sprint 3–6, 5 thành viên)

Ưu tiên: **đóng phần CV truyền thống + pipeline trước** (yêu cầu bắt buộc), sau đó realtime, cuối cùng OCR chữ.

*(Cập nhật §0: các việc dữ liệu của TV5 — dataset v2, tập OOD, nhãn OCR — bị bỏ; TV5 chuyển sang video demo, E4/E6/T3 và kiểm thử chấp nhận.)*

| Sprint | TV1 (Lead · ML · Đánh giá) | TV2 (CV · Frontend) | TV3 (DL · Backend · DevOps) | TV4 (Báo cáo) | TV5 (Dữ liệu · Kiểm thử) |
|---|---|---|---|---|---|
| **S3** (→ 13/11) | `evaluate.py detect` (E1) dựa trên `analyze_run.py`; khung E2 | **`region_features`** (màu, hình học, Hu, HOG) + test | Pipeline ảnh: enhance → YOLO → (xác minh) ; `POST /detect/image` | Ch.2 lý thuyết: **HOG, màu/hình dạng, Hu, Kalman** + YOLO | Dataset v2: 55 ảnh, 23 lỗi nhãn, lớp "Biển chỉ dẫn hướng đi" |
| **S4** (13–20/11) | **LightGBM xác minh** + E3 (tập đặc trưng, LogReg/RF/LGBM) | `tracking.py` Kalman + IoU; trang Ảnh | E3 YOLO (960 / 1280 / ô cắt) trên v2; job video | Ch.3 Dữ liệu (dùng §3), Ch.4 Phương pháp (dùng §6) | Ảnh nền khó; **tập OOD** (≥ 2 video, gán nhãn); crop số |
| **S5** (20–27/11) | **E2 ablation**, **E8** (HOG-SVM, SIFT-BoVW-SVM vs YOLO) | Vùng số → VietOCR; trang Video + Giải thích | Model freeze; webcam WebSocket; Docker GPU | Ch.5 Thực nghiệm | E4, E6; kiểm thử chấp nhận A1–A7 |
| **S6** (27/11–04/12) | Review cuối, phản biện | Video demo | Tag v1.0, README tái lập | Báo cáo cuối, slide | Hồi quy cuối, checklist nộp |

Có thể lùi sang *Could* nếu thiếu thời gian: OCR chữ trên biển + biển phụ (FR-PIPE-09/10/11), ONNX, SAHI.

## 10. Rủi ro

| Rủi ro | Khả năng | Phương án |
|---|---|---|
| Phần CV truyền thống trễ (đang chậm nhất) | Cao | Ưu tiên S3–S4 như §9; E8 độc lập với pipeline nên làm được song song |
| Bộ xác minh không tăng precision | Trung bình | Vẫn là kết quả ablation hợp lệ; phân tích theo nhóm đặc trưng (E3) và theo độ tương đồng |
| Tập OOD chậm (gán nhãn video) | Trung bình | Tối thiểu dùng nhóm "khác train" trong test (đã có công cụ) |
| Biển nhỏ không cải thiện | Trung bình | Báo cáo recall theo track trên video (biển to dần khi tới gần) |
| Thiếu GPU | Thấp | Colab / Kaggle; baseline đã có |

## Tài liệu tham khảo

Đánh số theo [research/README.md](research/README.md) (R1–R24); các tài liệu chính:

- [R1] N. Dalal, B. Triggs. Histograms of Oriented Gradients for Human Detection. CVPR 2005.
- [R2] S. Houben et al. Detection of Traffic Signs in Real-World Images: The German Traffic Sign Detection Benchmark. IJCNN 2013.
- [R3] L. Vieira. Comparing Performance of Preprocessing Techniques for Traffic Sign Recognition Using a HOG-SVM. arXiv:2504.09424, 2024.
- [R5] Fast Traffic Sign Recognition Using Color Segmentation and Deep Convolutional Networks. ACIVS 2016.
- [R7] Traffic Sign Classification using Hybrid HOG-SURF Features and CNN. 2019.
- [R8] R. Sapkota et al. YOLO advances to its genesis: a decadal and comprehensive review of the YOLO series. Artificial Intelligence Review 58:274, 2025.
- [R9] F. C. Akyon, S. O. Altinuc, A. Temizel. Slicing Aided Hyper Inference and Fine-tuning for Small Object Detection. ICIP 2022.
- [R10–R12] Small-object traffic sign detectors on TT100K: improved YOLOv7 (Sensors 2023), STC-YOLO (Sensors 2023), ESA-YOLO (PLOS ONE 2025).
- [R14] Zalo AI Challenge 2020 — Traffic Sign Detection (RetinaNet + image tiling).
- [R15] P. X. Tung et al. Research and Development of a Traffic Sign Recognition Module in Vietnam. ETASR 14(1):12740–12744, 2024.
- [R16] T. T. A. Cu et al. Detection of Vietnamese Traffic Danger and Warning Signs via Deep Learning. JESTEC 19(1):133–145, 2024.
- [R19] C. Ertler et al. The Mapillary Traffic Sign Dataset for Detection and Classification on a Global Scale. ECCV 2020.
- [R20] TSCLIP: Robust CLIP Fine-Tuning for Worldwide Cross-Regional Traffic Sign Recognition. arXiv:2409.15077, 2024.
- [R22] A. Bewley et al. Simple Online and Realtime Tracking. ICIP 2016.
- [R23] S. Šegvić et al. Exploiting temporal and spatial constraints in traffic sign detection from a moving vehicle. Machine Vision and Applications, 2014.
- [R24] G. Ke et al. LightGBM: A Highly Efficient Gradient Boosting Decision Tree. NeurIPS 2017.
- Bộ GTVT. QCVN 41:2019/BGTVT — Quy chuẩn kỹ thuật quốc gia về báo hiệu đường bộ.
- Dataset: Roboflow *merge Real-time Viet Nam Traffic Dtctn 2*, CC BY 4.0.
