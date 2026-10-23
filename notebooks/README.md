# Notebooks fine-tune (ADR-006)

| File | Dùng ở |
|---|---|
| `train/_template.py` | **Nguồn duy nhất** — chỉ sửa file này, rồi `python scripts/build_notebooks.py` |
| `train/train_local.ipynb` | Máy cá nhân (kernel `.venv`, torch tự cài; `jupyter lab --config jupyter_server_config.py` mở JupyterLab trên `UTCI_JUPYTER_PORT`) |
| `train/train_colab.ipynb` | Google Colab — `git clone` https://github.com/HoanBuCon/UTCI-Vision; dữ liệu `MyDrive/UTCI_VISION/data/`, kết quả `MyDrive/UTCI_VISION/runs/` |
| `train/train_kaggle.ipynb` | Kaggle — Dataset riêng tư `utci-v1`, bật Internet + GPU |

YOLO11 được **fine-tune** từ pretrained COCO (hoặc `INIT_WEIGHTS`), không train lại từ đầu. Chạy thử: `SMOKE = True` → *Run all*.
Kết quả `<run_id>/` → `python scripts/import_run.py <thư-mục> --promote`. Notebook khám phá cá nhân không commit vào repo.
