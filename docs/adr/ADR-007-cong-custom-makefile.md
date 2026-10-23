# ADR-007: Cổng custom qua `.env` + Makefile cho DevOps

- **Trạng thái:** Accepted (nhóm duyệt 2026-10-22)

## Bối cảnh
Thành viên chạy nhiều dự án trên cùng máy; cổng mặc định (8000 uvicorn, 8080/80 nginx, 5173 Vite, 8888 Jupyter) thường đã bị chiếm.
Lệnh chạy giữa Python, Node, Docker khác nhau, dễ sai thứ tự (ví dụ quên tự cài torch trước requirements).

## Quyết định
- Mọi tiến trình đọc cổng từ **một nguồn**: `.env` (sinh từ `.env.example` bằng `make env`), mặc định
  `UTCI_API_PORT=18100`, `UTCI_WEB_PORT=18080`, `UTCI_DEV_PORT=15173`, `UTCI_JUPYTER_PORT=18888`.
  - Python: `utci_vision.env.Ports.from_env()`; API chạy bằng `python -m utci_vision.api`.
  - Vite: `loadEnv("..", "UTCI_")`, `strictPort: true` (không tự nhảy sang cổng khác).
  - Docker Compose: nội suy `${UTCI_*}`; Nginx: `nginx.conf.template` (envsubst) — listen đúng `UTCI_WEB_PORT`.
- **Makefile chỉ dùng cho DevOps**: môi trường (`env`, `venv`, `install`, `check-env`, `freeze`), CI (`lint`, `format`, `test`, `ci`),
  Docker (`build`, `up`, `up-gpu`, `down`, `logs`, `ps`, `clean`). Dữ liệu, fine-tune, đánh giá, chạy dev gọi trực tiếp `scripts/`, notebook, `npm`.
- JupyterLab: `jupyter lab --config jupyter_server_config.py` (file config đọc `UTCI_JUPYTER_PORT` từ `.env`).
- Không ghi chú cuối dòng trong `.env` (Make/Python đọc nguyên giá trị) — có test kiểm tra.

## Hệ quả
- (+) Không xung đột cổng mặc định; đổi cổng chỉ sửa `.env`.
- (+) Người mới chỉ cần `make env venv install ci`; Makefile ngắn, không lẫn nghiệp vụ.
- (−) Windows cần Git Bash có GNU Make.
