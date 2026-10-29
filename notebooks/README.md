# Notebooks fine-tune (ADR-006)

| File | Dùng ở |
|---|---|
| `train/_template.py` | **Nguồn duy nhất** — chỉ sửa file này, rồi `python scripts/build_notebooks.py` |
| `train/train_local.ipynb` | Máy cá nhân (kernel `.venv`, torch tự cài; `jupyter lab --config jupyter_server_config.py` mở JupyterLab trên `UTCI_JUPYTER_PORT`) |
| `train/train_colab.ipynb` | Google Colab — `git clone` https://github.com/HoanBuCon/UTCI-Vision; dữ liệu `MyDrive/UTCI_VISION/data/`, kết quả `MyDrive/UTCI_VISION/runs/` |
| `train/train_kaggle.ipynb` | Kaggle — Dataset riêng tư `utci-v1`, bật Internet + GPU |

YOLO11 được **fine-tune** từ pretrained COCO (hoặc `INIT_WEIGHTS`), không train lại từ đầu. Chạy thử: `SMOKE = True` → *Run all*.
Kết quả `<run_id>/` → `python scripts/import_run.py <thư-mục> --promote`. Notebook khám phá cá nhân không commit vào repo.

## Chạy thử (smoke) trên Colab / Kaggle

Hướng dẫn từng bước (Kaggle, Colab, import kết quả): [docs/huong_dan_colab_kaggle.md](../docs/huong_dan_colab_kaggle.md).

Chuẩn bị (máy local, 1 lần mỗi phiên bản dữ liệu): `python scripts/data.py package` → `dataset/packages/utci_v1.zip` + `utci_v1.sha256`.

| | Colab | Kaggle |
|---|---|---|
| Dữ liệu | Upload `utci_v1.zip` + `utci_v1.sha256` vào `MyDrive/UTCI_VISION/data/` | *Datasets → New Dataset*, slug **`utci-v1`**, riêng tư, upload `utci_v1.zip` (Kaggle tự giải nén) |
| Notebook | *File → Upload notebook* `train_colab.ipynb`; *Runtime → Change runtime type → T4 GPU* | *Import notebook* `train_kaggle.ipynb`; *Add Input* → `utci-v1`; *Settings*: Accelerator GPU T4, **Internet on** |
| Chạy | Ô **Cấu hình**: `SMOKE = True`, `BRANCH` = nhánh có code cần thử → *Run all* | như Colab |
| Đạt khi | Ô kiểm tra môi trường không có `[!]`; fine-tune 1 epoch xong; có `yolo11.pt` + `run_record.json` trong `MyDrive/UTCI_VISION/runs/<run_id>/` | như Colab, trong `/kaggle/working/runs/<run_id>/` (*Output*) |

Kết quả smoke chỉ để chứng minh notebook chạy được — không `import_run --promote`. Ghi run_id + thời gian chạy vào thẻ Trello.
