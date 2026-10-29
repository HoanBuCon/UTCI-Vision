# UTCI-VISION — Phương án kỹ thuật (bản đã duyệt)

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 3.2 — đề xuất đã duyệt (2026-10-22) + bổ sung: fine-tune, cổng custom, Makefile; bỏ SVM chữ số (2026-10-23) |
| Repo | https://github.com/HoanBuCon/UTCI-Vision |
| Chủ sở hữu | TV1 (Tech Lead) |
| Liên quan | 01_TECHSTACK.md, 02_SRS.md, 03_SPRINT_PLAN.md, docs/adr/ |

## 0. Các quyết định đã chốt

| # | Quyết định | ADR |
|---|---|---|
| Q1 | **Một hệ thống duy nhất**: YOLO11 làm lõi phát hiện + phân loại; CV và ML làm những việc YOLO không làm được, chạy theo track | ADR-001 |
| Q2 | **Không** dùng CNN phân loại riêng (trùng việc với YOLO) — chỉ để Backlog, làm khi phân tích lỗi chứng minh cần | ADR-001 |
| Q3 | Detector: **YOLO11** (Ultralytics), mặc định `yolo11s`, `imgsz` 960 — **fine-tune từ trọng số pretrained**, không train lại từ đầu; không so sánh các đời YOLO khác | ADR-004 |
| Q4 | **VietOCR đọc cả số và chữ** trên biển và **biển phụ**: CV cắt vùng, regex hợp lệ hoá số, từ điển sửa chữ; chạy bất đồng bộ theo track. Không dùng SVM chữ số riêng | ADR-001 |
| Q5 | Demo là **web** (React + FastAPI), đóng gói **Docker Compose** (CPU mặc định, profile GPU) | ADR-003 |
| Q6 | **Không khoá torch/CUDA** — mỗi thành viên tự cài theo GPU; chỉ khoá thư viện dùng chung | ADR-005 |
| Q7 | **Fine-tune chỉ qua 3 notebook** (Local / Google Colab / Kaggle) sinh từ một template; mọi việc khác chạy bằng mã nguồn local | ADR-006 |
| Q9 | Mọi tiến trình dùng **cổng custom qua `.env`** (API 18100, web 18080, Vite 15173, Jupyter 18888); **Makefile chỉ cho DevOps** (môi trường, CI, Docker) | ADR-007 |
| Q8 | Dữ liệu chia lại theo cụm gần trùng; train → YOLO, val → chỉnh tham số + train bộ xác minh ML, test → chỉ đánh giá | ADR-002 |

## 1. Mục tiêu & phạm vi

Web app nhận diện **27 lớp biển báo giao thông Việt Nam** (26 loại + "Biển báo khác", ADR-009) từ **ảnh, video và webcam realtime**. Với mỗi biển: vị trí, tên tiếng Việt, ý nghĩa, giá trị số (km/h, m) và **chữ tiếng Việt trên biển / biển phụ** khi đọc được.

Ngoài phạm vi: tên riêng cho các biển thuộc lớp "Biển báo khác" và biển ngoài dataset, đèn tín hiệu, vạch kẻ đường, ứng dụng mobile/nhúng, hệ thống ADAS thật.

## 2. Kiến trúc pipeline

```
Frame ─► [CV] Đánh giá chất lượng ─► (chỉ khi tối/kém) gamma + CLAHE (+ khử nhiễu)
      ─► [DL] YOLO11: phát hiện + phân loại 27 lớp                    ← mỗi frame
      ─► [CV] Tracking: Kalman + ghép IoU, bỏ phiếu nhãn theo track    ← mỗi frame, < 1 ms
      ─► Theo track — chạy nền, kết quả gắn vào track khi xong:
            [CV+ML] Đặc trưng màu/hình dạng → LightGBM xác minh + hiệu chỉnh độ tin cậy
            [CV+DL] Cắt vùng số → VietOCR → regex hợp lệ hoá → 50 km/h · 3.5 m · 10 T
            [CV+DL] Chọn frame nét/lớn nhất → cắt vùng chữ, tìm biển phụ → VietOCR
                    → hậu xử lý: khớp từ điển (rapidfuzz) + regex (khung giờ, khoảng cách, loại xe)
      ─► API (REST / WebSocket) ─► Web
```

Với ảnh tĩnh: cùng pipeline, "track" chỉ có một frame và các tác vụ nền chạy đồng bộ.

| Kỹ thuật | Thành phần | Vai trò |
|---|---|---|
| **DL** | YOLO11s fine-tune từ pretrained COCO | Phát hiện + phân loại 27 lớp (lõi) |
| **DL** | VietOCR (pretrained, transformer) | Nhận dạng dòng chữ tiếng Việt có dấu |
| **CV** | Đánh giá chất lượng (độ sáng V, độ lệch chuẩn L, phương sai Laplacian) + tăng cường thích nghi | Tăng recall khi ảnh tối/ngược sáng mà không cần train lại |
| **CV** | Đặc trưng vùng: tỉ lệ màu đỏ/xanh/vàng/trắng, độ tròn, số đỉnh xấp xỉ, solidity, Hu moments, HOG-PCA, độ nét | Đầu vào cho bộ xác minh ML (mã hoá tri thức QCVN về màu/hình dạng) |
| **CV** | Kalman + IoU tracking, bỏ phiếu có trọng số, xác nhận track sau ≥ 3 frame | Nhãn không nhấp nháy, mỗi biển thông báo một lần, chọn frame tốt cho OCR |
| **CV** | Cắt vùng số (đĩa trắng trong viền đỏ); cắt vùng chữ (phóng to, CLAHE, nắn nghiêng `minAreaRect`, projection profile); tìm biển phụ (tấm chữ nhật sáng ngay dưới box) | Chuẩn bị đầu vào cho SVM / VietOCR |
| **ML** | LightGBM (stacking trên dự đoán YOLO ở tập val) | Loại dương tính giả, hiệu chỉnh độ tin cậy |
| **ML** | Khớp mờ với từ điển chữ biển báo (rapidfuzz, Levenshtein) | Sửa lỗi dấu/ký tự của OCR |

### 2.1 Bộ xác minh (LightGBM)
- **Mẫu:** mỗi box YOLO dự đoán trên tập **val** (ngưỡng conf thấp 0.1). **Nhãn:** 1 nếu khớp GT cùng lớp (IoU ≥ 0.5), ngược lại 0.
- **Đặc trưng:** điểm YOLO, lớp YOLO (one-hot siêu lớp + id), kích thước/vị trí box tương đối, đặc trưng vùng CV, độ phù hợp giữa siêu lớp dự đoán và màu/hình dạng đo được.
- **Đầu ra:** xác suất "đúng" đã hiệu chỉnh (isotonic) thay cho điểm YOLO; box dưới ngưỡng bị loại. Feature importance dùng cho phần giải thích trong báo cáo.

### 2.2 Đọc số và OCR tiếng Việt
| Loại chữ | Ví dụ | Cách đọc |
|---|---|---|
| Số trên biển cấm | 50 (km/h), 3.5 (m), 10 (T) | CV cắt vùng số + VietOCR; regex trích số, đơn vị suy từ lớp biển, hợp lệ hoá theo tập giá trị cho phép |
| Chữ trên biển chính | "KIỂM TRA", chữ trên biển chỉ dẫn | CV cắt vùng chữ + VietOCR |
| Biển phụ | "6h–22h", "Trừ xe buýt", "Cách 100m" | CV tìm biển phụ + VietOCR + regex phân tích nghĩa |

- Chỉ chạy khi chiều cao crop ≥ ~60 px (cấu hình được); trên video, track chờ biển to dần và đọc ở frame tốt nhất (diện tích × độ nét).
- Lớp nào có chữ: cờ `has_text` / `has_value` trong `configs/classes.yaml`.
- Dữ liệu không có nhãn chữ → tự gán ~200 crop (gồm biển phụ) để đánh giá (CER, exact match). Dự phòng nếu tìm biển phụ bằng CV không đạt: gán nhãn thêm lớp "biển phụ" (300–500 box) cho YOLO.

## 3. Hiệu năng realtime

Ngân sách mỗi frame (ước tính — đo thật bằng benchmark ở Sprint 1), ảnh 960×540, RTX 4060 Laptop:

| Khâu | Thời gian |
|---|---|
| Giải mã JPEG + resize | 3–5 ms |
| Đánh giá chất lượng (+ CLAHE khi cần) | 0,5 ms (+3–5 ms) |
| YOLO11s FP16 | 10–15 ms |
| Tracking + bỏ phiếu | < 1 ms |
| Xác minh (chia đều theo track) | 1–2 ms |
| OCR | 0 ms trên luồng chính (luồng nền, trễ vài trăm ms) |
| **Tổng** | **~20–30 ms (~30 FPS)** — mục tiêu ≥ 20 FPS qua web |

Biện pháp: khâu nặng chạy theo track (khi track mới / mỗi N frame / khi độ tin cậy giảm); WebSocket có back-pressure (client chỉ gửi frame mới khi nhận xong kết quả); server chỉ trả JSON, client vẽ canvas; mỗi khâu có cờ bật/tắt; dự phòng `imgsz` 640, FP16, ONNX/TensorRT. **Benchmark FPS là thẻ bắt buộc ở Sprint 1.**

## 4. Web & Docker

- **Backend FastAPI:** `GET /api/v1/health`, `GET /api/v1/classes`, `POST /api/v1/detect/image`, `POST /api/v1/jobs/video` + `GET /api/v1/jobs/{id}`, `WS /api/v1/stream`; tham số `debug=true` trả kết quả trung gian từng khâu. Chạy bằng `python -m utci_vision.api` trên `UTCI_API_PORT`.
- **Frontend React + TypeScript + Vite** (Nginx): trang Ảnh, Video, Webcam realtime, Thư viện biển báo, Giải thích.
- **Docker Compose:** `api` + `web`; image CPU mặc định; profile `gpu` dùng image `pytorch/pytorch` (CUDA đi kèm image, máy thật chỉ cần driver + WSL2). Trọng số mount từ `./models`. `make up` (hoặc `make up-gpu`) → `http://localhost:18080` (cổng theo `.env`, xem §7).

## 5. Dữ liệu

Kết quả kiểm tra dataset thật (5 453 ảnh, 13 478 box, 32 lớp — Roboflow, CC BY 4.0):

| Vấn đề | Số liệu | Xử lý |
|---|---|---|
| Mất cân bằng lớp | 31 → 1 705 box (~55×) | Báo cáo AP theo lớp; copy-paste augmentation; gộp 6 lớp < 60 cụm cảnh vào "Biển báo khác" (ADR-009) |
| Biển rất nhỏ | trung vị ≈ 25 px; 30% box < 0,05% diện tích ảnh | YOLO `imgsz` 960; OCR chờ frame gần |
| Lệch phân bố giữa các tập | 6/32 lớp không có trong test gốc; test 100% một độ phân giải | Chia lại 70/15/15 phân tầng theo lớp + nguồn |
| Ảnh gần trùng | 530 cụm, 2 033 ảnh (37%); 4 cụm vắt qua nhiều tập | Chia theo cụm (pHash, Hamming ≤ 6) |
| 118 ảnh không nhãn | — | Duyệt tay; ảnh nền thật giữ lại |

Công cụ `scripts/data.py audit|split` đã chạy thử thành công trên dữ liệu thật. Dữ liệu bổ sung (để đánh giá OCR): ≥ 150 crop có nhãn giá trị số, ~200 crop có nhãn chữ, 2 video đường phố.

Luồng dữ liệu: local `scripts/data.py audit → split → (crops) → package` → `utci_v1.zip` + checksum → Google Drive (Colab) và Kaggle Dataset riêng tư (Kaggle) → notebook kiểm tra checksum trước khi train.

## 6. Fine-tune bằng notebook

| Fine-tune / fit (notebook) | Không huấn luyện (mã nguồn local) |
|---|---|
| Fine-tune YOLO11 từ pretrained · sinh tập xác minh từ val + fit LightGBM · đánh giá nhanh trên val · (tuỳ chọn) export ONNX | Kiểm tra/chia/đóng gói dữ liệu · đánh giá trên test, ablation, benchmark · pipeline, API, web, Docker · registry chính thức · báo cáo |

- **Fine-tune, không retrain:** YOLO11 khởi tạo từ `yolo11s.pt` pretrained COCO (hoặc checkpoint của nhóm qua `INIT_WEIGHTS`), AdamW `lr0=0.001`, ~80 epoch, tuỳ chọn đóng băng backbone (`freeze=10`, so sánh ở E3); VietOCR dùng pretrained (đọc cả số và chữ); LightGBM là mô hình cổ điển nên được *fit* trên đặc trưng.
- `notebooks/train/_template.py` → `python scripts/build_notebooks.py` sinh `train_local.ipynb`, `train_colab.ipynb`, `train_kaggle.ipynb`. Chỉ ô thiết lập môi trường, đường dẫn dữ liệu và lưu kết quả khác nhau; logic nằm ở `src/utci_vision/` (`detector.finetune`, `verifier`, `training.py`), tham số ở `configs/`.
- Chế độ `SMOKE=True` (1 epoch, ~20 ảnh) để kiểm tra mỗi nền tảng chạy hết các ô.
- Mỗi lần chạy sinh `<run_id>/` gồm trọng số + `run_record.json` (cấu hình, metric, commit, **phiên bản torch/CUDA/GPU**, nền tảng). Ở local, `python scripts/import_run.py <thư-mục> --promote` đưa vào `models/current/` và ghi `experiments/registry.csv`.
- Lưu ý nền tảng: Windows local đặt `workers=0` trong Jupyter; Colab lưu `last.pt` lên Drive để resume khi mất phiên; Kaggle 12 giờ/phiên, ~30 giờ GPU/tuần.

## 7. Môi trường & thư viện

- **Khoá phiên bản chính xác** các thư viện dùng chung trong `requirements.txt` (numpy, opencv, scikit-learn, lightgbm, ultralytics, fastapi…).
- **Không khoá** torch/torchvision/CUDA/`nvidia-*`/triton: mỗi người tự cài theo GPU; chỉ yêu cầu tối thiểu `torch >= 2.4` (Ultralytics loại trừ 2.4.0 trên Windows).
- Thứ tự cài: torch tự chọn → `pip install -r requirements.txt` → `pip install --no-deps vietocr==0.3.13` (VietOCR khoá cứng thư viện cũ như `imgaug`, `pillow==10.2.0`, không tương thích numpy 2 — nên cài không kèm phụ thuộc, các phụ thuộc cần thiết đã có trong requirements).
- `make check-env` kiểm tra torch/CUDA/GPU + cổng; `make freeze` sinh `requirements.lock` đã lọc các gói GPU.
- **Cổng custom** (ADR-007): `.env` là nguồn duy nhất — API 18100, web 18080, Vite 15173, Jupyter 18888; không tiến trình nào dùng 8000/8080/5173/8888/80.
- **Makefile chỉ cho DevOps**: môi trường, CI (`make ci`), Docker (`make up`); dữ liệu / fine-tune / đánh giá / chạy dev gọi trực tiếp `scripts/`, notebook, `npm`.
- Docker là nơi duy nhất cố định torch (image CPU: torch CPU; image GPU: `pytorch/pytorch:2.14.1-cuda12.6-cudnn9-runtime`).

## 8. Đánh giá (cho báo cáo)

| Mã | Nội dung | Metric |
|---|---|---|
| E1 | Toàn hệ thống trên test v1 | mAP@50, mAP@50:95, P, R, macro-F1, AP theo lớp & kích thước, FPS, độ trễ API |
| E2 | **Ablation**: YOLO thuần → + tăng cường CV → + xác minh ML → + tracking | ΔmAP, ΔPrecision, Δflicker, ΔFPS |
| E3 | Cấu hình fine-tune YOLO11: n vs s, `imgsz` 640 vs 960, `freeze` 0 vs 10; bộ xác minh LogReg vs RF vs LightGBM | mAP, FPS, thời gian fine-tune; AUC/precision của bộ xác minh |
| E4 | Độ bền: tối, mờ, nhiễu, mưa nhân tạo ± tăng cường | ΔmAP |
| E5 | Đọc số và chữ: VietOCR (+ regex / từ điển) vs EasyOCR; ± bước cắt vùng CV | Accuracy giá trị, CER, exact match |
| E6 | Video ± tracking | Flicker rate, số thông báo sai |
| E7 | Giải thích | Feature importance LightGBM, ảnh trung gian từng khâu |

Mục tiêu ban đầu: mAP@50 ≥ 0.80 · precision sau xác minh ≥ 0.90 · đọc số ≥ 85% · OCR ≥ 80% exact match (crop ≥ 60 px) · webcam qua web ≥ 20 FPS (GPU) · ảnh tĩnh ≤ 1,5 s trên CPU trong Docker. Do chia lại dữ liệu, số liệu không so sánh trực tiếp với repo tham khảo (mAP@50 0.78).

## 9. Phân công

| TV | Phụ trách chính |
|---|---|
| **TV1** | Tech lead; ML (bộ xác minh LightGBM); hậu xử lý OCR (regex số, từ điển chữ); đánh giá & ablation; review |
| **TV2** | CV (tăng cường, đặc trưng vùng, tracking, cắt vùng số / dòng chữ / biển phụ); frontend React |
| **TV3** | Fine-tune YOLO11; 3 notebook; tích hợp pipeline; FastAPI + WebSocket; tích hợp VietOCR; Docker/Makefile/CI; tối ưu hiệu năng |
| **TV4** | Báo cáo, slide, video demo; nội dung ý nghĩa biển; từ điển chữ biển phụ |
| **TV5** | Lọc, chia lại, đóng gói dữ liệu; nhãn đánh giá OCR (giá trị số + chữ); video thử; benchmark; kiểm thử chấp nhận web |

TV2 tải nặng (CV + frontend): từ S3 TV3 nhận bớt phần frontend nếu cần.

## 10. Lộ trình (23/10 → 04/12/2026, sprint chuyển vào thứ Sáu)

| Sprint | Trọng tâm | Kết quả cuối sprint |
|---|---|---|
| S1 | Khởi động & nền tảng | Repo/CI/Makefile; môi trường từng người (`make check-env`); dữ liệu audit + duyệt; 3 notebook smoke test; fine-tune baseline YOLO11s + **benchmark FPS**; khung API/web/Docker chạy; chốt schema JSON; khung báo cáo |
| S2 | Dữ liệu v1 & lõi | `processed/v1` + gói dữ liệu trên Drive/Kaggle; fine-tune YOLO11s 960 trên v1; tăng cường CV + tracking; web upload ảnh trong Docker; spike OCR + gán nhãn chữ |
| S3 | MVP | LightGBM xác minh; đọc số bằng VietOCR + regex; job video; trang Thư viện biển; E1 sơ bộ |
| S4 | Realtime & OCR | Webcam WebSocket; OCR tiếng Việt + biển phụ chạy nền; trang Giải thích; E4, E5 |
| S5 | Tối ưu & chốt | Tối ưu FPS; model freeze; ablation E2 đầy đủ; kiểm thử chấp nhận; bản nháp báo cáo |
| S6 | Hoàn thiện | Sửa lỗi, tag v1.0, Docker hoàn chỉnh; báo cáo cuối, slide, video; diễn tập bảo vệ |

## 11. Rủi ro chính

| Rủi ro | Phương án |
|---|---|
| Biển quá nhỏ để đọc chữ | Chờ frame gần nhất trong track; chấp nhận không đọc với biển xa |
| LightGBM không cải thiện so với YOLO thuần | Vẫn là kết quả ablation hợp lệ; tối thiểu tăng precision |
| VietOCR khoá thư viện cũ | Cài `--no-deps`; kiểm chứng ở S1; dự phòng EasyOCR (hỗ trợ tiếng Việt) |
| GPU trong Docker trên Windows | Image CPU mặc định; profile GPU có hướng dẫn riêng |
| Thiếu GPU / hết quota | Chia lượt train giữa tài khoản Kaggle/Colab của các thành viên |
| Kết quả lệch giữa các máy (torch/CUDA khác nhau) | `run_record.json` ghi môi trường; số liệu chính thức chỉ lấy từ một nền tảng cố định |
| Khối lượng frontend | Giao diện tối giản; TV3 hỗ trợ |

## 12. Tài liệu tham khảo

1. G. Jocher, J. Qiu. *Ultralytics YOLO11*. 2024. https://github.com/ultralytics/ultralytics
2. pbcquoc. *VietOCR — Transformer OCR cho tiếng Việt*. https://github.com/pbcquoc/vietocr
3. A. Bewley et al. *Simple Online and Realtime Tracking (SORT)*. ICIP 2016.
4. G. Ke et al. *LightGBM: A Highly Efficient Gradient Boosting Decision Tree*. NeurIPS 2017.
5. D. H. Wolpert. *Stacked Generalization*. Neural Networks, 1992.
6. N. Dalal, B. Triggs. *Histograms of Oriented Gradients for Human Detection*. CVPR 2005.
7. M.-K. Hu. *Visual Pattern Recognition by Moment Invariants*. 1962.
8. K. Zuiderveld. *Contrast Limited Adaptive Histogram Equalization*. Graphics Gems IV, 1994.
9. C. Ertler et al. *The Mapillary Traffic Sign Dataset*. ECCV 2020. https://arxiv.org/abs/1909.04422
10. *Traffic sign recognition with color segmentation, HOG and CNN*. https://iris.unint.eu/handle/20.500.14090/6262
11. *Hybrid Image Improving and CNN (HIICNN) Stacking Ensemble for Traffic Sign Recognition*. IEEE Access 2023. https://doaj.org/article/ee79e9b6bbaf4384b11572a9d4f9eb4a
12. Bộ GTVT. *QCVN 41:2019/BGTVT — Quy chuẩn kỹ thuật quốc gia về báo hiệu đường bộ*.
13. Mã tham khảo: https://github.com/Secret350/Real-time-Traffic-Objects-Detection
14. Repo dự án: https://github.com/HoanBuCon/UTCI-Vision
