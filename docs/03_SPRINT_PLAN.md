# UTCI-VISION — Nhận diện biển báo giao thông — Kế hoạch 6 Sprint

| Thuộc tính | Giá trị |
|---|---|
| Thời gian | 23/10/2026 → 04/12/2026 (6 sprint × 7 ngày) |
| Quy mô | 5 thành viên |
| Nguồn dữ liệu kế hoạch | planning/sprint_plan.json (sửa file này rồi chạy lại build_docs.py / trello_import.py) |
| Trello | https://trello.com/b/BcQ48yqk/faketime-traffic-signs-cant-detect |
| Repo | https://github.com/HoanBuCon/UTCI-Vision |

> Tài liệu này được sinh tự động từ `planning/sprint_plan.json`. Đừng sửa tay — sửa JSON rồi chạy lại script.

## 1. Phân vai

| Mã | Thành viên | Vai trò | Trọng tâm |
|---|---|---|---|
| TV1 | TV1 | Tech Lead · ML · Đánh giá | Kiến trúc, ADR, review; bộ xác minh LightGBM, hậu xử lý OCR (regex số, từ điển chữ); thí nghiệm & ablation |
| TV2 | TV2 | CV truyền thống · Frontend · Hỗ trợ báo cáo | Tăng cường ảnh, đặc trưng vùng, tracking, cắt vùng số / dòng chữ / biển phụ; React |
| TV3 | TV3 | Dev chính · DL · Backend · DevOps | Fine-tune YOLO11, 3 notebook, pipeline, FastAPI + WebSocket, VietOCR, Docker, Makefile, CI |
| TV4 | TV4 | Báo cáo · Slide · Video | Khung & các chương báo cáo, báo cáo mốc sprint, nội dung ý nghĩa biển, từ điển chữ biển phụ |
| TV5 | TV5 | Dữ liệu · Kiểm thử | Lọc, chia lại, đóng gói dữ liệu; nhãn đánh giá OCR (giá trị số + chữ); video thử; benchmark; kiểm thử chấp nhận |

Nguyên tắc: mỗi thẻ có **một** người chịu trách nhiệm chính; thẻ `ALL` là hoạt động chung của team. Người chịu trách nhiệm có thể nhờ người khác hỗ trợ nhưng là người kéo thẻ sang Hoàn thành.

## 2. Lộ trình tổng quan

| Sprint | Thời gian | Chủ đề | Mục tiêu |
|---|---|---|---|
| S1 | 23/10/2026 – 30/10/2026 | **Khởi động & nền tảng** | Cả 5 người chạy được môi trường (torch tự cài, cổng custom); dữ liệu được audit + duyệt; 3 notebook chạy SMOKE; có fine-tune baseline YOLO11s và benchmark FPS; khung API + web + Docker chạy được; chốt schema JSON. |
| S2 | 30/10/2026 – 06/11/2026 | **Dữ liệu v1 & các khối lõi** | Có processed/v1 sạch (đã chia lại, đóng gói lên Drive/Kaggle); YOLO11 fine-tune trên v1 với cấu hình tốt nhất (E3); tăng cường CV + đặc trưng vùng; pipeline khung + API ảnh; trang Ảnh chạy trong Docker. |
| S3 | 06/11/2026 – 13/11/2026 | **MVP: pipeline đầy đủ trên ảnh + video** | Ảnh tĩnh đi qua đủ các khâu (enhance → YOLO → xác minh LightGBM → đọc số bằng VietOCR + regex); video xử lý nền với tracking; trang Video + Thư viện; E1 sơ bộ. |
| S4 | 13/11/2026 – 20/11/2026 | **Realtime & OCR tiếng Việt** | Webcam qua WebSocket ≥ 20 FPS (GPU); tác vụ theo track chạy nền; OCR chữ tiếng Việt + biển phụ; trang Webcam; E4 độ bền, E5 đọc số/chữ. |
| S5 | 20/11/2026 – 27/11/2026 | **Tối ưu, model freeze & bản nháp báo cáo** | Đạt mục tiêu hiệu năng; chốt mô hình (fine-tune cuối trên nền tảng chính thức); ablation E2 + E6 đầy đủ; kiểm thử chấp nhận lần 1; bản nháp báo cáo đầy đủ. |
| S6 | 27/11/2026 – 04/12/2026 | **Ổn định, báo cáo cuối & bảo vệ** | Bản nộp cuối: code tag v1.0 tái lập được (make up), báo cáo PDF, slide, video demo; diễn tập thuyết trình. |

Các mốc quan trọng: **cuối S1** chốt phương án + baseline · **cuối S2** dataset v1 sạch · **cuối S3** MVP 3 chế độ end-to-end · **cuối S4** realtime + thí nghiệm chất lượng · **giữa S5** model freeze · **S6** code freeze, nộp bài, bảo vệ. Mỗi sprint có báo cáo mốc (TV4).

## 3. Phân bổ story point theo sprint

| Sprint | TV1 | TV2 | TV3 | TV4 | TV5 | ALL | Tổng |
|---|---|---|---|---|---|---|---|
| S1 | 6 | 5 | 11 | 6 | 10 | 2 | 40 |
| S2 | 5 | 9 | 10 | 8 | 7 | 2 | 41 |
| S3 | 9 | 10 | 10 | 6 | 7 | 2 | 44 |
| S4 | 6 | 10 | 8 | 6 | 5 | 2 | 37 |
| S5 | 7 | 7 | 10 | 6 | 5 | 2 | 37 |
| S6 | 3 | 5 | 5 | 8 | 2 | 4 | 27 |
| **Tổng** | **36** | **46** | **54** | **40** | **36** | **14** | **226** |

Thang điểm Fibonacci (1, 2, 3, 5, 8): 1 điểm ≈ nửa ngày làm việc tập trung. Mỗi người ~5–11 điểm/sprint (sinh viên học song song nhiều môn), chừa ~20% cho review, họp và việc phát sinh. Sau Sprint 1, hiệu chỉnh theo velocity thực tế.

## 4. Cấu trúc bảng Trello

| Cột (List) | Mục đích |
|---|---|
| 📌 Thông tin dự án | Link tài liệu, Definition of Done, quy ước Git, phân vai |
| 🧊 Backlog | Ý tưởng / yêu cầu Could-have / CHANGE-REQ chưa xếp sprint |
| Sprint 1 (23/10 - 30/10) - Bài KT 1 | Thẻ đã lên kế hoạch cho sprint này; kéo sang Đang làm khi bắt đầu |
| Sprint 2 (30/10 - 06/11) | Thẻ đã lên kế hoạch cho sprint này; kéo sang Đang làm khi bắt đầu |
| Sprint 3 (06/11 - 13/11) | Thẻ đã lên kế hoạch cho sprint này; kéo sang Đang làm khi bắt đầu |
| Sprint 4 (13/11 - 20/11) | Thẻ đã lên kế hoạch cho sprint này; kéo sang Đang làm khi bắt đầu |
| Sprint 5 (20/11 - 27/11) | Thẻ đã lên kế hoạch cho sprint này; kéo sang Đang làm khi bắt đầu |
| Sprint 6 (27/11 - 04/12) | Thẻ đã lên kế hoạch cho sprint này; kéo sang Đang làm khi bắt đầu |
| 🏗️ Đang làm | Thẻ đang thực hiện (mỗi người tối đa 2 thẻ cùng lúc) |
| 🔨 Đang sửa | Thẻ bị trả về từ Review / QA, đang sửa |
| 👀 Review / QA | Đã mở PR, chờ review hoặc kiểm thử |
| ✅ Hoàn thành | Đạt Definition of Done |

Nhãn: `TV1`, `TV2`, `TV3`, `TV4`, `TV5`, `Team`, `Data`, `CV`, `ML`, `DL`, `OCR`, `Backend`, `Frontend`, `DevOps`, `Eval`, `Report`, `Must`, `Should`, `Could`, `CHANGE-REQ`.

Mỗi thẻ có: tên `[S#][TV#] Tên việc`, mô tả (mục tiêu, yêu cầu SRS liên quan, story point), checklist các việc con, ngày bắt đầu/hạn = đầu/cuối sprint, nhãn người phụ trách + mảng + ưu tiên.

## Sprint 1 — Khởi động & nền tảng (23/10/2026 – 30/10/2026)

**Mục tiêu:** Cả 5 người chạy được môi trường (torch tự cài, cổng custom); dữ liệu được audit + duyệt; 3 notebook chạy SMOKE; có fine-tune baseline YOLO11s và benchmark FPS; khung API + web + Docker chạy được; chốt schema JSON.

**Sản phẩm bàn giao cuối sprint:**

- Repo UTCI-Vision: develop/main, CI xanh, Makefile, pre-commit
- Mọi thành viên: make check-env OK (torch theo GPU riêng)
- Báo cáo audit/EDA + excluded.txt bản đầu; classes.yaml đã xác nhận
- 3 notebook SMOKE OK trên Local/Colab/Kaggle; fine-tune baseline YOLO11s trên dữ liệu gốc + import-run
- Benchmark FPS YOLO11s (mốc S1); make up mở được web ở cổng 18080 với /health, /classes
- Khung báo cáo + Chương 1 + báo cáo mốc S1

| # | Thẻ | Phụ trách | Điểm | Ưu tiên | Yêu cầu SRS |
|---|---|---|---|---|---|
| 1 | Sprint 1 Planning & Kickoff | ALL | 1 | Must | - |
| 2 | Đưa khung mã nguồn lên repo + CI | TV1 | 3 | Must | NFR-MNT-01, NFR-MNT-03, FR-DEP-06 |
| 3 | Workshop phương án + chốt schema JSON API | TV1 | 2 | Must | FR-API-03 |
| 4 | Smoke test notebook trên Kaggle | TV1 | 1 | Must | FR-TRAIN-02 |
| 5 | Hiện thực Detector + validate | TV3 | 3 | Must | FR-PIPE-03, FR-TRAIN-04 |
| 6 | 3 notebook fine-tune: SMOKE local + hướng dẫn | TV3 | 3 | Must | FR-TRAIN-01, FR-TRAIN-02, FR-TRAIN-03, FR-TRAIN-07, FR-TRAIN-08 |
| 7 | Fine-tune baseline YOLO11s trên dữ liệu gốc | TV3 | 3 | Must | FR-TRAIN-04 |
| 8 | Khung API + web + Docker chạy được (cổng custom) | TV3 | 2 | Must | FR-API-01, FR-DEP-01, FR-DEP-05 |
| 9 | Cài môi trường + khung frontend dev | TV2 | 2 | Must | NFR-REP-02 |
| 10 | Spike CV: đánh giá chất lượng & tăng cường ảnh | TV2 | 3 | Must | FR-PIPE-01, FR-PIPE-02 |
| 11 | Audit, EDA & duyệt dữ liệu | TV5 | 5 | Must | FR-DATA-01, FR-DATA-02, FR-DATA-03 |
| 12 | Xác nhận classes.yaml (QCVN, has_value, has_text) | TV5 | 2 | Must | FR-DATA-06 |
| 13 | Smoke test notebook trên Colab + benchmark FPS mốc S1 | TV5 | 3 | Must | FR-TRAIN-02, FR-EVAL-07 |
| 14 | Khung báo cáo & Chương 1 | TV4 | 5 | Must | FR-DOC-02 |
| 15 | Báo cáo mốc S1 | TV4 | 1 | Must | FR-DOC-01 |
| 16 | Sprint 1 Review & Retro | ALL | 1 | Must | - |

### Chi tiết công việc Sprint 1

#### 1.1 [ALL] Sprint 1 Planning & Kickoff

Đọc tài liệu, thống nhất cách làm việc, chốt phạm vi.

- [ ] Đọc 00_PHUONG_AN, 01_TECHSTACK, 02_SRS; ghi câu hỏi
- [ ] Thống nhất DoD, quy ước Git, cổng custom
- [ ] Chốt TBD-2: Word hay LaTeX
- [ ] Gán tên thật TV1..TV5, mời vào board + repo

#### 1.2 [TV1] Đưa khung mã nguồn lên repo + CI

Repo https://github.com/HoanBuCon/UTCI-Vision (công khai, đã có LICENSE Apache-2.0 trên main).

- [ ] git init → remote add → pull main (giữ LICENSE) → push khung (không kèm dataset/.env)
- [ ] Tạo nhánh develop; branch protection main/develop, bắt buộc PR + CI
- [ ] GitHub Actions: python + web + compose config xanh
- [ ] PR template, CODEOWNERS

#### 1.3 [TV1] Workshop phương án + chốt schema JSON API

Thống nhất hợp đồng giữa backend (TV3) và frontend (TV2).

- [ ] Trình bày pipeline + kế hoạch thí nghiệm E1–E7
- [ ] Rà api/schemas.py ↔ web/src/api/types.ts
- [ ] Chốt ADR-002

#### 1.4 [TV1] Smoke test notebook trên Kaggle

SMOKE=True, Kaggle Dataset tạm từ dữ liệu gốc.

- [ ] Tạo Kaggle Dataset riêng tư
- [ ] Run all với SMOKE=True
- [ ] Tải zip kết quả, python scripts/import_run.py <thư-mục-run>

#### 1.5 [TV3] Hiện thực Detector + validate

detector.py: phần còn TODO.

- [ ] Detector.detect (batch, half khi GPU)
- [ ] validate(): mAP + AP theo lớp
- [ ] Test với trọng số pretrained COCO

#### 1.6 [TV3] 3 notebook fine-tune: SMOKE local + hướng dẫn

Sửa _template.py -> python scripts/build_notebooks.py.

- [ ] SMOKE train_local OK trên RTX 4060
- [ ] Hướng dẫn upload dữ liệu Drive/Kaggle
- [ ] Kiểm tra python scripts/import_run.py ghi registry

#### 1.7 [TV3] Fine-tune baseline YOLO11s trên dữ liệu gốc

Từ pretrained COCO, imgsz 640, để có mốc so sánh sớm (tương đương repo tham khảo).

- [ ] Chạy notebook (Kaggle/Colab)
- [ ] python scripts/import_run.py <thư-mục-run> --promote
- [ ] Ghi mAP@50, AP theo lớp; gửi TV1

#### 1.8 [TV3] Khung API + web + Docker chạy được (cổng custom)

make up -> http://localhost:18080 hiển thị HealthBadge + Thư viện biển.

- [ ] Build image CPU
- [ ] Kiểm tra không cổng nào dùng mặc định
- [ ] Ghi chú dung lượng Docker (ổ C:)

#### 1.9 [TV2] Cài môi trường + khung frontend dev

make env/venv/install; cd web && npm run dev chạy ở 15173 proxy sang API 18100.

- [ ] Tự cài torch theo GPU, make check-env
- [ ] python -m utci_vision.api --reload + cd web && npm run dev
- [ ] Làm quen api/client.ts, types.ts

#### 1.10 [TV2] Spike CV: đánh giá chất lượng & tăng cường ảnh

Thử trên 30 ảnh tối/ngược sáng/mờ trong dataset.

- [ ] Đo mean V, std L, phương sai Laplacian
- [ ] Đề xuất ngưỡng trong configs/pipeline.yaml
- [ ] Ảnh trước/sau gửi TV4

#### 1.11 [TV5] Audit, EDA & duyệt dữ liệu

python scripts/data.py audit --dedup đã chạy được trên dữ liệu thật.

- [ ] Biểu đồ phân bố lớp/kích thước/độ phân giải
- [ ] Duyệt 118 ảnh không nhãn + mẫu cụm gần trùng
- [ ] Contact-sheet theo lớp; ghi reports/data/excluded.txt
- [ ] Gửi hình EDA cho TV4

#### 1.12 [TV5] Xác nhận classes.yaml (QCVN, has_value, has_text)

Siêu lớp, mã QCVN, lớp nào có số/chữ.

- [ ] Đối chiếu QCVN 41:2019
- [ ] Sửa superclass/has_value/has_text nếu sai

#### 1.13 [TV5] Smoke test notebook trên Colab + benchmark FPS mốc S1

TV3 hỗ trợ benchmark.

- [ ] Run all train_colab với SMOKE=True
- [ ] scripts/evaluate.py benchmark --yolo-only trên video 720p
- [ ] Ghi FPS GPU/CPU vào registry

#### 1.14 [TV4] Khung báo cáo & Chương 1

Theo template của trường/khoa.

- [ ] Chọn template (Word/Overleaf)
- [ ] Mục lục theo report/README.md
- [ ] Viết Chương 1: bài toán, mục tiêu, phạm vi

#### 1.15 [TV4] Báo cáo mốc S1

- [ ] Thu số liệu từ registry
- [ ] Nộp trước Review

#### 1.16 [ALL] Sprint 1 Review & Retro

Demo baseline + web hello + EDA.

- [ ] Demo
- [ ] Cập nhật SRS Changelog
- [ ] Retro: Giữ / Bỏ / Thử

## Sprint 2 — Dữ liệu v1 & các khối lõi (30/10/2026 – 06/11/2026)

**Mục tiêu:** Có processed/v1 sạch (đã chia lại, đóng gói lên Drive/Kaggle); YOLO11 fine-tune trên v1 với cấu hình tốt nhất (E3); tăng cường CV + đặc trưng vùng; pipeline khung + API ảnh; trang Ảnh chạy trong Docker.

**Sản phẩm bàn giao cuối sprint:**

- dataset v1 + utci_v1.zip/sha256 trên Drive và Kaggle; DATA_CARD
- YOLO11 fine-tune trên v1: n/s × 640/960 × freeze 0/10 (E3) — chốt TBD-3
- enhance.py + verifier.region_features có test
- POST /detect/image + trang Ảnh hoạt động qua make up
- Chương 2 (lý thuyết CV + DL) bản nháp; báo cáo mốc S2

| # | Thẻ | Phụ trách | Điểm | Ưu tiên | Yêu cầu SRS |
|---|---|---|---|---|---|
| 1 | Sprint 2 Planning | ALL | 1 | Must | - |
| 2 | Chia lại dữ liệu → processed/v1 + DATA_CARD | TV5 | 3 | Must | FR-DATA-04, FR-DATA-07 |
| 3 | Đóng gói & upload dataset (package.py) | TV5 | 2 | Must | FR-DATA-05 |
| 4 | Cắt crop lớp có số/chữ để gán nhãn | TV5 | 2 | Must | FR-DATA-08, FR-DATA-09 |
| 5 | Fine-tune YOLO11 trên v1 — E3 cấu hình | TV3 | 5 | Must | FR-TRAIN-04, FR-EVAL-03 |
| 6 | Pipeline khung + POST /detect/image | TV3 | 5 | Must | FR-PIPE-13, FR-API-03, FR-API-07 |
| 7 | enhance.py: đánh giá chất lượng + tăng cường thích nghi | TV2 | 3 | Must | FR-PIPE-01, FR-PIPE-02 |
| 8 | verifier.py: đặc trưng vùng | TV2 | 3 | Must | FR-PIPE-05 |
| 9 | Trang Ảnh (web) | TV2 | 3 | Must | FR-WEB-01 |
| 10 | Bộ đánh giá E1 (evaluate.py detect) | TV1 | 5 | Must | FR-EVAL-01, FR-EVAL-08 |
| 11 | Ý nghĩa 27 lớp biển báo (meaning) cho web | TV4 | 2 | Should | FR-DATA-06, FR-WEB-04 |
| 12 | Chương 2: lý thuyết CV + DL (fine-tune, YOLO) | TV4 | 5 | Must | FR-DOC-02 |
| 13 | Báo cáo mốc S2 | TV4 | 1 | Must | FR-DOC-01 |
| 14 | Sprint 2 Review & Retro | ALL | 1 | Must | - |

### Chi tiết công việc Sprint 2

#### 2.1 [ALL] Sprint 2 Planning

Hiệu chỉnh theo velocity S1.

- [ ] Xem velocity
- [ ] Chọn thẻ

#### 2.2 [TV5] Chia lại dữ liệu → processed/v1 + DATA_CARD

ADR-002.

- [ ] python scripts/data.py split (sau excluded.txt)
- [ ] Kiểm tra mọi lớp có ở cả 3 tập, 0 cụm rò rỉ
- [ ] Điền DATA_CARD §3–§4

#### 2.3 [TV5] Đóng gói & upload dataset (package.py)

Hiện thực data/package.py (zip + VERSION.json + sha256).

- [ ] Hiện thực + test
- [ ] python scripts/data.py package
- [ ] Upload Drive (Colab) + Kaggle Dataset utci-v1

#### 2.4 [TV5] Cắt crop lớp có số/chữ để gán nhãn

python scripts/data.py crops — chuẩn bị gán nhãn giá trị số & chữ ở S3 (dùng để đánh giá OCR, E5).

- [ ] python scripts/data.py crops
- [ ] Xem mẫu từng lớp has_value / has_text
- [ ] Lập mẫu CSV nhãn: values.csv, texts.csv

#### 2.5 [TV3] Fine-tune YOLO11 trên v1 — E3 cấu hình

Từ pretrained COCO; so sánh n/s, imgsz 640/960, freeze 0/10.

- [ ] Chia lượt chạy giữa Kaggle/Colab của các thành viên
- [ ] python scripts/import_run.py <thư-mục-run> --promote cho từng run
- [ ] Chốt TBD-3 theo mAP + ngân sách FPS

#### 2.6 [TV3] Pipeline khung + POST /detect/image

pipeline.load_components + Recognizer.process (enhance → YOLO); visualize.draw.

- [ ] Nạp mô hình một lần; /health báo trạng thái thật
- [ ] Giới hạn kích thước/định dạng ảnh
- [ ] scripts/infer.py dùng chung pipeline

#### 2.7 [TV2] enhance.py: đánh giá chất lượng + tăng cường thích nghi

- [ ] assess, needed_ops, enhance
- [ ] Unit test
- [ ] Ảnh minh hoạ cho báo cáo

#### 2.8 [TV2] verifier.py: đặc trưng vùng

Tỉ lệ màu, độ tròn, số đỉnh, solidity, Hu, HOG, độ nét.

- [ ] Tinh chỉnh ngưỡng HSV trong configs/verifier.yaml
- [ ] FEATURE_NAMES
- [ ] Unit test với ảnh tổng hợp

#### 2.9 [TV2] Trang Ảnh (web)

- [ ] Kéo-thả / chọn ảnh
- [ ] Vẽ box SVG màu theo siêu lớp
- [ ] Danh sách biển: tên, ý nghĩa, độ tin cậy

#### 2.10 [TV1] Bộ đánh giá E1 (evaluate.py detect)

- [ ] Đối chiếu metrics.py với Ultralytics val (chênh < 0.01)
- [ ] AP theo lớp & kích thước -> reports/eval/
- [ ] Ghi registry

#### 2.11 [TV4] Ý nghĩa 27 lớp biển báo (meaning) cho web

Điền configs/classes.yaml > meaning.

- [ ] 1–2 câu mỗi biển theo QCVN
- [ ] TV5 rà soát

#### 2.12 [TV4] Chương 2: lý thuyết CV + DL (fine-tune, YOLO)

TV2 hỗ trợ phần CV.

- [ ] Không gian màu, CLAHE, hình thái học, contour, HOG, Kalman
- [ ] CNN, transfer learning / fine-tune, YOLO11
- [ ] Metric IoU, mAP, F1

#### 2.13 [TV4] Báo cáo mốc S2

- [ ] Bảng E3
- [ ] Nộp trước Review

#### 2.14 [ALL] Sprint 2 Review & Retro

Demo upload ảnh trên web (Docker).

- [ ] Demo
- [ ] Chốt TBD-3, TBD-5
- [ ] Retro

## Sprint 3 — MVP: pipeline đầy đủ trên ảnh + video (06/11/2026 – 13/11/2026)

**Mục tiêu:** Ảnh tĩnh đi qua đủ các khâu (enhance → YOLO → xác minh LightGBM → đọc số bằng VietOCR + regex); video xử lý nền với tracking; trang Video + Thư viện; E1 sơ bộ.

**Sản phẩm bàn giao cuối sprint:**

- Bộ xác minh LightGBM fit trên val (E3: LogReg/RF/LightGBM)
- Đọc giá trị số: CV cắt vùng + VietOCR + regex; hiển thị km/h, m, T
- Tracking Kalman + IoU; job video API + trang Video
- E1 sơ bộ + phân tích lỗi; chốt TBD-1, TBD-4

| # | Thẻ | Phụ trách | Điểm | Ưu tiên | Yêu cầu SRS |
|---|---|---|---|---|---|
| 1 | Sprint 3 Planning | ALL | 1 | Must | - |
| 2 | Bộ xác minh LightGBM (stacking) | TV1 | 5 | Must | FR-PIPE-06, FR-TRAIN-05, FR-EVAL-03 |
| 3 | Đọc giá trị số: regex + hợp lệ hoá | TV1 | 2 | Must | FR-PIPE-07 |
| 4 | E1 sơ bộ + phân tích lỗi | TV1 | 2 | Must | FR-EVAL-01 |
| 5 | ocr.py: cắt vùng số | TV2 | 2 | Must | FR-PIPE-07 |
| 6 | tracking.py: Kalman + IoU + bỏ phiếu | TV2 | 5 | Must | FR-PIPE-04 |
| 7 | Trang Video (web) | TV2 | 3 | Must | FR-WEB-02 |
| 8 | Tích hợp VietOCR (ocr.TextReader) | TV3 | 2 | Must | FR-PIPE-09 |
| 9 | Tích hợp xác minh + đọc số vào pipeline (ảnh) | TV3 | 3 | Must | FR-PIPE-06, FR-PIPE-07 |
| 10 | Job video (JobManager) + giới hạn upload | TV3 | 3 | Must | FR-API-04, FR-API-06 |
| 11 | Trang Thư viện biển + giao diện responsive | TV3 | 2 | Should | FR-WEB-04, FR-WEB-06 |
| 12 | Gán nhãn giá trị (≥150) & chữ (≥200 crop) | TV5 | 5 | Must | FR-DATA-08, FR-DATA-09 |
| 13 | 2 video đường phố để demo & đo flicker | TV5 | 2 | Should | FR-DATA-10 |
| 14 | Chương 2 (ML) + Chương 3 Dữ liệu | TV4 | 5 | Must | FR-DOC-02 |
| 15 | Báo cáo mốc S3 | TV4 | 1 | Must | FR-DOC-01 |
| 16 | Sprint 3 Review & Retro — Demo MVP | ALL | 1 | Must | - |

### Chi tiết công việc Sprint 3

#### 3.1 [ALL] Sprint 3 Planning

- [ ] Chốt định nghĩa MVP

#### 3.2 [TV1] Bộ xác minh LightGBM (stacking)

verifier.py; fit trong notebook (FIT_VERIFIER=True).

- [ ] build_dataset trên val, GroupKFold theo ảnh
- [ ] So sánh LogReg/RF/LightGBM + hiệu chỉnh xác suất
- [ ] Verifier.verify; ADR-008

#### 3.3 [TV1] Đọc giá trị số: regex + hợp lệ hoá

ocr.parse_value: trích số từ chuỗi VietOCR, hợp lệ hoá theo đơn vị của lớp (configs/ocr.yaml > value).

- [ ] parse_value ("50", "3.5", "3,5") + test
- [ ] Tập giá trị hợp lệ km/h, khoảng m/T
- [ ] Accuracy trên crop có nhãn giá trị của TV5

#### 3.4 [TV1] E1 sơ bộ + phân tích lỗi

- [ ] python scripts/evaluate.py detect --split test
- [ ] Confusion matrix, AP lớp hiếm
- [ ] Đề xuất cho S4

#### 3.5 [TV2] ocr.py: cắt vùng số

value_region: đĩa trắng trong viền đỏ, phóng to — đầu vào VietOCR.

- [ ] Mask đỏ + hình tròn -> vùng trong viền
- [ ] Phóng to, tăng tương phản
- [ ] So sánh VietOCR có/không cắt vùng trên crop thật

#### 3.6 [TV2] tracking.py: Kalman + IoU + bỏ phiếu

- [ ] Kalman 8 trạng thái
- [ ] Hungarian (scipy)
- [ ] min_hits, max_age, vote_window
- [ ] Test chuỗi frame nhiễu

#### 3.7 [TV2] Trang Video (web)

- [ ] Upload + tiến độ
- [ ] Phát/tải video kết quả
- [ ] Bảng biển đã xuất hiện

#### 3.8 [TV3] Tích hợp VietOCR (ocr.TextReader)

Đã kiểm chứng cài --no-deps. Cần từ S3 vì VietOCR đọc cả số trên biển.

- [ ] TextReader.read batch
- [ ] Trọng số local khi offline

#### 3.9 [TV3] Tích hợp xác minh + đọc số vào pipeline (ảnh)

Ảnh tĩnh chạy đồng bộ các tác vụ.

- [ ] Recognizer gọi Verifier + đọc số (value_region → TextReader → parse_value)
- [ ] Debug output cơ bản

#### 3.10 [TV3] Job video (JobManager) + giới hạn upload

- [ ] POST /jobs/video, GET /jobs/{id}
- [ ] Tracking trong video
- [ ] Dọn file > 24 giờ

#### 3.11 [TV3] Trang Thư viện biển + giao diện responsive

- [ ] Nhóm theo siêu lớp
- [ ] Kiểm tra trên điện thoại

#### 3.12 [TV5] Gán nhãn giá trị (≥150) & chữ (≥200 crop)

Từ data-crops + ảnh tự chụp (biển phụ).

- [ ] CSV giá trị
- [ ] CSV chữ (biển chính + biển phụ)
- [ ] Lưu Drive (dùng cho E5)

#### 3.13 [TV5] 2 video đường phố để demo & đo flicker

Tự quay hoặc nguồn mở có giấy phép.

- [ ] 1–3 phút mỗi video
- [ ] Ghi nguồn trong DATA_CARD

#### 3.14 [TV4] Chương 2 (ML) + Chương 3 Dữ liệu

- [ ] Gradient Boosting, stacking, hiệu chỉnh xác suất
- [ ] Chương 3 từ DATA_CARD + EDA

#### 3.15 [TV4] Báo cáo mốc S3

- [ ] E1 sơ bộ
- [ ] Nộp trước Review

#### 3.16 [ALL] Sprint 3 Review & Retro — Demo MVP

- [ ] Demo ảnh + video trên web
- [ ] Chốt TBD-1, TBD-4
- [ ] Retro

## Sprint 4 — Realtime & OCR tiếng Việt (13/11/2026 – 20/11/2026)

**Mục tiêu:** Webcam qua WebSocket ≥ 20 FPS (GPU); tác vụ theo track chạy nền; OCR chữ tiếng Việt + biển phụ; trang Webcam; E4 độ bền, E5 đọc số/chữ.

**Sản phẩm bàn giao cuối sprint:**

- WS /stream + trang Webcam với back-pressure
- Tác vụ theo track bất đồng bộ (xác minh, đọc số, OCR)
- VietOCR + hậu xử lý từ điển/regex; tìm biển phụ
- E4, E5 có số liệu; Chương 4 Phương pháp

| # | Thẻ | Phụ trách | Điểm | Ưu tiên | Yêu cầu SRS |
|---|---|---|---|---|---|
| 1 | Sprint 4 Planning | ALL | 1 | Must | - |
| 2 | Tác vụ theo track bất đồng bộ trong Recognizer | TV3 | 5 | Must | FR-PIPE-12 |
| 3 | WebSocket /stream + back-pressure | TV3 | 3 | Must | FR-API-05 |
| 4 | Trang Webcam (web) | TV2 | 5 | Must | FR-WEB-03 |
| 5 | ocr.py: dòng chữ, biển phụ, frame tốt nhất | TV2 | 5 | Should | FR-PIPE-08, FR-PIPE-09, FR-PIPE-10 |
| 6 | ocr.py: hậu xử lý chữ (từ điển, nghĩa, bỏ phiếu) | TV1 | 3 | Should | FR-PIPE-11 |
| 7 | E5: đọc số & OCR so với EasyOCR | TV1 | 3 | Should | FR-EVAL-05 |
| 8 | E4: tập suy giảm & độ bền | TV5 | 3 | Should | FR-DATA-11, FR-EVAL-04 |
| 9 | Benchmark qua API / WebSocket | TV5 | 2 | Must | FR-EVAL-07, NFR-PERF-01 |
| 10 | Chương 4 Phương pháp + từ điển chữ biển phụ | TV4 | 5 | Must | FR-DOC-02 |
| 11 | Báo cáo mốc S4 | TV4 | 1 | Must | FR-DOC-01 |
| 12 | Sprint 4 Review & Retro | ALL | 1 | Must | - |

### Chi tiết công việc Sprint 4

#### 4.1 [ALL] Sprint 4 Planning

- [ ] Chọn thẻ theo phân tích lỗi S3

#### 4.2 [TV3] Tác vụ theo track bất đồng bộ trong Recognizer

ThreadPool, refresh_every, không chặn luồng frame.

- [ ] Lập lịch theo track mới / đến hạn / độ tin cậy giảm
- [ ] Đo FPS luồng chính trước/sau (≤ 10%)

#### 4.3 [TV3] WebSocket /stream + back-pressure

- [ ] Mỗi kết nối một Recognizer(video=True)
- [ ] Thu nhỏ frame ≤ 960 px
- [ ] Kiểm tra qua nginx ở cổng 18080

#### 4.4 [TV2] Trang Webcam (web)

- [ ] getUserMedia + canvas
- [ ] Gửi JPEG, chờ kết quả rồi gửi tiếp
- [ ] FPS + panel biển vừa gặp

#### 4.5 [TV2] ocr.py: dòng chữ, biển phụ, frame tốt nhất

- [ ] text_lines (deskew, projection)
- [ ] find_sub_sign
- [ ] frame_score; quyết định TBD-4

#### 4.6 [TV1] ocr.py: hậu xử lý chữ (từ điển, nghĩa, bỏ phiếu)

- [ ] Khớp từ điển (rapidfuzz)
- [ ] Regex khung giờ / khoảng cách / loại xe
- [ ] Bỏ phiếu theo track

#### 4.7 [TV1] E5: đọc số & OCR so với EasyOCR

EasyOCR cài riêng, không vào requirements.

- [ ] Accuracy giá trị
- [ ] CER, exact match chữ
- [ ] Ghi registry

#### 4.8 [TV5] E4: tập suy giảm & độ bền

evaluation/experiments.DEGRADATIONS.

- [ ] evaluate detect --degrade × 4
- [ ] ± tăng cường CV
- [ ] Bảng ΔmAP gửi TV4

#### 4.9 [TV5] Benchmark qua API / WebSocket

- [ ] evaluate benchmark --api
- [ ] FPS, p95 latency
- [ ] Ghi registry

#### 4.10 [TV4] Chương 4 Phương pháp + từ điển chữ biển phụ

Từ điển: configs/ocr_lexicon.txt.

- [ ] Sơ đồ pipeline
- [ ] Mô tả từng khâu CV/DL/ML
- [ ] Bổ sung ocr_lexicon.txt

#### 4.11 [TV4] Báo cáo mốc S4

- [ ] Nộp trước Review

#### 4.12 [ALL] Sprint 4 Review & Retro

Demo webcam + OCR.

- [ ] Demo realtime
- [ ] Quyết định model freeze S5
- [ ] Retro

## Sprint 5 — Tối ưu, model freeze & bản nháp báo cáo (20/11/2026 – 27/11/2026)

**Mục tiêu:** Đạt mục tiêu hiệu năng; chốt mô hình (fine-tune cuối trên nền tảng chính thức); ablation E2 + E6 đầy đủ; kiểm thử chấp nhận lần 1; bản nháp báo cáo đầy đủ.

**Sản phẩm bàn giao cuối sprint:**

- NFR-PERF đạt (hoặc ghi nhận lý do); profile GPU + healthcheck
- Trọng số chốt + docs/models.md
- Bảng E1–E7 cuối cùng
- Kiểm thử chấp nhận A1–A7 lần 1; bản nháp Chương 1–6

| # | Thẻ | Phụ trách | Điểm | Ưu tiên | Yêu cầu SRS |
|---|---|---|---|---|---|
| 1 | Sprint 5 Planning | ALL | 1 | Must | - |
| 2 | Tối ưu FPS + export ONNX (Could) | TV3 | 5 | Should | NFR-PERF-01, NFR-PERF-02, FR-TRAIN-09 |
| 3 | Docker GPU profile + healthcheck + máy sạch | TV3 | 3 | Must | FR-DEP-02, FR-DEP-04, NFR-REP-03 |
| 4 | Model freeze: fine-tune cuối + docs/models.md | TV3 | 2 | Must | FR-TRAIN-04 |
| 5 | Trang Giải thích + debug output | TV2 | 5 | Should | FR-WEB-05, FR-PIPE-14 |
| 6 | E6: flicker rate ± tracking | TV2 | 2 | Should | FR-EVAL-06 |
| 7 | E2 ablation + tổng hợp E1–E7 | TV1 | 5 | Must | FR-EVAL-02 |
| 8 | Review kỹ thuật bản nháp báo cáo | TV1 | 2 | Must | FR-DOC-02 |
| 9 | Kiểm thử chấp nhận A1–A7 lần 1 | TV5 | 3 | Must | - |
| 10 | Bổ sung unit test (≥ 30) | TV5 | 2 | Should | NFR-MNT-02 |
| 11 | Chương 5 Thực nghiệm + Chương 6 Ứng dụng | TV4 | 5 | Must | FR-DOC-02 |
| 12 | Báo cáo mốc S5 | TV4 | 1 | Must | FR-DOC-01 |
| 13 | Sprint 5 Review & Retro | ALL | 1 | Must | - |

### Chi tiết công việc Sprint 5

#### 5.1 [ALL] Sprint 5 Planning

Hạn model freeze: thứ Ba (giữa sprint).

- [ ] Chốt nền tảng số liệu chính thức (TBD-5)

#### 5.2 [TV3] Tối ưu FPS + export ONNX (Could)

- [ ] FP16, refresh_every, kích thước frame
- [ ] (Could) ONNX cho CPU
- [ ] Đo lại benchmark

#### 5.3 [TV3] Docker GPU profile + healthcheck + máy sạch

- [ ] make up-gpu trên RTX 4060
- [ ] Healthcheck xanh
- [ ] make up trên một máy chưa cài gì (≤ 15 phút)

#### 5.4 [TV3] Model freeze: fine-tune cuối + docs/models.md

Fine-tune tiếp từ checkpoint tốt nhất nếu cần (INIT_WEIGHTS).

- [ ] Chốt yolo11.pt, verifier.joblib
- [ ] Upload Drive / Release
- [ ] Cập nhật docs/models.md

#### 5.5 [TV2] Trang Giải thích + debug output

- [ ] Pipeline trả ảnh trung gian khi debug
- [ ] Hiển thị theo thứ tự khâu
- [ ] Feature importance của bộ xác minh

#### 5.6 [TV2] E6: flicker rate ± tracking

Trên 2 video của TV5.

- [ ] Đo flicker
- [ ] Ghi registry

#### 5.7 [TV1] E2 ablation + tổng hợp E1–E7

evaluate detect --ablation.

- [ ] yolo_only → +enhance → +verifier → full
- [ ] Bảng + biểu đồ cho báo cáo
- [ ] Đối chiếu NFR

#### 5.8 [TV1] Review kỹ thuật bản nháp báo cáo

- [ ] Lý thuyết & số liệu đúng
- [ ] Comment cho TV4

#### 5.9 [TV5] Kiểm thử chấp nhận A1–A7 lần 1

SRS Phụ lục A.

- [ ] Chạy A1–A7
- [ ] Ghi lỗi thành thẻ S6

#### 5.10 [TV5] Bổ sung unit test (≥ 30)

- [ ] Test schema API
- [ ] Test tracking, ocr (hậu xử lý)

#### 5.11 [TV4] Chương 5 Thực nghiệm + Chương 6 Ứng dụng

TV2 viết phần CV.

- [ ] Môi trường (3 nền tảng fine-tune)
- [ ] E1–E7 + phân tích
- [ ] Ảnh chụp web

#### 5.12 [TV4] Báo cáo mốc S5

- [ ] Nộp trước Review

#### 5.13 [ALL] Sprint 5 Review & Retro

Đọc chéo bản nháp.

- [ ] Demo bản gần cuối
- [ ] Đọc chéo chương
- [ ] Retro

## Sprint 6 — Ổn định, báo cáo cuối & bảo vệ (27/11/2026 – 04/12/2026)

**Mục tiêu:** Bản nộp cuối: code tag v1.0 tái lập được (make up), báo cáo PDF, slide, video demo; diễn tập thuyết trình.

**Sản phẩm bàn giao cuối sprint:**

- Tag v1.0 + GitHub Release (trọng số) trên UTCI-Vision
- Báo cáo cuối kỳ (PDF + nguồn)
- Slide + video demo 3–5 phút
- Diễn tập ≥ 2 lần

| # | Thẻ | Phụ trách | Điểm | Ưu tiên | Yêu cầu SRS |
|---|---|---|---|---|---|
| 1 | Sprint 6 Planning | ALL | 1 | Must | - |
| 2 | Sửa lỗi, code freeze, tag v1.0 | TV3 | 3 | Must | - |
| 3 | README tái lập + kiểm tra máy sạch | TV3 | 2 | Must | FR-DOC-04, NFR-REP-02 |
| 4 | Hỗ trợ hoàn thiện báo cáo | TV2 | 3 | Must | FR-DOC-02 |
| 5 | Quay & dựng video demo 3–5 phút | TV2 | 2 | Must | FR-DOC-03 |
| 6 | Hoàn thiện báo cáo cuối kỳ | TV4 | 5 | Must | FR-DOC-02 |
| 7 | Slide thuyết trình | TV4 | 3 | Must | FR-DOC-03 |
| 8 | Review cuối & chuẩn bị phản biện | TV1 | 3 | Must | - |
| 9 | Kiểm thử hồi quy cuối + checklist nộp bài | TV5 | 2 | Must | - |
| 10 | Diễn tập thuyết trình (2 lần) | ALL | 2 | Must | - |
| 11 | Review cuối dự án & Retro | ALL | 1 | Must | - |

### Chi tiết công việc Sprint 6

#### 6.1 [ALL] Sprint 6 Planning

Chỉ sửa lỗi, không thêm tính năng.

- [ ] Code freeze: thứ Ba (giữa sprint)

#### 6.2 [TV3] Sửa lỗi, code freeze, tag v1.0

- [ ] Sửa lỗi từ kiểm thử
- [ ] develop → main, tag v1.0
- [ ] Release kèm trọng số

#### 6.3 [TV3] README tái lập + kiểm tra máy sạch

- [ ] make env/venv/install/up theo README
- [ ] ≤ 30 phút trên máy mới

#### 6.4 [TV2] Hỗ trợ hoàn thiện báo cáo

- [ ] Đánh số hình/bảng
- [ ] Tài liệu tham khảo
- [ ] Soát chính tả

#### 6.5 [TV2] Quay & dựng video demo 3–5 phút

Cùng TV3.

- [ ] Kịch bản: ảnh, video, webcam, giải thích
- [ ] Upload, link trong README

#### 6.6 [TV4] Hoàn thiện báo cáo cuối kỳ

- [ ] Chương 7 Kết luận
- [ ] Phụ lục phân công + kế hoạch
- [ ] Xuất PDF theo quy định

#### 6.7 [TV4] Slide thuyết trình

15–20 slide.

- [ ] Dàn ý theo báo cáo
- [ ] TV1 review

#### 6.8 [TV1] Review cuối & chuẩn bị phản biện

- [ ] Review code, báo cáo, slide
- [ ] 20 câu hỏi phản biện dự kiến
- [ ] Phân công trả lời

#### 6.9 [TV5] Kiểm thử hồi quy cuối + checklist nộp bài

- [ ] A1–A7 trên v1.0
- [ ] Đủ file nộp
- [ ] Ghi nguồn dataset & repo tham khảo

#### 6.10 [ALL] Diễn tập thuyết trình (2 lần)

- [ ] Lần 1: bấm giờ
- [ ] Lần 2: demo trực tiếp + phản biện thử

#### 6.11 [ALL] Review cuối dự án & Retro

- [ ] Nộp bài
- [ ] Retro toàn dự án

## Backlog (chưa xếp sprint)

| Thẻ | Phụ trách đề xuất | Điểm | Ghi chú |
|---|---|---|---|
| CNN phân loại lại cho cặp lớp hay nhầm | TV3 | 5 | Chỉ làm khi phân tích lỗi S3 cho thấy YOLO nhầm có hệ thống giữa vài cặp lớp; chạy theo track, chỉ cho các lớp đó. |
| Gán nhãn lớp "biển phụ" cho YOLO (dự phòng TBD-4) | TV5 | 5 | Nếu tìm biển phụ bằng CV không đạt. Cần 300–500 box. |
| Fine-tune VietOCR trên crop biển báo (FR-TRAIN-10) | TV3 | 5 | Chỉ khi E5 cho thấy OCR < 80% exact match. |
| Suy luận cắt lát SAHI cho ảnh độ phân giải cao (FR-PIPE-15) | TV1 | 3 | Cho ảnh tĩnh ≥ 1920 px. |
| Gộp/loại lớp hiếm (TBD-1) — đã chốt S1 | TV1 | 2 | Đã chốt 29/10/2026 (ADR-009): gộp 6 lớp < 60 cụm cảnh (5, 11, 12, 22, 25, 27) vào "Biển báo khác" -> 27 lớp. Còn lại: theo dõi AP lớp gộp; tách lớp khi đủ dữ liệu (v2+). |
| Mẫu thẻ yêu cầu thay đổi (CHANGE-REQ) | TV1 | 0 | Sao chép thẻ này khi muốn đổi yêu cầu. |

## Nghi thức Scrum rút gọn (sprint 1 tuần)

| Hoạt động | Thời điểm | Thời lượng | Nội dung |
|---|---|---|---|
| Sprint Review | Thứ Sáu, ngày chuyển sprint (sáng) | 30 phút | Demo, chạy đánh giá, cập nhật SRS |
| Retrospective | Thứ Sáu (sau Review) | 20 phút | Giữ / Bỏ / Thử |
| Sprint Planning | Thứ Sáu (sau Retro) | 45 phút | Chọn thẻ sprint mới, xác nhận người phụ trách & điểm |
| Daily (async) | Hằng ngày trên Discord | 5 phút/người | Hôm qua / Hôm nay / Vướng mắc |
| Sync giữa sprint | Thứ Ba | 20 phút | Gỡ vướng, điều chỉnh phạm vi |

## Rủi ro kế hoạch & phương án dự phòng

| Rủi ro | Dấu hiệu | Phương án |
|---|---|---|
| Lọc dữ liệu kéo dài | Cuối S2 chưa có processed/v1 | TV3/TV2 tiếp tục trên dữ liệu gốc; TV1 hỗ trợ TV5 duyệt ảnh |
| Thiếu GPU / train quá lâu | 1 lần train YOLO > 6 giờ | Kaggle/Colab, YOLO11n để thử nhanh, giảm epoch |
| Pipeline Classic recall thấp | Recall ROI < 0.3 ở S3 | Giới hạn đánh giá biển ≥ 24 px, báo cáo trung thực; thử MSER (Backlog) |
| Chất lượng chưa đạt ở S4 | mAP@50 < 0.75 | Ưu tiên dữ liệu & imgsz, hoãn các thẻ Could (OCR, tab So sánh) |
| Báo cáo dồn cuối kỳ | Cuối S4 chưa có Chương 1–4 | TV2 chuyển hẳn sang hỗ trợ báo cáo từ S5 |
| Thành viên bận/ốm | Velocity giảm > 30% | Cắt thẻ Should/Could; S6 là buffer |
| Yêu cầu thay đổi nhiều | Nhiều thẻ CHANGE-REQ | Xử lý theo SRS §9, chỉ nhận vào sprint kế tiếp |

