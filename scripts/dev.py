"""Chạy API và Vite trong cùng terminal; Ctrl+C dừng các tiến trình do lệnh này tạo."""

from __future__ import annotations

import argparse
import os
import shutil
import socket
import subprocess
import sys
import time

from utci_vision.env import ROOT, Ports


def listening(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def stop(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        # Chỉ dừng cây tiến trình do launcher này tạo, không dừng theo tên hoặc theo cổng.
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        os.killpg(process.pid, 15)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if os.name != "nt":
            os.killpg(process.pid, 9)
        else:
            process.kill()
        process.wait()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    ports = Ports.from_env()
    endpoints = {"API": (os.environ.get("UTCI_API_HOST", "127.0.0.1"), ports.api), "Web": ("localhost", ports.dev)}
    busy = []
    for name, (host, port) in endpoints.items():
        # Địa chỉ bind wildcard không phải địa chỉ đích để kiểm tra kết nối.
        check_host = "127.0.0.1" if host == "0.0.0.0" else "::1" if host == "::" else host
        active = listening(check_host, port)
        if active:
            busy.append(name)
        print(f"{name}: http://{host}:{port} — {'cổng đang mở' if active else 'cổng chưa mở'}", flush=True)
    if args.status:
        return 0
    if busy:
        print("Cổng đang được sử dụng. Dừng phiên cũ trước khi chạy make dev; không tự dừng tiến trình có sẵn.")
        return 1
    node = shutil.which("node")
    vite = ROOT / "web/node_modules/vite/bin/vite.js"
    if not node or not vite.is_file():
        print("Cần Node.js và thư viện web: npm.cmd --prefix web ci (Windows), npm --prefix web ci (Linux/macOS).")
        return 1
    children: list[subprocess.Popen] = []
    options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    try:
        children.append(subprocess.Popen([sys.executable, "-m", "utci_vision.api"], cwd=ROOT, **options))
        children.append(subprocess.Popen([node, str(vite)], cwd=ROOT / "web", **options))
        print(f"Mở http://localhost:{ports.dev} sau khi API nạp xong mô hình. Ctrl+C để dừng.", flush=True)
        while all(child.poll() is None for child in children):
            time.sleep(0.3)
        print("Một dịch vụ đã thoát; dừng dịch vụ còn lại.")
        return 1
    except KeyboardInterrupt:
        print("\nĐang dừng API và web...")
        return 0
    finally:
        for child in reversed(children):
            stop(child)


if __name__ == "__main__":
    raise SystemExit(main())
