"""Xuất .drawio -> .svg bằng chính draw.io (embed.diagrams.net, chế độ nhúng proto=json), không cần cài draw.io.

    python BaoCao/Nhom07/figures/source/render_drawio/server.py   # rồi mở http://127.0.0.1:18765 trên trình duyệt
Trang index.html lần lượt nạp từng sơ đồ vào iframe draw.io, gọi export SVG và POST kết quả về server này;
server ghi figures/drawio/<tên>.svg rồi in "done" khi xong. Chuyển SVG -> PDF: svg_to_pdf.py (Edge headless).
"""
from __future__ import annotations

import base64
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
DRAWIO = HERE.parents[1] / "drawio"
PORT = 18765


class H(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str = "text/plain; charset=utf-8") -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            return self._send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        if self.path == "/list":
            names = sorted(p.stem for p in DRAWIO.glob("*.drawio"))
            return self._send(200, json.dumps(names).encode(), "application/json")
        if self.path.startswith("/xml/"):
            p = DRAWIO / f"{Path(self.path[5:]).name}.drawio"
            return self._send(200, p.read_bytes(), "application/xml") if p.exists() else self._send(404, b"")
        self._send(404, b"")

    def do_POST(self) -> None:  # noqa: N802
        if not self.path.startswith("/save/"):
            return self._send(404, b"")
        name = Path(self.path[6:]).name
        data = self.rfile.read(int(self.headers["Content-Length"])).decode()
        if data.startswith("data:"):
            head, payload = data.split(",", 1)
            svg = base64.b64decode(payload) if ";base64" in head else payload.encode()
        else:
            svg = data.encode()
        (DRAWIO / f"{name}.svg").write_bytes(svg)
        print("saved", name, len(svg), flush=True)
        self._send(200, b"ok")

    def log_message(self, *a) -> None:  # bớt log
        pass


if __name__ == "__main__":
    print(f"http://127.0.0.1:{PORT}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
