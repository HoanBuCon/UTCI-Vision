# Hướng dẫn chạy fine-tune trên Kaggle / Google Colab

Áp dụng cho các việc còn lại của Sprint 1:

| Việc | Thẻ | Nền tảng khuyên dùng | Thời gian |
|---|---|---|---|
| A. Smoke notebook Kaggle | TV5 | Kaggle | ~10 phút |
| B. Smoke notebook Colab | TV1 | Colab | ~10 phút |
| C. Fine-tune baseline YOLO11s (640, 80 epoch) trên `processed/v1` | TV3 | **Kaggle** (chạy nền, 29 GB RAM) | ~2–3 giờ |
| D. Import kết quả + đánh giá + đo FPS | TV3, TV5 | Máy local | ~10 phút |

> Vì sao không chạy baseline trên máy local? Máy 16 GB RAM: notebook Windows phải để `WORKERS = 0` (~5,5 phút/epoch ≈ 7 giờ),
> chạy script với 2–6 worker thì hết RAM. Kaggle/Colab chạy Linux nên DataLoader nhiều worker không có vấn đề này.

---

## 0. Chuẩn bị (một lần, trên máy local)

1. **Gói dữ liệu** (đã có sẵn nếu ai đó đã chạy; tạo lại khi dữ liệu đổi):

   ```bash
   python scripts/data.py package
   ```

   Kết quả: `dataset/packages/utci_v1.zip` (~611 MB, 5.386 ảnh) và `dataset/packages/utci_v1.sha256`.

2. **Nhánh code**: notebook tự `git clone` repo. Code S1 (Detector, bản sửa SMOKE, `package`) nằm ở
   `feature/S1-catchup` cho tới khi PR được merge vào `develop`. Trước khi merge, đặt trong ô **Cấu hình**:

   ```python
   BRANCH = "feature/S1-catchup"
   ```

   Sau khi merge thì để `BRANCH = "develop"` như mặc định.

3. **Tệp notebook**: `notebooks/train/train_kaggle.ipynb` và `notebooks/train/train_colab.ipynb` (đừng sửa trực tiếp
   trong repo — sửa ô Cấu hình ngay trên Kaggle/Colab).

---

## 1. Kaggle

### 1.1 Tạo Dataset `utci-v1` (một lần)

1. Đăng nhập [kaggle.com](https://www.kaggle.com) → **xác minh số điện thoại** (*Settings → Phone verification*) —
   bắt buộc để bật GPU và Internet.
2. *Create → New Dataset*
   - Kéo thả `utci_v1.zip` (Kaggle tự giải nén).
   - **Title**: `utci-v1` → kiểm tra URL là `kaggle.com/datasets/<user>/utci-v1` (slug phải đúng `utci-v1`,
     notebook đọc `/kaggle/input/utci-v1`).
   - **Visibility**: *Private*. → *Create*. Chờ xử lý xong (vài phút).
3. Chia sẻ cho cả nhóm (tuỳ chọn): trang Dataset → *Settings → Sharing* → thêm tài khoản thành viên.

### 1.2 Mở notebook

1. *Create → New Notebook* → *File → Import Notebook* → chọn `train_kaggle.ipynb`.
2. Thanh bên phải (*Notebook options / Session options*):
   - **Accelerator**: `GPU T4 x2` (hoặc `GPU P100`). Notebook dùng 1 GPU (`DEVICE = 0`).
   - **Internet**: **On** (để `git clone` và `pip install`).
   - **Persistence**: không cần.
3. *Add Input* (biểu tượng **+ Add data**) → tab *Your Work* / *Datasets* → chọn `utci-v1`.
   Kiểm tra: khung *Input* hiện `utci-v1/utci_v1/data.yaml`.

### 1.3 Việc A — Smoke (TV5)

Sửa ô **Cấu hình**:

```python
AUTHOR = "TV5"
SMOKE = True
BRANCH = "feature/S1-catchup"   # hoặc "develop" sau khi merge
```

*Run all* (Ctrl + F9 không có trên Kaggle → nút **Run All**). Kiểm tra từng ô:

| Ô | Đạt khi |
|---|---|
| Clone + cài thư viện | không lỗi (cảnh báo pip về phiên bản gói của Kaggle có thể bỏ qua) |
| Kiểm tra môi trường | `cuda_available: true`, `gpu: Tesla T4`; không có dòng `[!]` |
| Dữ liệu | in ra đường dẫn `data.yaml` + mã SHA (không lỗi `manifest.csv không khớp`) |
| Fine-tune | chạy **1 epoch**, ảnh 320, ~1% dữ liệu — xong trong vài phút |
| run_record | in JSON có `"smoke": true` |
| Nén kết quả | `Tải file: /kaggle/working/runs/<run_id>.zip` |

Báo cáo trên thẻ Trello: `run_id`, thời gian chạy, ảnh chụp ô kiểm tra môi trường. **Không** import/promote kết quả smoke.

### 1.4 Việc C — Baseline YOLO11s (TV3)

Trong cùng notebook, sửa ô **Cấu hình**:

```python
AUTHOR = "TV3"
MODEL = "yolo11s.pt"
INIT_WEIGHTS = None
FREEZE = 0
IMGSZ = 640
EPOCHS = 80
BATCH = 16          # T4 16 GB dư sức; hết VRAM thì giảm 8
SMOKE = False
FINETUNE_YOLO = True
FIT_VERIFIER = False
RESUME = None
BRANCH = "feature/S1-catchup"
```

Chạy **nền** để có thể đóng trình duyệt:

1. Góc phải trên: **Save Version** → *Version type*: **Save & Run All (Commit)** → *Save*.
2. Theo dõi ở trang notebook → tab *Versions* / biểu tượng đồng hồ. Phiên tối đa 12 giờ; quota GPU 30 giờ/tuần/tài khoản.
3. Khi trạng thái **Complete**: mở version → tab **Output** → tải `runs/<run_id>.zip`
   (bên trong: `yolo11.pt`, `run_record.json`, `yolo/` gồm `results.csv`, biểu đồ, `weights/`).

Mốc tham chiếu: epoch 1 trên máy local đạt mAP50 ≈ 0,40; early stopping `patience: 25` có thể dừng trước 80 epoch.

Nếu version **lỗi giữa chừng**: mở log (tab *Logs*) — lỗi hay gặp:

| Lỗi | Cách xử lý |
|---|---|
| `CUDA out of memory` | `BATCH = 8` |
| `git clone ... not found` / `pip ... connection` | Internet chưa bật hoặc chưa xác minh số điện thoại |
| `StopIteration` ở ô Dữ liệu | chưa *Add Input* `utci-v1`, hoặc slug khác `utci-v1` |
| `manifest.csv không khớp` | zip upload bị hỏng/thiếu → upload lại zip mới (*New Version* của Dataset) |

---

## 2. Google Colab

### 2.1 Đưa dữ liệu lên Google Drive (một lần)

Tạo đúng cấu trúc trong *My Drive*:

```
MyDrive/
└── UTCI_VISION/
    ├── data/
    │   ├── utci_v1.zip
    │   └── utci_v1.sha256
    └── runs/            # notebook tự tạo, chứa kết quả
```

Có thể upload qua drive.google.com (kéo thả) hoặc Google Drive for Desktop.

### 2.2 Việc B — Smoke (TV1)

1. [colab.research.google.com](https://colab.research.google.com) → *File → Upload notebook* → `train_colab.ipynb`.
2. *Runtime → Change runtime type* → **T4 GPU** → *Save*.
3. Sửa ô **Cấu hình**: `AUTHOR = "TV1"`, `SMOKE = True`, `BRANCH = "feature/S1-catchup"`.
4. *Runtime → Run all*. Ô đầu sẽ hỏi quyền **Google Drive** → cho phép bằng tài khoản chứa `UTCI_VISION/`.
5. Nếu ô cài thư viện báo *"You must restart the runtime"* (Colab có sẵn bản numpy/opencv khác):
   *Runtime → Restart session* → *Run all* lại (repo đã clone sẽ được bỏ qua).
6. Đạt khi giống bảng ở mục 1.3; kết quả nằm ở `MyDrive/UTCI_VISION/runs/<run_id>/`.

### 2.3 Chạy baseline trên Colab (chỉ khi không dùng được Kaggle)

Cấu hình giống mục 1.4. Lưu ý Colab miễn phí ngắt khi tab không hoạt động lâu hoặc hết quota:

- Giữ tab mở, máy không ngủ.
- Checkpoint lưu mỗi 10 epoch (`save_period: 10`) vào `MyDrive/UTCI_VISION/runs/<run_id>/yolo/weights/`.
- Bị ngắt → mở lại notebook, đặt
  `RESUME = "/content/drive/MyDrive/UTCI_VISION/runs/<run_id>/yolo/weights/last.pt"` → *Run all*: chạy tiếp, không tạo run mới.

---

## 3. Việc D — Đưa kết quả về máy local

1. Giải nén vào `runs_out/` của repo (Kaggle: giải nén `<run_id>.zip`; Colab: tải nguyên thư mục `<run_id>/` từ Drive):

   ```
   runs_out/<run_id>/{yolo11.pt, run_record.json, yolo/}
   ```

2. Import + promote (copy vào `models/<run_id>/` và `models/current/`, ghi `experiments/registry.csv`):

   ```bash
   python scripts/import_run.py runs_out/<run_id> --promote --exp BASELINE --notes "YOLO11s 640, processed/v1, Kaggle T4"
   ```

3. Đánh giá trên tập test (TV3):

   ```bash
   python -c "from pathlib import Path; from utci_vision.detector import validate; from utci_vision.training import write_data_yaml; r = validate(Path('models/current/yolo11.pt'), write_data_yaml(Path('dataset/processed/v1')), 640, 'test', device=0); print({k: v for k, v in r.items() if k != 'ap50_per_class'}); print(sorted(r['ap50_per_class'].items(), key=lambda kv: kv[1])[:8])"
   ```

   Ghi mAP50, mAP50-95 và 8 lớp AP thấp nhất vào thẻ Trello / báo cáo mốc S1 (TV4).

4. Đo FPS với trọng số đã fine-tune (TV5):

   ```bash
   python scripts/evaluate.py --author TV5 benchmark --yolo-only --source dataset/processed/v1/test --imgsz 640 --device 0
   ```

5. Commit `experiments/registry.csv` (trọng số trong `models/` không commit — chia sẻ qua Drive).

---

## 4. Checklist hoàn thành Sprint 1

- [ ] A. Smoke Kaggle OK — run_id: ………
- [ ] B. Smoke Colab OK — run_id: ………
- [ ] C. Baseline xong — run_id: ……… · mAP50 (val): ……… · số epoch: ………
- [ ] D. Đã `import_run --promote`; mAP50 test: ………; FPS: ………
- [ ] PR `feature/S1-catchup` → `develop` đã được Mentor review + merge
- [ ] Cập nhật thẻ Trello tương ứng
