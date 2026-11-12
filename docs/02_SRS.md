# UTCI-VISION — Software Requirements Specification (Living SRS)

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.4.1 (dataset đóng băng; phương pháp truyền thống theo kết quả thử nghiệm S3; trạng thái sau triển khai) |
| Ngày | 2026-11-12 |
| Chủ sở hữu tài liệu | TV1 (Tech Lead) — mọi thành viên đều được đề xuất thay đổi |
| Trạng thái | Living document — cập nhật cuối mỗi Sprint Review |
| Liên quan | 00_PHUONG_AN.md, 01_TECHSTACK.md, 03_SPRINT_PLAN.md, 04_BAO_CAO_DE_XUAT.md, docs/adr/, docs/data/DATA_CARD.md, docs/danh_gia/, docs/research/ |
| Repo | https://github.com/HoanBuCon/UTCI-Vision |

## 0. Cách đọc & cập nhật

- **ID cố định** (`FR-DET-02`, `NFR-PERF-01`…); không dùng lại ID, yêu cầu bị bỏ chuyển `Dropped`.
- **Ưu tiên MoSCoW:** `M` Must · `S` Should · `C` Could · `W` Won't (lần này).
- **Trạng thái:** `Approved` → `In Progress` → `Done` · hoặc `Changed` / `Dropped` / `Deferred`.
- **Sprint** = sprint dự kiến; thẻ Trello ghi ID yêu cầu trong mô tả để truy vết.
- Ngưỡng định lượng là mục tiêu ban đầu, hiệu chỉnh bằng số đo thật ở Sprint 1–3; mọi thay đổi ghi Changelog (§10).
- SRS nói *hệ thống phải làm gì*; *làm thế nào* nằm ở 00_PHUONG_AN.md, ADR và code.

## 1. Giới thiệu

### 1.1 Mục đích
Đặc tả yêu cầu cho **Hệ thống nhận diện biển báo giao thông** (tên gọi: **UTCI-Vision**) — hệ thống web nhận diện biển báo
giao thông đường bộ Việt Nam từ ảnh, video và webcam, phục vụ học phần *Thị giác máy tính*.

Theo yêu cầu học phần, hệ thống dùng **hai phương pháp**, là các khâu của **cùng một pipeline** và được đánh giá riêng:
1. **Học sâu** — YOLO11 (phát hiện + phân loại), VietOCR (đọc số / chữ).
2. **Thị giác máy tính truyền thống & trích xuất đặc trưng thủ công** — **tăng cường ảnh thích nghi** (đánh giá chất lượng →
   gamma + CLAHE + lọc song phương) và **theo vết Kalman + IoU** trong pipeline; **trích xuất đặc trưng HOG / màu HSV / SIFT + SVM**
   làm phương pháp phân loại đối chứng (E8); bộ xác minh đặc trưng thủ công + LightGBM giữ như khâu tuỳ chọn (ablation);
   cắt vùng số / chữ cho OCR.

Thiết kế chi tiết và căn cứ nghiên cứu: `04_BAO_CAO_DE_XUAT.md`.

### 1.2 Phạm vi
**Trong phạm vi (v1.0, sau 6 sprint):**
- Phát hiện + phân loại **27 lớp** biển báo: 26 lớp của dataset Roboflow + lớp gộp "Biển báo khác" chứa 6 lớp hiếm
  (< 60 cụm cảnh độc lập — ADR-009); dữ liệu đã lọc → `processed/v1`.
- Đọc giá trị số trên biển (km/h, m, T) và **chữ tiếng Việt** trên biển chính và **biển phụ** khi đủ lớn.
- Web app: ảnh, video (xử lý nền), webcam realtime, thư viện biển báo, chế độ giải thích.
- REST/WebSocket API; đóng gói **Docker Compose** (CPU mặc định, profile GPU).
- 3 notebook fine-tune (Local, Google Colab, Kaggle); công cụ dữ liệu, đánh giá, benchmark chạy local; Makefile + cổng custom qua `.env`.
- Báo cáo môn học, báo cáo mốc từng sprint, slide, video demo.

**Ngoài phạm vi (Won't):** biển ngoài dataset và tên riêng cho các biển trong lớp "Biển báo khác"; đèn tín hiệu, vạch kẻ đường; ứng dụng mobile/nhúng; ADAS thật; nhiều người dùng đồng thời quy mô lớn, đăng nhập/tài khoản; so sánh các đời YOLO khác.

### 1.3 Thuật ngữ

| Thuật ngữ | Nghĩa |
|---|---|
| Detection | Một biển phát hiện được: bbox, lớp, độ tin cậy, `track_id`, giá trị, chữ |
| Track | Chuỗi detection của cùng một biển qua các frame video |
| Bộ xác minh | Mô hình LightGBM đánh giá một detection của YOLO là đúng hay nhầm, trả độ tin cậy đã hiệu chỉnh |
| Biển phụ | Tấm biển chữ nhật nhỏ đặt dưới biển chính, ghi điều kiện (giờ, loại xe, khoảng cách) |
| Tác vụ theo track | Tác vụ chạy nền một/vài lần cho mỗi track (xác minh, đọc số, OCR), không chạy mỗi frame |
| Run | Một lần fine-tune/fit trong notebook, sinh thư mục `<run_id>/` gồm trọng số + `run_record.json` |
| Fine-tune | Huấn luyện tiếp từ trọng số đã train sẵn (pretrained COCO hoặc checkpoint của nhóm) với learning rate nhỏ — không khởi tạo ngẫu nhiên |
| mAP@50 / mAP@50:95 | Mean Average Precision tại IoU 0.5 / trung bình IoU 0.5–0.95 |
| CER / exact match | Tỉ lệ lỗi ký tự / tỉ lệ chuỗi đọc đúng hoàn toàn |
| Flicker rate | Tỉ lệ frame mà nhãn hiển thị của cùng một track bị đổi |

### 1.4 Tài liệu tham khảo
00_PHUONG_AN.md, 01_TECHSTACK.md, 04_BAO_CAO_DE_XUAT.md, ADR-001…009, QCVN 41:2019/BGTVT, repo tham khảo Secret350/Real-time-Traffic-Objects-Detection;
nghiên cứu liên quan (HOG, GTSDB, SAHI, SORT, LightGBM, biển báo Việt Nam…): `docs/research/README.md`.

## 2. Mô tả tổng quan

### 2.1 Bối cảnh sản phẩm

```
Trình duyệt ──HTTP/WS──► web (Nginx + React) ──/api──► api (FastAPI) ──► utci_vision.pipeline
                                                                     └─► models/ (yolo11, verifier, vietocr)
Notebook huấn luyện (Local/Colab/Kaggle) ──<run_id>/──► scripts/import_run.py ──► models/ + experiments/registry.csv
```

### 2.2 Nhóm người dùng

| Nhóm | Nhu cầu |
|---|---|
| Giảng viên / hội đồng | Mở web, thử ảnh/video/webcam; hiểu vai trò từng kỹ thuật (chế độ giải thích); kiểm chứng số liệu tái lập được |
| Người dùng demo | Tải ảnh/video, xem biển được nhận diện kèm tên, ý nghĩa, giá trị, chữ |
| Thành viên nhóm (dev) | Huấn luyện trên nền tảng sẵn có; chạy đánh giá/benchmark bằng một lệnh; triển khai bằng Docker |

### 2.3 Môi trường vận hành
- Máy chạy demo: Windows 10/11 + Docker Desktop (WSL2), hoặc Linux; trình duyệt Chrome/Edge/Firefox bản hiện hành.
- GPU NVIDIA tuỳ chọn (profile `gpu`); **bắt buộc chạy được trên CPU**.
- Phát triển: Python 3.11; torch do từng thành viên tự cài theo GPU (ADR-005); Node.js 22 LTS cho frontend.
- Huấn luyện: GPU cá nhân, Google Colab, Kaggle.

### 2.4 Ràng buộc
- C-01: 6 tuần (6 sprint × 1 tuần, 23/10 → 04/12/2026; sprint chuyển vào thứ Sáu), 5 thành viên.
- C-02: Hệ thống phải dùng **hai phương pháp theo yêu cầu học phần — CV truyền thống / trích xuất đặc trưng truyền thống và học sâu** —
  mỗi phương pháp có vai trò thật trong pipeline và **có kết quả đánh giá riêng** (E2, E8); học máy (LightGBM, SVM) là bộ phân loại trên đặc trưng thủ công.
- C-03: Demo là web chạy bằng Docker.
- C-04: Huấn luyện chỉ qua 3 notebook (Local/Colab/Kaggle) và là **fine-tune** từ trọng số pretrained, không train lại từ đầu; việc khác chạy bằng mã nguồn local.
- C-07: Không tiến trình nào dùng cổng mặc định (8000, 8080, 80, 5173, 8888); mọi cổng cấu hình qua `.env`.
- C-05: Không khoá phiên bản torch/CUDA; chỉ khoá thư viện dùng chung.
- C-08: **Dataset đóng băng ở `processed/v1`** (27 lớp, 5 386 ảnh): không bổ sung ảnh, không gán thêm / sửa nhãn. Video chỉ dùng để
  demo và đo độ ổn định (E6), không đưa vào dataset. Mọi cải thiện đến từ phương pháp.
- C-06: Không commit dataset, trọng số, video vào git; ghi nguồn dataset (CC BY 4.0) và các thư viện/mô hình bên thứ ba (AGPL-3.0 của Ultralytics, VietOCR).

### 2.5 Giả định & phụ thuộc
- A-01: Nhãn dataset đúng ở mức chấp nhận được sau khi TV5 lọc (v1). 23 loại lỗi nhãn có hệ thống đã ghi nhận **không sửa được** (C-08)
  — là hạn chế đã biết của mọi số đo; 55 ảnh thiếu nhãn tiếp tục bị loại.
- A-02: Mỗi tuần có ít nhất ~10 giờ GPU (cá nhân/Colab/Kaggle) cho nhóm.
- A-03: Trọng số pretrained của VietOCR tải được (hoặc nhóm lưu bản sao trên Drive).

## 3. Yêu cầu chức năng

### 3.1 FR-DATA — Dữ liệu (chạy local)

| ID | Yêu cầu | Ưu tiên | Sprint | Trạng thái |
|---|---|---|---|---|
| FR-DATA-01 | Kiểm tra toàn vẹn dataset (ảnh hỏng, nhãn sai định dạng, toạ độ/class ngoài phạm vi, ảnh không nhãn) và xuất báo cáo | M | S1 | Done |
| FR-DATA-02 | Thống kê EDA: phân bố lớp, kích thước box, độ phân giải, số box/ảnh theo tập | M | S1 | Done |
| FR-DATA-03 | Phát hiện ảnh gần trùng (perceptual hash) và gom cụm | M | S1 | Done |
| FR-DATA-04 | Chia lại 70/15/15 phân tầng theo lớp + nguồn, đơn vị là cụm gần trùng; ánh xạ id lớp gốc → 27 lớp (`classes.yaml > raw_ids`) | M | S2 | Done |
| FR-DATA-05 | Đóng gói dataset (zip + checksum + manifest) để upload Google Drive / Kaggle Dataset | M | S2 | Done |
| FR-DATA-06 | `configs/classes.yaml`: tên có dấu, mã QCVN, siêu lớp, màu/hình dạng, ý nghĩa, cờ `has_text`/`has_value` | M | S1–S2 | In Progress (thiếu `meaning`) |
| FR-DATA-07 | Data card: nguồn, giấy phép, quy trình lọc, thống kê trước/sau | M | S2 | Approved |
| FR-DATA-08 | ~~Tập đánh giá đọc số: ≥ 150 crop có nhãn giá trị~~ — không gán thêm nhãn được (C-08) | — | — | Dropped |
| FR-DATA-09 | ~~Tập đánh giá OCR: ≥ 200 crop có nhãn chữ~~ — không gán thêm nhãn được (C-08) | — | — | Dropped |
| FR-DATA-10 | ≥ 1 video đường phố Việt Nam (tự quay / nguồn mở có giấy phép) **chỉ để demo và đo E6** (không gán nhãn, không vào dataset) | S | S4 | Changed |
| FR-DATA-11 | Tập suy giảm nhân tạo (tối, mờ, nhiễu, mưa) sinh từ test | S | S3 | Done (`experiments.DEGRADATIONS`, T4) |
| FR-DATA-12 | ~~**Dataset v2**~~ (C-08): gán nhãn 55 ảnh thiếu nhãn; sửa 23 lỗi nhãn có hệ thống; định nghĩa lại lớp "Biển chỉ dẫn hướng đi" theo QCVN; thêm ảnh nền khó (nhãn rỗng); cập nhật DATA_CARD | — | — | Dropped |
| FR-DATA-13 | ~~Tập test OOD có nhãn~~ (C-08) → thay bằng nhóm ảnh test ít giống train nhất (pHash, `analyze_run.py`) | — | — | Dropped |

### 3.2 FR-TRAIN — Fine-tune (notebook)

| ID | Yêu cầu | Ưu tiên | Sprint | Trạng thái |
|---|---|---|---|---|
| FR-TRAIN-01 | 3 notebook `train_local`, `train_colab`, `train_kaggle` sinh tự động từ một template; không sửa tay `.ipynb` | M | S1 | Done |
| FR-TRAIN-02 | Chế độ `SMOKE` chạy hết mọi ô trong ≤ 10 phút trên mỗi nền tảng | M | S1 | Approved |
| FR-TRAIN-03 | Notebook kiểm tra môi trường (torch/CUDA/GPU) và checksum dữ liệu trước khi train | M | S1 | Done |
| FR-TRAIN-04 | **Fine-tune** YOLO11 từ trọng số pretrained COCO hoặc checkpoint của nhóm (`configs/yolo.yaml`: AdamW, lr nhỏ, `fliplr=0`, tuỳ chọn `freeze`); resume được khi mất phiên | M | S1–S2 | Done (baseline `20261029-1030_yolo11s_960`) |
| FR-TRAIN-05 | Sinh tập xác minh từ dự đoán của YOLO đã fine-tune trên val và fit bộ xác minh LightGBM (+ hiệu chỉnh xác suất) | S | S3 | Done (`fit_verifier.py`, OOF AUC 0,945) |
| FR-TRAIN-06 | ~~Fit SVM chữ số trên HOG~~ — VietOCR đọc số (FR-PIPE-07) | — | — | Dropped |
| FR-TRAIN-07 | Mỗi run sinh `<run_id>/` gồm trọng số + `run_record.json` (cấu hình, metric val, commit, torch/CUDA/GPU, nền tảng) | M | S1 | Done |
| FR-TRAIN-08 | `python scripts/import_run.py` nhập run về `models/<run_id>` (+ `models/current` khi promote), ghi `experiments/registry.csv` | M | S1 | Done |
| FR-TRAIN-09 | Export YOLO sang ONNX để chạy CPU nhanh hơn | C | S5 | Approved |
| FR-TRAIN-10 | Fine-tune VietOCR trên crop biển báo | C | — | Deferred |

### 3.3 FR-PIPE — Pipeline nhận diện

| ID | Yêu cầu | Ưu tiên | Sprint | Trạng thái |
|---|---|---|---|---|
| FR-PIPE-01 | Đánh giá chất lượng frame (độ sáng, tương phản, độ mờ) | M | S2 | Done |
| FR-PIPE-02 | **[CV truyền thống — khâu chính]** Tăng cường thích nghi: gamma tự động, CLAHE, khử nhiễu — chỉ áp dụng khi đánh giá chất lượng yêu cầu; ngưỡng chọn trên **val** | M | S3 | Done (E4: +0,041 recall ảnh tối) |
| FR-PIPE-03 | YOLO11 phát hiện + phân loại 27 lớp | M | S1–S2 | Done (`Detector`) |
| FR-PIPE-04 | **[CV truyền thống]** Tracking (Kalman + ghép IoU), xác nhận track sau ≥ N frame, bỏ phiếu nhãn có trọng số | M | S3 | Done (`tracking.py`) |
| FR-PIPE-05 | Trích đặc trưng thủ công cho mỗi vùng YOLO: tỉ lệ màu HSV (đỏ/xanh/vàng/trắng, viền vs lõi), độ tròn, số đỉnh, solidity, tỉ lệ khung, Hu moments, HOG 32×32 → PCA, độ nét | M | S3 | Done (`verifier.region_features`) |
| FR-PIPE-06 | Bộ xác minh LightGBM trên đặc trưng FR-PIPE-05 (+ điểm/lớp YOLO): loại dương tính giả, thay độ tin cậy bằng xác suất đã hiệu chỉnh. **Mặc định tắt** — T1 không vượt điểm YOLO ở cùng recall; bật khi làm ablation | S | S3 | Done — mặc định tắt (E2) |
| FR-PIPE-07 | Đọc số trên biển có `has_value` (tốc độ, chiều cao, trọng lượng): cắt vùng số (CV) + VietOCR; regex trích số, hợp lệ hoá theo tập giá trị cho phép | M | S3 | Done (định tính) |
| FR-PIPE-08 | Chọn frame tốt nhất của track (diện tích × độ nét) cho đọc số/OCR | S | S4 | Done |
| FR-PIPE-09 | OCR tiếng Việt chữ trên biển `has_text`: cắt vùng chữ, nắn nghiêng (CV) + VietOCR | S | S4 | Done (định tính; lọc độ tin cậy < 0,75) |
| FR-PIPE-10 | Tìm và OCR **biển phụ** dưới biển chính | S | S4 | Done (định tính) |
| FR-PIPE-11 | Hậu xử lý OCR: khớp mờ với từ điển chữ biển báo; regex trích khung giờ, khoảng cách, loại xe | S | S4 | Done |
| FR-PIPE-12 | Tác vụ theo track (xác minh, đọc số, OCR) chạy **bất đồng bộ**, không chặn luồng xử lý frame | M | S4 | Done |
| FR-PIPE-13 | Mỗi khâu bật/tắt được qua `configs/pipeline.yaml` (phục vụ ablation và hạ tải) | M | S2 | Done |
| FR-PIPE-14 | Chế độ debug trả kết quả trung gian từng khâu (ảnh tăng cường, mask, crop, đặc trưng quan trọng, vùng chữ) | S | S4 | Done |
| FR-PIPE-15 | Suy luận cắt lát (SAHI) cho ảnh tĩnh độ phân giải cao | C | S5 | In Progress (`Detector.detect_tiled`, đã đo T3; chưa có tuỳ chọn trên API) |

### 3.4 FR-API — Backend

| ID | Yêu cầu | Ưu tiên | Sprint | Trạng thái |
|---|---|---|---|---|
| FR-API-01 | `GET /api/v1/health`: trạng thái, phiên bản, mô hình đã nạp, thiết bị (CPU/GPU) | M | S1 | Done |
| FR-API-02 | `GET /api/v1/classes`: 27 lớp kèm tên, siêu lớp, ý nghĩa, ảnh minh hoạ | M | S2 | Done (thiếu nội dung `meaning` — TV4) |
| FR-API-03 | `POST /api/v1/detect/image`: nhận ảnh, trả JSON detection (+ ảnh đã vẽ nếu yêu cầu, + debug) | M | S2 | Done |
| FR-API-04 | `POST /api/v1/jobs/video` tạo job xử lý nền; `GET /api/v1/jobs/{id}` trả tiến độ, kết quả, link video đã vẽ, thống kê biển xuất hiện | M | S3 | Done |
| FR-API-05 | `WS /api/v1/stream`: nhận frame JPEG, trả JSON detection; back-pressure (một frame đang xử lý / client) | M | S4 | Done (CPU 9,3 FPS) |
| FR-API-06 | Giới hạn kích thước upload (ảnh ≤ 10 MB, video ≤ 200 MB, ≤ 3 phút) và báo lỗi rõ ràng | M | S3 | Done |
| FR-API-07 | Mô hình nạp một lần khi khởi động; thiếu trọng số thì `health` báo rõ, không crash | M | S2 | Done |

### 3.5 FR-WEB — Frontend

| ID | Yêu cầu | Ưu tiên | Sprint | Trạng thái |
|---|---|---|---|---|
| FR-WEB-01 | Trang **Ảnh**: tải/kéo-thả ảnh, hiển thị box + nhãn tiếng Việt, danh sách biển (tên, ý nghĩa, độ tin cậy, giá trị, chữ) | M | S2 | Done |
| FR-WEB-02 | Trang **Video**: tải video, thanh tiến độ, xem/tải video kết quả, bảng biển đã xuất hiện | M | S3 | Done |
| FR-WEB-03 | Trang **Webcam**: stream camera qua WebSocket, vẽ kết quả lên canvas, hiện FPS; panel "biển vừa gặp" | M | S4 | Done (chưa thử với camera thật) |
| FR-WEB-04 | Trang **Thư viện biển báo**: 27 lớp theo siêu lớp, ý nghĩa, ví dụ | S | S3 | Done |
| FR-WEB-05 | Chế độ **Giải thích**: hiển thị kết quả trung gian từng khâu cho một ảnh | S | S4 | Done |
| FR-WEB-06 | Giao diện tiếng Việt, dùng được trên màn hình laptop và điện thoại | M | S3 | Done |

### 3.6 FR-DEP — Triển khai

| ID | Yêu cầu | Ưu tiên | Sprint | Trạng thái |
|---|---|---|---|---|
| FR-DEP-01 | `make up` (hoặc `make up-gpu`) khởi động `api` + `web`; truy cập `http://localhost:${UTCI_WEB_PORT}` (mặc định 18080) | M | S1–S2 | Done |
| FR-DEP-02 | Image `api` mặc định chạy CPU; profile `gpu` dùng GPU NVIDIA qua NVIDIA Container Toolkit | M | S2 / S5 | Approved |
| FR-DEP-03 | Trọng số mount từ `./models`; cấu hình qua biến môi trường (`.env`) | M | S2 | Approved |
| FR-DEP-04 | Healthcheck cho container `api` | S | S5 | Approved |
| FR-DEP-05 | Cổng của mọi tiến trình (API, web, Vite dev/preview, Jupyter) đọc từ `.env`; mặc định 18100 / 18080 / 15173 / 18888 | M | S1 | Done |
| FR-DEP-06 | Makefile chỉ cho DevOps: môi trường, CI (`make ci`), Docker (`make help`); việc nghiệp vụ gọi trực tiếp `scripts/` | M | S1 | Done |

### 3.7 FR-EVAL — Đánh giá (chạy local)

| ID | Yêu cầu | Ưu tiên | Sprint | Trạng thái |
|---|---|---|---|---|
| FR-EVAL-01 | Đánh giá toàn hệ thống trên test v1 **và tập OOD**: P, R, mAP@50, mAP@50:95, macro-F1, AP theo lớp và theo kích thước; **CI 95% bootstrap theo ảnh**; P/R tại điểm vận hành; theo độ tương đồng với train (E1) — công cụ `scripts/analyze_run.py` | M | S3 | Done (`S3_danh_gia_he_thong.md`) |
| FR-EVAL-02 | Ablation: YOLO thuần → + tăng cường → + xác minh → + tracking (E2) | M | S5 | Done |
| FR-EVAL-03 | So sánh cấu hình YOLO11: `imgsz` 960 / 1280 / huấn luyện trên ô cắt (± `freeze`); bộ xác minh LogReg/RF/LightGBM và **tập đặc trưng** (màu / +hình học / +HOG / đầy đủ) (E3) | M | S3–S4 | In Progress (bộ xác minh: LGBM / LogReg / RF; imgsz: T3) |
| FR-EVAL-04 | Độ bền trên tập suy giảm ± tăng cường (E4) | M | S3 | Done (tối, nhiễu, mờ) |
| FR-EVAL-05 | Đọc số và chữ (E5): **định tính** — ví dụ đọc đúng / sai trên crop có sẵn; không đo được accuracy / CER vì không có nhãn chữ (C-08) | C | S5 | Changed |
| FR-EVAL-06 | Flicker rate trên video demo ± tracking (E6) — không cần nhãn: tỉ lệ frame mà nhãn hiển thị của cùng một track bị đổi | S | S4 | In Progress (công cụ `evaluate.py flicker`; chờ video demo) |
| FR-EVAL-07 | Benchmark FPS/độ trễ: pipeline local (GPU/CPU) và qua API/WebSocket | M | S1, S4, S5 | In Progress (detector: 54,6 FPS) |
| FR-EVAL-08 | `experiments/registry.csv` ghi mọi run và mọi lần đánh giá (mã E#, commit, cấu hình, môi trường, metric) | M | S1 | Done |
| FR-EVAL-09 | **So sánh truyền thống vs học sâu (E8)**: phân loại crop biển bằng HOG + SVM, SIFT-BoVW + SVM và YOLO; accuracy / macro-F1 theo nhóm kích thước (< 16, 16–32, 32–64, ≥ 64 px) kèm CI, thời gian / crop | M | S3 | Done (`compare_traditional_dl.py`) |
| FR-EVAL-11 | Biển nhỏ **không cần dữ liệu mới** (T3): suy luận imgsz 1280 và cắt lát (SAHI) với trọng số hiện có; recall biển < 16 px, FPS | S | S4 | Done (imgsz 1280 làm mặc định) |
| FR-EVAL-10 | Ma trận nhầm lẫn và P/R theo lớp tính tại điểm vận hành (conf của pipeline); không dùng ma trận mặc định của Ultralytics 8.4 (ghép cả dự đoán conf 0,001) làm bằng chứng | M | S3 | Done (`analyze_run.py`) |

### 3.8 FR-DOC — Báo cáo & bàn giao

| ID | Yêu cầu | Ưu tiên | Sprint | Trạng thái |
|---|---|---|---|---|
| FR-DOC-01 | Báo cáo mốc mỗi sprint (1–2 trang) | M | S1–S6 | Approved |
| FR-DOC-02 | Báo cáo cuối kỳ (Word hoặc LaTeX — TBD-2) theo luồng pipeline, kèm E1–E7 | M | S6 | Approved |
| FR-DOC-03 | Slide + video demo 3–5 phút | M | S6 | Approved |
| FR-DOC-04 | README: cài đặt (tự cài torch), huấn luyện bằng notebook, chạy Docker, tái lập số liệu | M | S6 | Approved |

## 4. Yêu cầu phi chức năng

| ID | Yêu cầu | Mục tiêu ban đầu | Ưu tiên |
|---|---|---|---|
| NFR-ACC-01 | Phát hiện + phân loại trên test v1 (hệ thống đầy đủ) | mAP@50 ≥ 0.88; mAP@50:95 ≥ 0.68 (baseline YOLO: 0,89–0,91 / 0,68 — không được giảm khi thêm khâu) | M |
| NFR-ACC-02 | ~~Precision ≥ 0.90 sau bộ xác minh~~ — T1: không đạt (0,878 với ngưỡng val; không khác biệt ở cùng recall). Thay bằng NFR-ACC-07 | — | Dropped |
| NFR-ACC-05 | Precision trên nhóm ảnh test ít giống train nhất (pHash ≥ 15) — báo cáo kèm CI, không đặt ngưỡng (không có dữ liệu mới để cải thiện) | Báo cáo (baseline 0,758) | S |
| NFR-ACC-06 | Recall biển < 16 px tại điểm vận hành (bằng T3, không train lại) | ≥ 0.70 (baseline 0,62) | S |
| NFR-ACC-07 | Recall trên ảnh test làm tối (γ 3,5) khi bật tăng cường thích nghi | ≥ 0.80 (không tăng cường 0,686; T4: 0,822) và không giảm recall trên ảnh gốc quá 0,005 | M |
| NFR-ACC-03 | ~~Đọc đúng giá trị số ≥ 85%~~ — không đo được vì không có nhãn giá trị (C-08) | — | Dropped |
| NFR-ACC-04 | ~~OCR chữ ≥ 80% exact match~~ — không đo được vì không có nhãn chữ (C-08) | — | Dropped |
| NFR-PERF-01 | Webcam qua web, GPU RTX 4060 Laptop, frame 960×540 | ≥ 20 FPS hiển thị, độ trễ p95 ≤ 120 ms | M |
| NFR-PERF-02 | Ảnh tĩnh qua API, Docker CPU (4 nhân) | ≤ 1,5 s/ảnh (không tính OCR); ≤ 3 s có OCR | M |
| NFR-PERF-03 | Xử lý video nền, Docker GPU | ≥ 1× thời gian thực với video 720p | S |
| NFR-PERF-04 | Tác vụ theo track không làm giảm FPS luồng chính quá 10% | ≤ 10% | M |
| NFR-REP-01 | Mọi số liệu trong báo cáo truy được về registry (run_id, commit, môi trường) và có CI 95% cho chỉ số tổng | 100% | M |
| NFR-REP-02 | Máy mới: cài môi trường dev theo README (đã có torch) | ≤ 30 phút | M |
| NFR-REP-03 | Máy mới: chạy demo bằng Docker (đã có Docker + trọng số) | ≤ 15 phút | M |
| NFR-MNT-01 | Python theo `ruff`; frontend `tsc --noEmit` strict; tham số ở `configs/` | CI xanh | M |
| NFR-MNT-02 | Unit test cho logic xử lý (nhãn, metric, tracking, hậu xử lý OCR, schema API) | ≥ 30 test, < 60 s | S |
| NFR-MNT-03 | `requirements.txt` khoá phiên bản thư viện dùng chung, **không** chứa torch/CUDA | Kiểm tra trong CI | M |
| NFR-MNT-04 | Không hard-code cổng/đường dẫn; không dùng cổng mặc định | Test `Ports`, `.env.example` | M |
| NFR-USE-01 | Giao diện tiếng Việt có dấu; người lần đầu dùng thao tác được không cần hướng dẫn | — | M |
| NFR-SEC-01 | API chỉ nhận định dạng ảnh/video hợp lệ, giới hạn kích thước; không lưu file người dùng quá 24 giờ | — | S |
| NFR-LEG-01 | Ghi nguồn dataset (CC BY 4.0), Ultralytics (AGPL-3.0), VietOCR trong README và báo cáo | — | M |

## 5. Giao diện bên ngoài

### 5.1 REST / WebSocket (tiền tố `/api/v1`) — schema đã chốt 29/10/2026 (S1)

Nguồn chuẩn: `src/utci_vision/api/schemas.py` (backend) ↔ `web/src/api/types.ts` (frontend); `tests/test_api_contract.py` kiểm tra hai bên luôn khớp tên trường. Đổi schema = CHANGE-REQ (§9).

| Phương thức | Đường dẫn | Mô tả |
|---|---|---|
| GET | `/health` | `{status, version, device, models: {detector, verifier, ocr}}` |
| GET | `/classes` | Danh sách 27 lớp |
| POST | `/detect/image?annotate=true&debug=false` | multipart `file` → `DetectResponse` |
| POST | `/jobs/video` | multipart `file` → `{job_id}` |
| GET | `/jobs/{job_id}` | `{status, progress, result_video_url, summary}` |
| WS | `/stream` | client gửi JPEG nhị phân; server trả `DetectResponse` dạng JSON |

```json
{
  "frame": 120,
  "image_size": [960, 540],
  "latency_ms": {"total": 24.1, "yolo": 12.3},
  "detections": [
    {"bbox": [812, 233, 846, 268], "class_id": 24, "class_name": "Giới hạn tốc độ",
     "superclass": "prohibitory", "score": 0.94, "verified": true, "track_id": 7,
     "value": {"number": 50, "unit": "km/h"},
     "text": null,
     "sub_sign": {"text": "6h-22h", "parsed": {"time_ranges": [["06:00", "22:00"]]}}}
  ]
}
```

### 5.2 Lệnh local

```bash
# DevOps (Makefile)
make env && make install && make check-env && make ci
make up                                            # hoặc make up-gpu
# Nghiệp vụ (gọi trực tiếp)
python scripts/data.py audit --dedup               # split | crops | package
python scripts/import_run.py <thư-mục-run> --promote
python scripts/evaluate.py detect --split test     # benchmark
python scripts/build_notebooks.py
python -m utci_vision.api --reload                 # dev; web: cd web && npm run dev
```

## 6. Mô hình dữ liệu

- Nhãn: định dạng YOLO `class cx cy w h` (chuẩn hoá).
- `processed/v1/manifest.csv`: `image, split, resolution, dup_cluster, n_boxes, classes` (id mô hình), `raw_classes` (id gốc), `new_split`.
- `models/<run_id>/run_record.json`: `run_id, platform, model, config, metrics, commit, torch, cuda, gpu, dataset_version, dataset_sha256, started_at, duration_s`.
- `experiments/registry.csv`: `run_id, exp, date, author, platform, commit, torch, cuda, gpu, config, dataset_version, metrics_json, notes`.
- `configs/classes.yaml`: `id, name, name_vi, superclass (prohibitory|warning|mandatory|info|other), qcvn, meaning, has_text, has_value, value_unit, raw_ids`.

## 7. Tiêu chí chấp nhận v1.0

1. Mọi yêu cầu `M` ở trạng thái `Done` hoặc `Changed` có chấp thuận của nhóm.
2. Có bảng E1 (test v1 + nhóm ảnh ít giống train), **E2 (đóng góp từng khâu, gồm tăng cường và xác minh)**, **E4 (tăng cường trên ảnh xấu)**,
   **E8 (truyền thống vs học sâu)** và ≥ 1 trong E3, E6, T3 — truy vết được về registry.
3. Trên một máy sạch có Docker: `docker compose --profile cpu up` → kịch bản A1–A6 (Phụ lục A) đạt.
4. Cả 3 notebook chạy `SMOKE` thành công trên nền tảng tương ứng.
5. Báo cáo, slide, video demo, README hoàn chỉnh.

## 8. Vấn đề mở (TBD)

| # | Vấn đề | Hạn chốt | Người quyết |
|---|---|---|---|
| ~~TBD-1~~ | Gộp/loại lớp hiếm → **đã chốt 29/10/2026**: gộp 6 lớp vào "Biển báo khác" (ADR-009) | S1 | TV1 + TV5 |
| TBD-2 | Báo cáo bằng Word hay LaTeX? | Planning S1 | TV4 |
| TBD-3 | `imgsz` 960 / 1280 / huấn luyện ô cắt cho biển nhỏ (theo E3 + ngân sách FPS). Đã có: `yolo11s` 960 đạt 0,89–0,91 mAP@50, 55 FPS | Review S4 | TV3 |
| TBD-4 | Tìm biển phụ bằng CV đủ tốt hay phải gán nhãn lớp "biển phụ" cho YOLO? | Review S3 | TV1 + TV2 |
| TBD-5 | Nền tảng "chính thức" để lấy số liệu báo cáo (đề xuất: huấn luyện trên Colab T4 như baseline; đánh giá trên RTX 4060 Laptop) | Review S3 | TV1 |
| ~~TBD-6~~ | Tách / sửa lớp "Biển chỉ dẫn hướng đi" → **không làm** (C-08); báo cáo là lớp yếu do định nghĩa lớp | S3 | Nhóm |

## 9. Quản lý thay đổi yêu cầu

1. Tạo thẻ Trello từ mẫu **CHANGE-REQ** (cột Backlog): yêu cầu liên quan, thay đổi, lý do, ảnh hưởng.
2. Thảo luận ở Sync giữa sprint hoặc Sprint Review; TV1 chốt.
3. Cập nhật bảng yêu cầu (trạng thái `Changed`), ghi Changelog; thẻ được nhận vào **sprint kế tiếp** (trừ lỗi chặn).

## 10. Changelog

| Phiên bản | Ngày | Người sửa | Thay đổi |
|---|---|---|---|
| 0.1.0 | 2026-10-22 | TV1 | Bản nháp đầu (3 chế độ tách rời) |
| 1.4.1 | 2026-11-12 | TV1 | Cập nhật trạng thái sau khi cài đặt pipeline đầy đủ, API, web, đánh giá E1/E2/E4/T3 (`docs/danh_gia/S3_danh_gia_he_thong.md`) |
| 1.4.0 | 2026-11-12 | TV1 | Dataset đóng băng (C-08): FR-DATA-08/09/12/13 Dropped, FR-DATA-10 chỉ để demo; theo thử nghiệm S3 (T1, E8, T4): tăng cường thích nghi + tracking là khâu CV truyền thống chính (FR-PIPE-02/04), bộ xác minh thành tuỳ chọn mặc định tắt (FR-PIPE-06, FR-TRAIN-05 → S), E8 Done; NFR-ACC-02/03/04 Dropped, thêm NFR-ACC-07 (ảnh tối) và FR-EVAL-11 (T3); E5 định tính |
| 1.3.0 | 2026-11-11 | TV1 | Theo `04_BAO_CAO_DE_XUAT.md`: nêu rõ **hai phương pháp theo yêu cầu học phần** (§1.1, C-02); thêm FR-DATA-12 (dataset v2), FR-DATA-13 (tập OOD), FR-EVAL-09 (E8 truyền thống vs học sâu), FR-EVAL-10, NFR-ACC-05/06; FR-PIPE-05/06, FR-EVAL-01/03 Changed; nâng NFR-ACC-01/02 theo baseline; cập nhật trạng thái Done của S1–S2; cập nhật TBD-3/5, thêm TBD-6; ma trận truy vết S3–S5 theo kế hoạch mới |
| 1.2.0 | 2026-10-23 | TV1 | Bỏ SVM chữ số: VietOCR + regex đọc số (FR-PIPE-07, FR-DATA-08, FR-EVAL-05 Changed; FR-TRAIN-06 Dropped) |
| 1.1.0 | 2026-10-22 | TV1 | Huấn luyện = fine-tune từ pretrained (C-04, FR-TRAIN-04); cổng custom qua `.env` + Makefile (C-07, FR-DEP-05/06, NFR-MNT-04); thêm repo |
| 1.0.0 | 2026-10-22 | TV1 | Viết lại theo phương án đã duyệt: một pipeline YOLO11 + CV/ML/OCR theo track; web + Docker; OCR tiếng Việt & biển phụ; 3 notebook huấn luyện; chính sách không khoá torch/CUDA |

## Phụ lục A — Kịch bản kiểm thử chấp nhận

| # | Kịch bản | Kết quả mong đợi |
|---|---|---|
| A1 | `make up` trên máy sạch (CPU), mở `localhost:18080` | Web hiển thị; `/api/v1/health` báo đủ mô hình |
| A2 | Trang Ảnh: tải ảnh test có 3 biển | ≤ 1,5 s (CPU) hiện 3 box đúng lớp, tên + ý nghĩa tiếng Việt |
| A3 | Ảnh chụp gần biển "Giới hạn tốc độ 50" có biển phụ "6h–22h" | Hiện "50 km/h" và chữ biển phụ đã phân tích |
| A4 | Ảnh tối (gamma 2.5) | Có tăng cường thì phát hiện nhiều biển hơn; trang Giải thích hiện ảnh trước/sau |
| A5 | Trang Video: video đường phố 1 phút | Job hoàn tất, video kết quả không nhấp nháy nhãn, bảng thống kê biển |
| A6 | Trang Webcam (profile GPU) | ≥ 20 FPS hiển thị, chạy ổn định ≥ 5 phút |
| A7 | `python scripts/evaluate.py --split test` | Bảng E1 khớp số trong báo cáo |

## Phụ lục B — Ma trận truy vết (Yêu cầu → Sprint)

| Sprint | Yêu cầu chính |
|---|---|
| S1 | FR-DATA-01/02/03/06, FR-TRAIN-01/02/03/04/07/08, FR-PIPE-03, FR-API-01, FR-DEP-01/05/06, FR-EVAL-07/08 |
| S2 | FR-DATA-04/05/06/07/08/09, FR-PIPE-01/02/04/05/13, FR-API-02/03/07, FR-WEB-01, FR-DEP-02/03, FR-EVAL-03 |
| S3 | FR-PIPE-02/05, FR-DATA-12, FR-API-03, FR-EVAL-01/03, FR-DATA-08/09/10, FR-PIPE-07 |
| S4 | FR-TRAIN-05, FR-PIPE-04/06/08/12, FR-DATA-13, FR-API-04/05/06, FR-WEB-01/02/03, FR-EVAL-03/04/07, FR-DATA-11 |
| S5 | FR-EVAL-02/05/06/07/09, FR-PIPE-09/10/11/14, FR-WEB-04/05/06, FR-TRAIN-09, FR-PIPE-15, FR-DEP-02/04, bản nháp báo cáo |
| S6 | FR-DOC-02/03/04, ổn định & bàn giao |
| S1–S6 | FR-DOC-01 |
