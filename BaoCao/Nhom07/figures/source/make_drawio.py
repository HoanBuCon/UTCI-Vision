"""Sinh các sơ đồ draw.io (.drawio, mở và sửa được bằng draw.io / diagrams.net) cho báo cáo.

Phong cách theo sơ đồ mẫu của nhóm (Fig_aggregation, Fig_data_use): nền trắng, Arial, khối bo góc viền đen mảnh,
khung nhóm xám nhạt có nhãn (a)/(b), ảnh thật có viền màu, chú thích kích thước in nghiêng, mũi tên liền = luồng dữ liệu,
mũi tên đứt = tham số / khâu tuỳ chọn, chú giải một hàng ở cuối. Ảnh nhỏ lấy từ figures/qual (make_qualitative.py).

    .venv/Scripts/python BaoCao/Nhom07/figures/source/make_drawio.py
Ra: figures/drawio/*.drawio. Xuất SVG / PDF: figures/source/render_drawio/ (draw.io chính thức qua chế độ nhúng).
"""
from __future__ import annotations

import base64
import json
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import cv2

FIG = Path(__file__).resolve().parents[1]
QUAL = FIG / "qual"
OUT = FIG / "drawio"
OUT.mkdir(exist_ok=True)
EDA = json.loads((Path(__file__).resolve().parents[4] / "web/public/data/eda.json").read_text(encoding="utf8"))

INK, MUTED, PANEL = "#1a1a1a", "#5a5a5a", "#c8c8c8"
CV_C, DL_C, OPT = "#009E73", "#0072B2", "#7f7f7f"
TRAIN, SELECT, FIT, EVAL = "#0072B2", "#E69F00", "#CC79A7", "#BBBBBB"
FONT = "fontFamily=Arial;"


class Diagram:
    def __init__(self, name: str, w: int, h: int):
        self.name, self.w, self.h, self.cells, self.n = name, w, h, [], 1

    def _id(self) -> str:
        self.n += 1
        return f"c{self.n}"

    def vertex(self, x, y, w, h, value="", style="") -> str:
        i = self._id()
        self.cells.append(
            f'<mxCell id="{i}" value={quoteattr(value)} style={quoteattr(style)} vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
        )
        return i

    def edge(self, src, dst, style="", value="", points=(), exit=None, entry=None) -> str:
        i = self._id()
        st = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;endSize=6;strokeWidth=1.3;" \
             f"strokeColor={INK};{FONT}fontSize=12;fontColor={MUTED};fontStyle=2;labelBackgroundColor=#ffffff;"
        if exit:
            st += f"exitX={exit[0]};exitY={exit[1]};exitDx=0;exitDy=0;"
        if entry:
            st += f"entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;"
        pts = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in points)
        arr = f'<Array as="points">{pts}</Array>' if pts else ""
        self.cells.append(
            f'<mxCell id="{i}" value={quoteattr(value)} style={quoteattr(st + style)} edge="1" parent="1" '
            f'source="{src}" target="{dst}"><mxGeometry relative="1" as="geometry">{arr}</mxGeometry></mxCell>'
        )
        return i

    def line(self, x1, y1, x2, y2, style="") -> str:
        i = self._id()
        st = f"html=1;endArrow=block;endFill=1;endSize=6;strokeWidth=1.3;strokeColor={INK};" + style
        self.cells.append(
            f'<mxCell id="{i}" value="" style={quoteattr(st)} edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
            f'<mxPoint x="{x1}" y="{y1}" as="sourcePoint"/><mxPoint x="{x2}" y="{y2}" as="targetPoint"/></mxGeometry></mxCell>'
        )
        return i

    # ---- khối dựng sẵn
    def text(self, x, y, w, h, value, size=13, bold=False, italic=False, color=INK, align="center", valign="middle"):
        style = (f"text;html=1;whiteSpace=wrap;overflow=visible;strokeColor=none;fillColor=none;{FONT}fontSize={size};"
                 f"fontColor={color};align={align};verticalAlign={valign};spacing=0;fontStyle={int(bold) + 2 * int(italic)};")
        return self.vertex(x, y, w, h, value, style)

    def panel(self, x, y, w, h, title):
        self.vertex(x, y, w, h, "", f"rounded=1;arcSize=2;absoluteArcSize=1;html=1;fillColor=none;strokeColor={PANEL};strokeWidth=1.2;")
        self.text(x + 14, y + 8, w - 28, 22, title, 15, bold=True, align="left")

    def box(self, x, y, w, h, title, sub="", tags=(), dashed=False, fill="#ffffff", title_size=14):
        val = f"<b>{escape(title)}</b>" + (f"<br><font style=\"font-size:12px\" color=\"{MUTED}\">{sub}</font>" if sub else "")
        style = (f"rounded=1;arcSize=10;html=1;whiteSpace=wrap;{FONT}fontSize={title_size};fontColor={INK};fillColor={fill};"
                 f"strokeColor={OPT if dashed else INK};strokeWidth=1.4;spacing=6;"
                 + ("dashed=1;dashPattern=5 3;" if dashed else ""))
        i = self.vertex(x, y, w, h, val, style)
        tx = x + 8
        for t in tags:
            c = CV_C if t == "CV" else DL_C
            tw = 28 if len(t) <= 2 else 40
            self.vertex(tx, y - 9, tw, 17, t,
                        f"rounded=1;arcSize=40;html=1;{FONT}fontSize=11;fontStyle=1;fontColor=#ffffff;fillColor={c};strokeColor=none;")
            tx += tw + 4
        return i

    def image(self, x, y, w, h, path: Path, border="#1a1a1a", px=2.0):
        img = cv2.imread(str(path))
        ih, iw = img.shape[:2]
        # cắt giữa cho đúng tỉ lệ khung rồi thu nhỏ (giữ file nhẹ)
        r = w / h
        if iw / ih > r:
            nw = int(ih * r)
            img = img[:, (iw - nw) // 2:(iw - nw) // 2 + nw]
        else:
            nh = int(iw / r)
            img = img[(ih - nh) // 2:(ih - nh) // 2 + nh]
        img = cv2.resize(img, (int(w * px), int(h * px)), interpolation=cv2.INTER_AREA)
        b64 = base64.b64encode(cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 85])[1]).decode()
        style = (f"shape=image;html=1;imageAspect=0;aspect=fixed;imageBorder={border};strokeWidth=2;"
                 f"image=data:image/jpeg,{b64};")
        return self.vertex(x, y, w, h, "", style)

    def legend(self, x, y, items):
        cx = x
        for kind, label, color in items:
            if kind == "arrow":
                self.line(cx, y + 9, cx + 34, y + 9, f"strokeColor={INK};")
                cx += 40
            elif kind == "dash":
                self.line(cx, y + 9, cx + 34, y + 9, f"dashed=1;strokeColor={OPT};")
                cx += 40
            elif kind == "dashbox":
                self.vertex(cx, y + 1, 30, 16, "", f"rounded=1;html=1;fillColor=#ffffff;strokeColor={OPT};dashed=1;strokeWidth=1.4;")
                cx += 36
            elif kind == "tag":
                self.vertex(cx, y + 1, 28, 17, label.split()[0],
                            f"rounded=1;arcSize=40;html=1;{FONT}fontSize=11;fontStyle=1;fontColor=#ffffff;fillColor={color};strokeColor=none;")
                cx += 34
                label = " ".join(label.split()[1:])
            elif kind == "swatch":
                self.vertex(cx, y + 2, 30, 14, "", f"html=1;fillColor={color};strokeColor={'#9e9e9e' if color == '#ffffff' else 'none'};")
                cx += 36
            w = 7.3 * len(label) + 6
            self.text(cx, y, w, 18, label, 13, align="left")
            cx += w + 22

    def write(self):
        body = "".join(self.cells)
        xml = (f'<mxfile host="UTCI-Vision" agent="figures/source/make_drawio.py"><diagram id="{self.name}" name="{self.name}">'
               f'<mxGraphModel dx="{self.w}" dy="{self.h}" grid="1" gridSize="5" guides="1" tooltips="1" connect="1" arrows="1" '
               f'fold="1" page="1" pageScale="1" pageWidth="{self.w}" pageHeight="{self.h}" background="#ffffff" math="0" shadow="0">'
               f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>{body}</root></mxGraphModel></diagram></mxfile>')
        (OUT / f"{self.name}.drawio").write_text(xml, encoding="utf8", newline="\n")
        print("wrote", self.name, f"{len(xml) / 1024:.0f} KB")


def comma_int(n: int) -> str:
    return f"{n:,}".replace(",", " ")


# ============================================================ 1. pipeline hệ thống chính
def fig_system():
    d = Diagram("Fig_pipeline_he_thong", 930, 560)
    BW, BH = 165, 78
    xs = [180, 400, 620]
    y1, y2 = 160, 360

    # đầu vào
    d.text(0, 70, 150, 20, "Đầu vào", 14, bold=True)
    d.image(15, 96, 120, 68, QUAL / "cv_input.jpg", border=INK)
    d.image(15, 172, 120, 68, QUAL / "toi_goc.jpg", border=INK)
    d.text(0, 246, 150, 18, "ảnh · video · webcam", 12, italic=True, color=MUTED)
    d.line(135, 130, xs[0], y1 + BH / 2)
    d.line(135, 206, xs[0], y1 + BH / 2)

    q = d.box(xs[0], y1, BW, BH, "Đánh giá chất lượng", "độ sáng V · tương phản L<br>phương sai Laplacian", ("CV",))
    e = d.box(xs[1], y1, BW, BH, "Tăng cường thích nghi", "gamma · CLAHE kênh L<br>lọc song phương", ("CV",))
    y = d.box(xs[2], y1, BW, BH, "YOLO11s", "phát hiện + phân loại<br>27 lớp · suy luận 1280 px", ("DL",))
    d.edge(q, e)
    d.edge(e, y)
    d.text(xs[0] + BW, y1 + BH / 2 - 22, xs[1] - xs[0] - BW, 16, "khi cần", 11, italic=True, color=MUTED)
    d.text(xs[0], 118, BW, 30, "chọn phép tăng cường<br>theo ngưỡng cấu hình", 11, italic=True, color=MUTED)
    d.image(xs[1], 64, 80, 45, QUAL / "toi_goc.jpg", border=MUTED)
    d.image(xs[1] + 85, 64, 80, 45, QUAL / "toi_tang_cuong.jpg", border=CV_C)
    d.text(xs[1], 112, 80, 16, "trước", 11, italic=True, color=MUTED)
    d.text(xs[1] + 85, 112, 80, 16, "sau (γ 3,5)", 11, italic=True, color=MUTED)
    d.image(xs[2] + 2, 56, 160, 80, QUAL / "da_dang2_yolo.jpg", border=DL_C)
    d.text(xs[1] - 10, y1 + BH + 6, BW + 20, 16, "ảnh tốt giữ nguyên (≈ 97% ảnh test)", 11, italic=True, color=MUTED)
    d.line(xs[2] + BW, y1 + BH / 2, 815, y1 + BH / 2, f"dashed=1;strokeColor={OPT};endArrow=none;")
    d.text(815, y1 + BH / 2 - 20, 115, 40, "API FastAPI<br>Web React · Docker", 11, italic=True, color=MUTED, align="left")

    # hàng 2
    v = d.box(xs[0], y2, BW, BH, "Bộ xác minh", "HSV · hình dạng · Hu · HOG<br>→ LightGBM · tắt mặc định",
              ("CV", "DL"), dashed=True)
    t = d.box(xs[1], y2, BW, BH, "Theo vết", "Kalman + Hungarian (IoU)<br>bỏ phiếu nhãn · chỉ video", ("CV",))
    o = d.box(xs[2], y2, BW, BH, "Đọc số / chữ", "cắt vùng chữ → VietOCR<br>regex + từ điển", ("CV", "DL"))
    r = d.box(815, y2 + 6, 110, 66, "Kết quả", "khung · lớp<br>giá trị · QCVN", fill="#f5f5f5")
    d.edge(y, v, points=[(xs[2] + BW / 2, 295), (xs[0] + BW / 2, 295)], exit=(0.5, 1), entry=(0.5, 0))
    d.edge(v, t)
    d.edge(t, o)
    d.edge(o, r)
    d.image(xs[2] + 10, y2 + BH + 14, 62, 62, QUAL / "ocr_value_region_0.jpg", border=CV_C)
    d.text(xs[2] + 80, y2 + BH + 24, 110, 40, "giá trị đọc được:<br><b>40 km/h</b>", 12, align="left")
    d.image(815, y2 + BH + 14, 110, 62, QUAL / "ocr_result.jpg", border=INK)
    d.text(xs[0], y2 + BH + 8, BW, 30, "bật lại khi cần<br>ít báo nhầm (E2)", 11, italic=True, color=MUTED)
    d.text(xs[1], y2 + BH + 8, BW, 30, "ảnh tĩnh: bỏ qua; video:<br>tác vụ nền theo từng vết", 11, italic=True, color=MUTED)

    d.legend(20, 540, [("tag", "CV xử lý ảnh / đặc trưng thủ công", CV_C), ("tag", "DL học sâu", DL_C),
                       ("arrow", "luồng dữ liệu", None), ("dashbox", "khâu tuỳ chọn", None)])
    d.write()


# ============================================================ 2. pipeline CV truyền thống (đối chứng)
def fig_cv():
    d = Diagram("Fig_pipeline_cv", 1000, 330)
    BW, BH, Y = 160, 78, 160
    xs = [150, 340, 530, 720]
    d.text(0, 136, 130, 20, "Ảnh vào", 14, bold=True)
    d.image(10, 168, 115, 64, QUAL / "cv_input.jpg", border=INK)
    d.text(0, 236, 135, 30, "sau khâu tăng cường<br>dùng chung", 11, italic=True, color=MUTED)
    a = d.box(xs[0], Y, BW, BH, "Phân đoạn màu", "HSV: đỏ · xanh · vàng<br>mở + đóng hình thái học", ("CV",))
    b = d.box(xs[1], Y, BW, BH, "Ứng viên", "contour · độ tròn bao lồi<br>số đỉnh · solidity · NMS", ("CV",))
    c = d.box(xs[2], Y, BW, BH, "Đặc trưng thủ công", "crop nới 10% → 32×32<br>HOG 324 + HSV 64 chiều", ("CV",))
    s = d.box(xs[3], Y, BW, BH, "SVM nhân RBF", "vector 388 chiều<br>27 lớp biển + 1 lớp nền", ("CV",))
    d.line(125, Y + BH / 2, xs[0], Y + BH / 2)
    d.edge(a, b)
    d.edge(b, c)
    d.edge(c, s)
    d.image(xs[0] + 15, 58, 130, 72, QUAL / "cv_masks.jpg", border=CV_C)
    d.image(xs[1] + 15, 58, 130, 72, QUAL / "cv_candidates.jpg", border=CV_C)
    d.text(xs[1], 132, BW, 16, "15 ứng viên", 11, italic=True, color=MUTED)
    d.image(xs[2] + 8, 74, 46, 46, QUAL / "cv_crop1.jpg", border=MUTED)
    d.image(xs[2] + 57, 74, 46, 46, QUAL / "cv_hog1.jpg", border=CV_C)
    d.image(xs[2] + 106, 74, 46, 46, QUAL / "cv_sift1.jpg", border=OPT)
    d.text(xs[2], 124, BW, 16, "crop · HOG · SIFT", 11, italic=True, color=MUTED)
    d.text(905, 136, 95, 20, "Kết quả", 14, bold=True)
    d.image(910, 168, 88, 50, QUAL / "cv_result.jpg", border=INK)
    d.text(905, 222, 95, 32, "3 biển: lớp<br>+ độ tin cậy", 11, italic=True, color=MUTED)
    d.line(xs[3] + BW, Y + BH / 2, 910, Y + BH / 2)
    sf = d.box(xs[2], 268, BW, 50, "SIFT + BoVW", "từ điển 256 · đối chứng (E8)", dashed=True, title_size=13)
    d.edge(sf, s, style=f"dashed=1;strokeColor={OPT};", exit=(1, 0.5), entry=(0.5, 1))
    d.text(xs[0], 272, 330, 40, "huấn luyện SVM: 15 449 mẫu train (6 000 nền)<br>chọn C = 10 trên val", 12, italic=True,
           color=MUTED, align="left")
    d.write()


# ============================================================ 3. dữ liệu: chuẩn bị + sử dụng
def fig_data():
    t, s = EDA["totals"], EDA["splits"]
    d = Diagram("Fig_du_lieu", 900, 470)
    # (a) chuẩn bị
    d.panel(0, 0, 900, 150, "(a) Chuẩn bị dữ liệu processed/v1")
    BW, BH, Y = 150, 72, 50
    steps = [
        ("Roboflow (CC BY 4.0)", "5 453 ảnh · 13 478 biển<br>32 lớp"),
        ("Kiểm tra", f"loại 12 ảnh lỗi<br>+ 55 ảnh thiếu nhãn"),
        ("Ảnh gần trùng", f"pHash 8×8, Hamming ≤ 6<br>{comma_int(t['clusters'])} cụm cảnh"),
        ("Gộp lớp hiếm", "6 lớp &lt; 60 cụm cảnh<br>→ 27 lớp (ADR-009)"),
        ("Chia theo cụm", "70 / 15 / 15 · phân tầng<br>theo lớp + độ phân giải"),
    ]
    ids = []
    for k, (a, b) in enumerate(steps):
        ids.append(d.box(16 + k * 177, Y, BW, BH, a, b, title_size=13))
    for a, b in zip(ids, ids[1:]):
        d.edge(a, b)

    # (b) sử dụng
    d.panel(0, 165, 900, 270, "(b) Vai trò của từng tập trong huấn luyện, lựa chọn và đánh giá")
    X0, GAP, W = 220, 10, 660
    tot = sum(v["images"] for v in s.values())
    widths = {k: max(W * v["images"] / tot, 92) for k, v in s.items()}
    scale = (W - 2 * GAP - widths["val"] - widths["test"])
    widths["train"] = scale
    xs = {"train": X0, "val": X0 + widths["train"] + GAP, "test": X0 + widths["train"] + widths["val"] + 2 * GAP}
    for k, lab in [("train", "Train"), ("val", "Val"), ("test", "Test")]:
        d.text(xs[k] + widths[k] / 2 - 80, 198, 160, 34,
               f"<b>{lab}</b><br>{comma_int(s[k]['images'])} ảnh · {comma_int(s[k]['boxes'])} biển", 12)
    rows = [
        ("YOLO11s", [TRAIN, SELECT, EVAL], "chọn epoch"),
        ("HOG / SIFT + SVM", [TRAIN, SELECT, EVAL], "chọn C"),
        ("Bộ xác minh LightGBM", ["#ffffff", FIT, EVAL], "fit trên ứng viên YOLO"),
    ]
    for r, (name, cols, note) in enumerate(rows):
        yy = 245 + r * 44
        d.text(16, yy, 195, 30, name, 13, bold=True, align="right")
        for k, c in zip(("train", "val", "test"), cols):
            st = f"html=1;fillColor={c};strokeColor={'#9e9e9e' if c == '#ffffff' else '#ffffff'};"
            d.vertex(xs[k], yy, widths[k], 30, "", st)
        d.text(xs["val"], yy, widths["val"], 30, note, 10.5, color="#ffffff" if cols[1] != "#ffffff" else INK, bold=True)
    d.text(xs["test"] - 30, 380, widths["test"] + 40, 36, "+ bản làm tối / nhiễu / mờ<br>(T4, E4)", 11, italic=True,
           color=MUTED)
    d.text(xs["train"], 380, widths["train"], 36, "không ảnh nào của cùng một cụm cảnh nằm ở hai tập", 11, italic=True,
           color=MUTED)
    d.legend(20, 445, [("swatch", "Huấn luyện", TRAIN), ("swatch", "Chọn mô hình / siêu tham số", SELECT),
                       ("swatch", "Fit bộ xác minh", FIT), ("swatch", "Đánh giá cuối", EVAL),
                       ("swatch", "Không dùng", "#ffffff")])
    d.write()


if __name__ == "__main__":
    fig_system()
    fig_cv()
    fig_data()
