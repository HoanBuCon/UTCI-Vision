"""Chuyển figures/drawio/*.svg (xuất từ draw.io) -> figures/<tên>.pdf vector, đúng khổ hình, bằng Edge/Chrome headless.

    python BaoCao/Nhom07/figures/source/render_drawio/svg_to_pdf.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

FIG = Path(__file__).resolve().parents[2]
DRAWIO = FIG / "drawio"
BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]
exe = next((b for b in BROWSERS if Path(b).exists()), shutil.which("msedge") or shutil.which("chrome"))

for svg in sorted(DRAWIO.glob("*.svg")):
    text = svg.read_text(encoding="utf8")
    m = re.search(r'<svg[^>]*?width="([\d.]+)px"[^>]*?height="([\d.]+)px"', text) or re.search(
        r'<svg[^>]*?viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', text)
    w, h = float(m.group(1)), float(m.group(2))
    html = (f"<!doctype html><html><head><meta charset='utf-8'><style>@page{{size:{w}px {h}px;margin:0}}"
            f"html,body{{margin:0;padding:0;background:#fff}}svg{{display:block}}</style></head><body>"
            f"{text[text.index('<svg'):]}</body></html>")
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "page.html"
        page.write_text(html, encoding="utf8")
        out = FIG / f"{svg.stem}.pdf"
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
                        "--virtual-time-budget=3000", f"--print-to-pdf={out}", page.as_uri()],
                       check=True, capture_output=True, timeout=120)
    print("wrote", out.name, f"{w:.0f}x{h:.0f}px")
