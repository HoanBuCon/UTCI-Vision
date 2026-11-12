"""Chụp ảnh giao diện web cho mục demo của báo cáo (Edge headless + Chrome DevTools Protocol).

Cần API (18100) và web dev (15173) đang chạy: `.venv/Scripts/python -m utci_vision.api` và `npm --prefix web run dev`.
    .venv/Scripts/python BaoCao/Nhom07/figures/source/screenshot_web.py
Ra: figures/web_*.png
"""
from __future__ import annotations

import asyncio
import base64
import json
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import websockets

FIG = Path(__file__).resolve().parents[1]
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
BASE = "http://localhost:15173"
PORT = 9333

CLICK_SAMPLE = "[...document.querySelectorAll('button.sample')].find(b => b.title.startsWith({t!r})).click()"
CLICK_RUN = "document.querySelector('button.btn-primary') && document.querySelector('button.btn-primary').click()"

# (tên tệp, đường dẫn, chiều cao khung nhìn, các bước JS, thời gian chờ mỗi bước)
SHOTS = [
    ("web_eda", "/data", 1500, [], 4),
    ("web_pipeline", "/pipeline", 1900, [CLICK_SAMPLE.format(t="Biển có số 1")], 12),
    ("web_dl", "/demo/dl", 1250, [CLICK_SAMPLE.format(t="Nhiều biển nhỏ 1"), CLICK_RUN], 12),
    ("web_cv", "/demo/traditional", 1700, [CLICK_SAMPLE.format(t="Nhiều loại biển 2"), CLICK_RUN], 12),
    ("web_compare", "/compare", 1500, [CLICK_SAMPLE.format(t="Nhiều biển 1"), CLICK_RUN], 15),
    ("web_results", "/results", 1500, [], 4),
]


async def main() -> None:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as prof:
        proc = subprocess.Popen([EDGE, "--headless=new", f"--remote-debugging-port={PORT}", f"--user-data-dir={prof}",
                                 "--force-device-scale-factor=1", "--hide-scrollbars", "about:blank"])
        try:
            for _ in range(50):
                try:
                    urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1)
                    break
                except OSError:
                    time.sleep(0.2)
            req = urllib.request.Request(f"http://127.0.0.1:{PORT}/json/new?about:blank", method="PUT")
            ws_url = json.loads(urllib.request.urlopen(req).read())["webSocketDebuggerUrl"]
            async with websockets.connect(ws_url, max_size=2**28) as ws:
                n = 0

                async def cmd(method: str, **params):
                    nonlocal n
                    n += 1
                    await ws.send(json.dumps({"id": n, "method": method, "params": params}))
                    while True:
                        msg = json.loads(await ws.recv())
                        if msg.get("id") == n:
                            return msg.get("result", {})

                await cmd("Page.enable")
                await cmd("Runtime.enable")
                await cmd("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "light"}])
                for name, path, height, steps, wait in SHOTS:
                    await cmd("Emulation.setDeviceMetricsOverride", width=1440, height=height, deviceScaleFactor=1, mobile=False)
                    await cmd("Page.navigate", url=BASE + path)
                    await asyncio.sleep(4)
                    for js in steps:
                        r = await cmd("Runtime.evaluate", expression=js, awaitPromise=True)
                        if "exceptionDetails" in r:
                            print("  JS lỗi:", name, r["exceptionDetails"].get("text"))
                        await asyncio.sleep(wait if js is steps[-1] else 1.5)
                    await cmd("Runtime.evaluate", expression="window.scrollTo(0,0)")
                    await asyncio.sleep(1)
                    shot = await cmd("Page.captureScreenshot", format="png")
                    (FIG / f"{name}.png").write_bytes(base64.b64decode(shot["data"]))  # báo cáo dùng bản .jpg (chuyển sau)
                    print("wrote", name)
        finally:
            proc.terminate()
            proc.wait(10)


asyncio.run(main())
