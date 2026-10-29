# Nguồn DUY NHẤT của 3 notebook fine-tune (ADR-006). KHÔNG sửa file .ipynb — sửa file này rồi chạy `python scripts/build_notebooks.py`.
# Cú pháp ô:  "# %%" ô code chung · "# %% [markdown]" ô markdown chung
#             "# %% [colab]" / "# %% [kaggle]" / "# %% [local]" / "# %% [markdown, kaggle]" chỉ có ở notebook tương ứng.

# %% [markdown]
# # UTCI-VISION — Notebook fine-tune ({platform})
#
# Repo: https://github.com/HoanBuCon/UTCI-Vision
#
# **Fine-tune, không train lại từ đầu:** YOLO11 khởi tạo từ trọng số pretrained COCO (hoặc checkpoint của nhóm qua `INIT_WEIGHTS`).
# Sau đó *fit* **bộ xác minh LightGBM** (ML cổ điển) trên dự đoán của YOLO ở tập val. VietOCR dùng pretrained, không huấn luyện ở đây.
# Mọi việc khác (dữ liệu, đánh giá test, API, web, Docker) chạy bằng mã nguồn local.
#
# Cách dùng: sửa ô **Cấu hình** → *Run all*. Chạy thử nhanh: `SMOKE = True` (1 epoch, ~1% dữ liệu).
# Kết quả: thư mục `<run_id>/` (trọng số + `run_record.json`) → ở local: `python scripts/import_run.py <thư-mục> --promote`.

# %% [markdown, colab]
# **Colab:** Runtime → Change runtime type → GPU. Đặt `utci_v1.zip` + `utci_v1.sha256` ở `MyDrive/UTCI_VISION/data/`
# (chưa có thì ô Dữ liệu hiện nút chọn file từ máy và tự lưu lên Drive).
# Kết quả ghi thẳng vào `MyDrive/UTCI_VISION/runs/` nên không mất khi phiên bị ngắt; đặt `RESUME` để chạy tiếp.

# %% [markdown, kaggle]
# **Kaggle:** Settings → Accelerator GPU T4×2/P100; bật **Internet**; Add Input → Dataset riêng tư `utci-v1`.
# Giới hạn 12 giờ/phiên. Kết quả ở `/kaggle/working/runs/` — tải file `.zip` cuối notebook.

# %% [markdown, local]
# **Local:** kernel của `.venv` dự án (torch tự cài theo GPU — ADR-005). Windows giữ `WORKERS = 0` để DataLoader không treo trong Jupyter.

# %%
# ===== Cấu hình =====
AUTHOR = "TV3"
MODEL = "yolo11s.pt"          # pretrained COCO: yolo11n.pt | yolo11s.pt
INIT_WEIGHTS = None           # fine-tune tiếp từ checkpoint của nhóm (.pt); None = từ pretrained COCO
FREEZE = 0                    # 0 = fine-tune toàn bộ · 10 = đóng băng backbone
IMGSZ = 960                   # 640 | 960
EPOCHS = 80
BATCH = 8
SMOKE = False                 # True: chạy thử toàn bộ notebook trong vài phút
FINETUNE_YOLO = True
FIT_VERIFIER = False          # Sprint 3 — cần YOLO đã fine-tune (của run này hoặc YOLO_WEIGHTS)
YOLO_WEIGHTS = None           # YOLO đã fine-tune, dùng khi FINETUNE_YOLO = False
RESUME = None                 # last.pt của lần chạy bị ngắt -> chạy tiếp (không phải lần fine-tune mới)
DATASET_VERSION = "v1"
REPO_URL = "https://github.com/HoanBuCon/UTCI-Vision.git"
BRANCH = "develop"            # nhánh tích hợp; trước khi có develop (S1) dùng "main"

# %% [local]
import os
import sys
from pathlib import Path

ROOT = Path.cwd().resolve().parents[1]  # notebooks/train -> gốc dự án
sys.path.insert(0, str(ROOT / "src"))
DATA_ROOT = ROOT / "dataset" / "processed" / DATASET_VERSION
OUT_ROOT = ROOT / "runs_out"
WORKERS = 0 if os.name == "nt" else 4
DEVICE = 0

# %% [colab]
import subprocess
import sys
from pathlib import Path

from google.colab import drive

drive.mount("/content/drive")
DRIVE = Path("/content/drive/MyDrive/UTCI_VISION")
ROOT = Path("/content/UTCI-Vision")
if not ROOT.exists():
    subprocess.run(["git", "clone", "-b", BRANCH, "--depth", "1", REPO_URL, str(ROOT)], check=True)
# torch có sẵn trên Colab — chỉ cài thư viện dùng chung (ADR-005)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(ROOT / "requirements.txt")], check=True)
sys.path.insert(0, str(ROOT / "src"))
DATA_ZIP = DRIVE / "data" / f"utci_{DATASET_VERSION}.zip"
DATA_ROOT = Path("/content/data")  # giải nén ra ổ VM (nhanh hơn đọc từ Drive)
OUT_ROOT = DRIVE / "runs"
WORKERS = 2
DEVICE = 0

# %% [kaggle]
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/kaggle/working/UTCI-Vision")
if not ROOT.exists():
    subprocess.run(["git", "clone", "-b", BRANCH, "--depth", "1", REPO_URL, str(ROOT)], check=True)
# torch có sẵn trên Kaggle — chỉ cài thư viện dùng chung (ADR-005)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(ROOT / "requirements.txt")], check=True)
sys.path.insert(0, str(ROOT / "src"))
INPUT_DIR = Path(f"/kaggle/input/utci-{DATASET_VERSION}")  # Kaggle tự giải nén zip khi upload
DATA_ROOT = Path("/kaggle/working/data")  # bản sao ghi được (Ultralytics ghi cache nhãn)
OUT_ROOT = Path("/kaggle/working/runs")
WORKERS = 2
DEVICE = 0  # "0,1" để dùng 2 GPU T4

# %%
# ===== Kiểm tra môi trường (torch/CUDA/GPU tự cài) =====
import json

from utci_vision.env import check_environment, environment_summary

print(json.dumps(environment_summary(), ensure_ascii=False, indent=2))
for warning in check_environment():
    print("[!]", warning)

# %% [local]
# ===== Dữ liệu =====
from utci_vision.training import verify_extracted, write_data_yaml

DATASET_DIR = DATA_ROOT
DATASET_SHA = verify_extracted(DATASET_DIR) if (DATASET_DIR / "VERSION.json").exists() else None
DATA_YAML = write_data_yaml(DATASET_DIR)

# %% [colab]
# ===== Dữ liệu: kiểm tra checksum zip -> giải nén =====
from utci_vision.training import extract_dataset, verify_checksum, write_data_yaml

DATA_SHA = DATA_ZIP.with_suffix(".sha256")
if not (DATA_ZIP.exists() and DATA_SHA.exists()):
    # Dự phòng: chưa có trên Drive -> chọn file từ máy (chậm với ~600 MB), lưu lên Drive để lần sau không phải tải lại
    from google.colab import files

    print(f"Không thấy {DATA_ZIP.name} / {DATA_SHA.name} trong {DATA_ZIP.parent} — chọn CẢ HAI file từ máy:")
    DATA_ZIP.parent.mkdir(parents=True, exist_ok=True)
    for name, content in files.upload().items():  # trình duyệt có thể đổi tên ("utci_v1 (1).zip") -> lưu theo đuôi
        target = {".zip": DATA_ZIP, ".sha256": DATA_SHA}.get(Path(name).suffix)
        if target is not None:
            target.write_bytes(content)
    assert DATA_ZIP.exists() and DATA_SHA.exists(), f"Cần cả {DATA_ZIP.name} và {DATA_SHA.name}"

DATASET_SHA = verify_checksum(DATA_ZIP, DATA_SHA)
DATASET_DIR = extract_dataset(DATA_ZIP, DATA_ROOT)
DATA_YAML = write_data_yaml(DATASET_DIR)

# %% [kaggle]
# ===== Dữ liệu: kiểm tra VERSION.json -> sao chép sang thư mục ghi được =====
from utci_vision.training import find_dataset_dir, verify_extracted, write_data_yaml

src_dir = find_dataset_dir(INPUT_DIR)
DATASET_SHA = verify_extracted(src_dir)
if not DATA_ROOT.exists():
    shutil.copytree(src_dir, DATA_ROOT)
DATASET_DIR = DATA_ROOT
DATA_YAML = write_data_yaml(DATASET_DIR)

# %%
# ===== Tạo run =====
from utci_vision.config import load_config
from utci_vision.training import RunRecord, new_run_id

RUN_ID = new_run_id(MODEL, IMGSZ, SMOKE)
RUN_DIR = OUT_ROOT / RUN_ID
overrides = {"imgsz": IMGSZ, "epochs": EPOCHS, "batch": BATCH, "freeze": FREEZE, "workers": WORKERS, "device": DEVICE}
record = RunRecord(run_id=RUN_ID, author=AUTHOR, dataset_version=DATASET_VERSION, dataset_sha256=DATASET_SHA,
                   smoke=SMOKE, config={"model": MODEL, "init_weights": INIT_WEIGHTS, **overrides})
print(DATA_YAML, DATASET_SHA, RUN_DIR, sep="\n")

# %%
# ===== [DL] Fine-tune YOLO11 =====
from utci_vision import detector

if FINETUNE_YOLO:
    yolo_cfg = load_config("yolo") | {"model": MODEL}
    record.metrics["yolo"] = detector.finetune(DATA_YAML, RUN_DIR, yolo_cfg, overrides, smoke=SMOKE,
                                               init_weights=Path(INIT_WEIGHTS) if INIT_WEIGHTS else None,
                                               resume=Path(RESUME) if RESUME else None)
    record.artifacts.append("yolo11.pt")
    YOLO_WEIGHTS = RUN_DIR / "yolo11.pt"
    print(record.metrics["yolo"])

# %%
# ===== [CV+ML] Fit bộ xác minh LightGBM trên dự đoán YOLO ở tập val (stacking) =====
from utci_vision import verifier

if FIT_VERIFIER:
    ver_cfg = load_config("verifier")
    df = verifier.build_dataset(Path(YOLO_WEIGHTS), DATASET_DIR / "val", ver_cfg, limit=50 if SMOKE else None)
    record.metrics["verifier"] = verifier.train(df, RUN_DIR, ver_cfg)
    record.artifacts.append("verifier.joblib")

# %%
# ===== Lưu run_record.json =====
print(record.save(RUN_DIR).read_text(encoding="utf-8"))

# %% [kaggle]
# ===== Nén kết quả để tải về =====
print("Tải file:", shutil.make_archive(str(OUT_ROOT / RUN_ID), "zip", RUN_DIR))

# %% [markdown, local]
# **Tiếp theo:** `python scripts/import_run.py runs_out/<RUN_ID> --promote` (đưa trọng số vào `models/current/` + ghi `experiments/registry.csv`).

# %% [markdown, colab]
# **Tiếp theo:** tải `MyDrive/UTCI_VISION/runs/<RUN_ID>/` về máy rồi `python scripts/import_run.py <thư-mục> --promote`.

# %% [markdown, kaggle]
# **Tiếp theo:** tải `runs/<RUN_ID>.zip`, giải nén rồi `python scripts/import_run.py <thư-mục> --promote`.
