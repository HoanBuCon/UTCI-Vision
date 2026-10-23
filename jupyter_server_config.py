"""Cổng JupyterLab lấy từ .env (UTCI_JUPYTER_PORT, mặc định 18888 — không dùng 8888).
Jupyter tự nạp file này khi chạy `jupyter lab` từ thư mục gốc dự án (ADR-007)."""

import os
from pathlib import Path

for line in (Path(__file__).parent / ".env").read_text(encoding="utf-8").splitlines() if (
    Path(__file__).parent / ".env"
).exists() else []:
    key, sep, value = line.partition("=")
    if sep and not key.strip().startswith("#"):
        os.environ.setdefault(key.strip(), value.strip())

c = get_config()  # noqa: F821 — biến do Jupyter cung cấp
c.ServerApp.port = int(os.environ.get("UTCI_JUPYTER_PORT", "18888"))
c.ServerApp.port_retries = 0  # cổng bận thì báo lỗi, không tự nhảy về cổng khác
