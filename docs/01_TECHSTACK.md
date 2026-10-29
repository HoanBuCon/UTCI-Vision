# UTCI-VISION — Techstack (v3.0)

| Thuộc tính | Giá trị |
|---|---|
| Ngày | 2026-10-22 |
| Chủ sở hữu | TV1 (Tech Lead) |
| Repo | https://github.com/HoanBuCon/UTCI-Vision |
| Liên quan | 00_PHUONG_AN.md, 02_SRS.md, ADR-003…007, `requirements*.txt`, `Makefile`, `.env.example`, `web/package.json` |

## 1. Stack tổng quan

| Lớp | Công nghệ | Dùng cho |
|---|---|---|
| Ngôn ngữ | **Python 3.11** (tối thiểu; 3.12 trên Colab/Kaggle) · **TypeScript** | Pipeline + backend · frontend |
| DL — detector | **Ultralytics YOLO11** (`yolo11s` pretrained COCO) trên **PyTorch** (tự cài) | **Fine-tune** phát hiện + phân loại 27 lớp |
| DL — OCR | **VietOCR** (`vgg_transformer`, pretrained) | Đọc số trên biển và chữ tiếng Việt có dấu (dùng sẵn; fine-tune là Could) |
| CV truyền thống | **OpenCV 4.x**, **scikit-image** | Đánh giá chất lượng & tăng cường, đặc trưng màu/hình dạng/Hu/HOG, cắt vùng số / dòng chữ / biển phụ, Kalman |
| ML | **LightGBM**, **scikit-learn** (PCA, hiệu chỉnh xác suất; LogReg/RF để so sánh) | Bộ xác minh — fit trên đặc trưng |
| Hậu xử lý OCR | **rapidfuzz** + regex | Hợp lệ hoá số theo đơn vị; khớp từ điển chữ; trích khung giờ / khoảng cách / loại xe |
| Dữ liệu | numpy, pandas, Pillow, imagehash, PyYAML | Audit, gom ảnh trùng, chia lại, đóng gói |
| Backend | **FastAPI** + **Uvicorn**, Pydantic v2 | REST + WebSocket |
| Frontend | **React 19** + **Vite** + TypeScript, React Router | Ảnh / Video / Webcam / Thư viện / Giải thích |
| Phục vụ web | **Nginx** (template cổng theo env) | File tĩnh + reverse-proxy `/api` (kể cả WebSocket) |
| Triển khai | **Docker Compose** | `api` (CPU mặc định, profile `gpu`) + `web` |
| DevOps | **Makefile**, `.env` (cổng custom), pre-commit, GitHub Actions | Một lệnh cho mọi tiến trình |
| Fine-tune | **3 notebook** Local / Google Colab / Kaggle sinh từ một template (nbformat) | ADR-006 |
| Theo dõi thí nghiệm | `run_record.json` + `experiments/registry.csv` | Không phụ thuộc dịch vụ ngoài |
| Chất lượng code | ruff (lint + format), pytest, `tsc --noEmit` strict | `make ci` |
| Lưu trữ | Google Drive (dataset zip, trọng số), Kaggle Dataset riêng tư, GitHub Release | Không commit dữ liệu/trọng số |
| Quản lý công việc | Trello *faketime-traffic-signs-cant-detect* (`planning/`) | |
| Báo cáo | Word hoặc LaTeX/Overleaf (TBD-2) | |

## 2. Quyết định chính

| ADR | Quyết định | Lý do ngắn |
|---|---|---|
| 001 | YOLO11 làm lõi; CV/ML/OCR theo track, bất đồng bộ | Mỗi kỹ thuật có vai trò thật; chỉ YOLO trên đường găng realtime |
| 002 | Chia lại dữ liệu theo cụm gần trùng | 6/32 lớp không có trong test gốc; 37% ảnh gần trùng |
| 009 | Gộp 6 lớp hiếm vào "Biển báo khác" (32 → 27 lớp) | 6 lớp chỉ có 25–54 cụm cảnh độc lập |
| 003 | React + FastAPI + Docker Compose | Demo web chạy được mọi máy; webcam qua WebSocket |
| 004 | **Fine-tune** YOLO11 từ pretrained, không train từ đầu | Dữ liệu ~5,4k ảnh — quá ít để train từ đầu; tiết kiệm GPU |
| 005 | Không khoá torch/CUDA | GPU mỗi người khác nhau |
| 006 | Fine-tune qua 3 notebook từ một template | Đồng bộ nền tảng; việc khác chạy local |
| — | Mã nguồn tổ chức theo **khâu pipeline**, không theo kỹ thuật (bỏ `cv/`, `ml/`, `dl/`) | Mỗi khâu một file, một người phụ trách; nhãn CV/ML/DL ghi trong docstring và bảng §8 |
| 007 | Cổng custom qua `.env` + Makefile | Tránh xung đột cổng mặc định; một lệnh cho mọi tiến trình |

## 3. Chính sách phiên bản (ADR-005)

| Nhóm | Quản lý | File |
|---|---|---|
| Thư viện dùng chung | **Khoá chính xác** (`==`) | `requirements.txt`, `requirements-dev.txt` |
| VietOCR | Khoá `==`, cài **`--no-deps`** (gói khoá cứng `imgaug`, `pillow==10.2.0`… không hợp numpy 2) | `requirements-nodeps.txt` |
| torch, torchvision, CUDA, `nvidia-*`, triton | **Không khoá** — mỗi người tự cài; tối thiểu `torch >= 2.4` (không dùng 2.4.0 trên Windows) | — |
| Frontend | Khoá trong `web/package-lock.json` | `web/package.json` |
| Docker | Cố định toàn bộ, kể cả torch | `docker/*.Dockerfile` |

### 3.1 Phiên bản đã khoá (kiểm tra 2026-10-22; `pip install --dry-run` resolve sạch 119 gói)

| Thư viện | Phiên bản | Ghi chú |
|---|---|---|
| ultralytics | 8.4.183 | YOLO11; loại trừ `opencv-python 4.13.0.90` |
| opencv-python | 4.14.0.94 | Giữ 4.x |
| numpy / scipy / pandas | 2.4.6 / 1.17.1 / 3.1.0 | pandas 3 cần Python ≥ 3.11 |
| scikit-image / scikit-learn / lightgbm / joblib | 0.26.0 / 1.9.1 / 4.7.0 / 1.6.0 | |
| pillow / pyyaml / imagehash / tqdm / matplotlib / rapidfuzz | 13.0.0 / 6.0.3 / 4.3.2 / 4.70.1 / 3.11.2 / 3.14.6 | |
| vietocr (+ einops / gdown / lmdb) | 0.3.13 (+ 0.8.2 / 6.4.2 / 3.0.0) | Đã chạy thử với torch 2.14.1 CPU: "Trừ xe buýt", "6h - 22h" đúng; ~120–290 ms/dòng CPU |
| fastapi / uvicorn / pydantic / python-multipart | 0.159.1 / 0.54.0 / 2.14.1 / 0.0.32 | |
| pytest / httpx / ruff / pre-commit / nbformat / jupyterlab | 9.1.1 / 0.28.1 / 0.17.1 / 4.7.0 / 5.11.1 / 4.6.4 | Dev |
| react / react-router-dom / vite / @vitejs/plugin-react / typescript | 19.3.1 / 7.18.4 / 8.3.5 / 6.1.2 / 5.9.3 | Frontend |
| Node.js | 22 LTS | |
| Docker base | `python:3.11-slim` + torch 2.14.1 CPU · `pytorch/pytorch:2.14.1-cuda12.6-cudnn9-runtime` · `node:22-alpine` · `nginx:1.31-alpine` | |

EasyOCR chỉ dùng làm mốc so sánh (E5), cài riêng khi đánh giá — không vào requirements (kéo `opencv-python-headless` xung đột).

## 4. Cổng dịch vụ (ADR-007) — không dùng cổng mặc định

| Biến `.env` | Mặc định dự án | Tránh cổng mặc định | Dùng bởi |
|---|---|---|---|
| `UTCI_API_PORT` | **18100** | 8000 (uvicorn) | FastAPI (`python -m utci_vision.api --reload`, container `api`) |
| `UTCI_WEB_PORT` | **18080** | 80 / 8080 (nginx) | Nginx trong container `web` (listen + publish) |
| `UTCI_DEV_PORT` | **15173** | 5173 (Vite) | `npm run dev`, `npm run preview` trong `web/` (`strictPort`) |
| `UTCI_JUPYTER_PORT` | **18888** | 8888 (Jupyter) | `jupyter lab --config jupyter_server_config.py` (file config đọc `.env`, `port_retries=0`) |

Một nguồn duy nhất: `.env` (tạo bằng `make env` từ `.env.example`). Python đọc qua `utci_vision.env.Ports`, Vite qua `loadEnv("..", "UTCI_")`,
Docker Compose qua nội suy `${UTCI_*}`, Nginx qua `nginx.conf.template` (envsubst khi khởi động). Container `api` chỉ `expose` nội bộ — truy cập từ ngoài qua `web`.

## 5. Makefile — chỉ DevOps

| Nhóm | Lệnh `make` |
|---|---|
| Môi trường | `env` · `venv` (rồi tự cài torch) · `install` (pip + VietOCR `--no-deps` + package + `npm ci` + pre-commit) · `check-env` · `freeze` |
| Chất lượng / CI | `lint` · `format` · `test` · `ci` (lint + test + notebook khớp template + build web + compose hợp lệ) |
| Docker | `build` · `up` · `up-gpu` · `down` · `logs` · `ps` · `clean` |

Không đưa vào Makefile các việc nghiệp vụ — chạy trực tiếp:

| Việc | Lệnh |
|---|---|
| Dữ liệu | `python scripts/data.py {audit --dedup, split, crops, package}` |
| Fine-tune | 3 notebook; sinh lại: `python scripts/build_notebooks.py`; nhập kết quả: `python scripts/import_run.py <thư-mục> --promote` |
| Đánh giá | `python scripts/evaluate.py {detect, benchmark}` |
| Dev | `python -m utci_vision.api --reload` · `cd web && npm run dev` · `jupyter lab --config jupyter_server_config.py` |

Windows: chạy `make` trong Git Bash (GNU Make 4.x). Makefile đặt `PYTHONUTF8=1`; khi chạy script trực tiếp trên console Windows nên đặt `PYTHONUTF8=1` để in tiếng Việt.

## 6. Cài đặt môi trường dev

```bash
git clone https://github.com/HoanBuCon/UTCI-Vision.git && cd UTCI-Vision
make env && make venv
# TỰ cài PyTorch theo GPU/driver: https://pytorch.org/get-started/locally/
#   CUDA 12.6: .venv/Scripts/python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
#   CPU:       .venv/Scripts/python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
make install && make check-env && make ci
```

## 7. Fine-tune (ADR-004, ADR-006)

- **YOLO11:** khởi tạo từ `yolo11s.pt` pretrained COCO (hoặc checkpoint của nhóm qua `INIT_WEIGHTS`), `AdamW`, `lr0 = 0.001`, cosine LR,
  warmup 3 epoch, ~80 epoch, `freeze` 0 (toàn bộ) hoặc 10 (đóng băng backbone — so sánh ở E3). `RESUME` chỉ để chạy tiếp một lần bị ngắt.
- **VietOCR:** dùng trọng số pretrained; fine-tune trên crop biển báo là Could (FR-TRAIN-10).
- **LightGBM:** mô hình cổ điển — *fit* trên đặc trưng sinh từ YOLO đã fine-tune (không có khái niệm pretrained).
- Không có SVM chữ số: số trên biển do VietOCR đọc, regex hợp lệ hoá (quyết định 2026-10-23).

| Notebook | Môi trường | Dữ liệu | Kết quả |
|---|---|---|---|
| `train_local.ipynb` | `.venv` dự án | `dataset/processed/v1` | `runs_out/<run_id>/` |
| `train_colab.ipynb` | torch có sẵn; `git clone` repo + `pip install -r requirements.txt` | zip trên Drive → giải nén `/content/data` | `MyDrive/UTCI_VISION/runs/<run_id>/` |
| `train_kaggle.ipynb` | torch có sẵn; bật Internet | Kaggle Dataset `utci-v1` (kiểm tra `VERSION.json`) | `/kaggle/working/runs/<run_id>.zip` |

Nguồn duy nhất `notebooks/train/_template.py` → `python scripts/build_notebooks.py`; pre-commit và CI kiểm tra notebook khớp template.
Sau mỗi lần chạy: `python scripts/import_run.py <thư-mục> --promote` → `models/current/` + `experiments/registry.csv`.

## 8. Cấu trúc mã nguồn

```
UTCI-Vision/
├── Makefile (DevOps) · .env.example · docker-compose.yml · pyproject.toml · requirements{,-dev,-nodeps}.txt · jupyter_server_config.py
├── configs/            classes · data · yolo · pipeline · verifier · ocr (+ ocr_lexicon.txt) · api
├── src/utci_vision/    mỗi module ở gốc = một khâu của pipeline (nhãn kỹ thuật trong docstring)
│   ├── pipeline.py     điều phối: Components (mô hình nạp một lần) + Recognizer (mỗi nguồn ảnh/video)
│   ├── enhance.py      [CV]      đánh giá chất lượng frame + tăng cường thích nghi
│   ├── detector.py     [DL]      YOLO11: fine-tune từ pretrained + suy luận
│   ├── tracking.py     [CV]      Kalman + ghép IoU + bỏ phiếu nhãn
│   ├── verifier.py     [CV+ML]   đặc trưng vùng (màu/hình dạng/Hu/HOG) + LightGBM
│   ├── ocr.py          [CV+DL]   cắt vùng số/chữ/biển phụ + VietOCR + regex/từ điển
│   ├── structures.py   Detection, SignValue, SignText
│   ├── config.py · env.py (cổng .env, torch/CUDA/GPU, git commit)
│   ├── training.py     tiện ích notebook: kiểm tra dữ liệu, RunRecord
│   ├── registry.py · visualize.py
│   ├── data/           labels · audit · dedup · split · crops · package
│   ├── evaluation/     metrics (IoU, mAP) · experiments (ablation, suy giảm, FPS)
│   └── api/            main (app factory) · routes (REST + WebSocket) · schemas · jobs · __main__
├── scripts/            data · evaluate · infer · import_run · build_notebooks · env
├── notebooks/train/    _template.py + 3 notebook sinh tự động
├── web/                React + Vite + TS · Dockerfile · nginx.conf.template
├── docker/             api.Dockerfile · api.gpu.Dockerfile
├── tests/              test_config_env · test_data · test_evaluation · test_training · test_api
├── experiments/registry.csv · models/ (gitignore) · docs/ · report/ · planning/
```

## 9. Docker

```bash
make up        # CPU   -> http://localhost:${UTCI_WEB_PORT}
make up-gpu    # GPU   (NVIDIA driver + Docker Desktop WSL2)
```

`./models` mount chỉ đọc vào `/app/models`; `./outputs` giữ video đã xử lý (xoá sau 24 giờ).
**Dung lượng:** image `api` CPU ~1,5–2 GB, GPU ~6–8 GB (cộng thêm cache build). Image nằm ở ổ chứa dữ liệu WSL của Docker Desktop
(Settings → Resources → Disk image location), không phải ổ cài đặt — kiểm tra ổ đó còn trống trước khi `make up-gpu`.

## 10. Mục tiêu hiệu năng

| Chỉ số | Mục tiêu | Đo bằng |
|---|---|---|
| Webcam qua web (GPU, 960×540) | ≥ 20 FPS, p95 ≤ 120 ms | `scripts/evaluate.py benchmark --api` |
| Ảnh tĩnh, Docker CPU | ≤ 1,5 s (không OCR), ≤ 3 s (có OCR) | `scripts/evaluate.py benchmark --api` |
| Tác vụ theo track | giảm FPS luồng chính ≤ 10% | `scripts/evaluate.py benchmark` (bật/tắt `track_tasks`) |
| mAP@50 / precision sau xác minh | ≥ 0.80 / ≥ 0.90 | `python scripts/evaluate.py detect --split test` |

## 11. Quy ước làm việc

Chi tiết nhánh, commit, PR: **[quy_uoc.md](quy_uoc.md)**. Tóm tắt:

- Nhánh: `main` ← `release/*` ← `develop` ← `feature/*`, `fix/*`, `docs/*`, `refactor/*`; `hotfix/*` từ `main`. Không commit trực tiếp `main`/`develop`; PR về `develop`, rebase xử lý conflict, Mentor review; `make ci` xanh trước khi mở PR.
- Commit: Conventional Commits (`feat:`, `fix:`, `data:`, `exp:`, `docs:`, `refactor:`, `test:`, `chore:`).
- Không commit: dataset, `*.pt`, `*.joblib`, video, `runs_out/`, `.env`.
- Không hard-code cổng / đường dẫn: cổng ở `.env`, tham số ở `configs/`.

## 12. Rủi ro kỹ thuật & dự phòng

| Rủi ro | Dự phòng |
|---|---|
| Không cài được torch CUDA | torch CPU ở local, fine-tune trên Colab/Kaggle |
| VietOCR tải trọng số thất bại | Lưu bản sao trên Drive nhóm; `configs/ocr.yaml > reader.weights` trỏ file local |
| Xung đột OpenCV | Chỉ giữ `opencv-python`; `make check-env` cảnh báo |
| Cổng 18xxx bị chiếm trên máy ai đó | Đổi trong `.env` — mọi tiến trình đọc cùng nguồn |
| Ổ đĩa đầy khi build Docker / cài torch | Chuyển Docker disk image và pip cache sang ổ khác |
| Kết quả lệch giữa máy | `run_record.json` ghi môi trường; số liệu báo cáo lấy từ một nền tảng (TBD-5) |
