"""Sinh biểu đồ cho báo cáo (Chương 2-3) từ số liệu tổng hợp của dự án.

Nguồn: web/public/data/{eda,results}.json (sinh bằng scripts/export_web_data.py từ registry + CSV đánh giá).
Không chép tay con số nào. Chạy từ gốc repo:
    .venv/Scripts/python BaoCao/Nhom07/figures/source/make_charts.py
Ra: BaoCao/Nhom07/figures/ch*_*.pdf (vector).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter, PercentFormatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1]
EDA = json.loads((ROOT / "web/public/data/eda.json").read_text(encoding="utf8"))
RES = json.loads((ROOT / "web/public/data/results.json").read_text(encoding="utf8"))

# Bảng màu Okabe-Ito (an toàn với người mù màu), thứ tự cố định — cùng bảng màu với sơ đồ draw.io.
BLUE, ORANGE, GREEN, VERM, PURPLE, SKY, YELLOW = "#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442"
GRAY, INK, MUTED, GRID = "#9E9E9E", "#1A1A1A", "#555555", "#E6E6E6"

plt.rcParams.update({
    "font.family": "Arial", "font.size": 9, "axes.titlesize": 9.5, "axes.titleweight": "bold",
    "axes.labelsize": 9, "axes.edgecolor": "#BDBDBD", "axes.linewidth": 0.8, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "axes.axisbelow": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "legend.frameon": False, "legend.fontsize": 8.5,
    "pdf.fonttype": 42, "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
})
vn = FuncFormatter(lambda v, _: f"{v:.2f}".replace(".", ","))
vn1 = FuncFormatter(lambda v, _: f"{v:.1f}".replace(".", ","))


def comma(v: float, d: int = 3) -> str:
    return f"{v:.{d}f}".replace(".", ",")


def save(fig, name: str) -> None:
    fig.savefig(OUT / f"{name}.pdf")
    plt.close(fig)
    print("wrote", name)


def grouped(ax, groups, series, colors, width=0.8, labels=True, fmt=lambda v: comma(v, 2), fs=6.8):
    n = len(series)
    w = width / n
    for i, (name, vals) in enumerate(series.items()):
        xs = [g + (i - (n - 1) / 2) * w for g in range(len(groups))]
        bars = ax.bar(xs, vals, w * 0.92, color=colors[i], label=name, zorder=2)
        if labels:
            for b, v in zip(bars, vals):
                ax.text(b.get_x() + b.get_width() / 2, v + 0.006, fmt(v), ha="center", va="bottom", fontsize=fs, color=INK)
    ax.set_xticks(range(len(groups)), groups)
    ax.grid(axis="x", visible=False)


# ---------------------------------------------------------------- Chương 2: dữ liệu
def eda_classes() -> None:
    rows = sorted(EDA["per_class"], key=lambda r: r["total"])
    sup_color = {"prohibitory": VERM, "warning": ORANGE, "mandatory": BLUE, "info": GREEN, "other": GRAY}
    sup_name = {s["key"]: s["name"] for s in EDA["superclasses"]}
    fig, ax = plt.subplots(figsize=(6.3, 6.4))
    ys = range(len(rows))
    ax.barh(ys, [r["total"] for r in rows], 0.72, color=[sup_color[r["superclass"]] for r in rows], zorder=2)
    for y, r in zip(ys, rows):
        ax.text(r["total"] + 18, y, f"{r['total']:,}".replace(",", ".") + f"  ({comma(r['median_px'], 0)} px)",
                va="center", fontsize=7, color=MUTED)
    ax.set_yticks(list(ys), [r["name"] for r in rows], fontsize=7.6)
    ax.set_xlabel("Số biển (train + val + test); trong ngoặc: cạnh trung vị")
    ax.set_xlim(0, max(r["total"] for r in rows) * 1.22)
    ax.grid(axis="y", visible=False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in sup_color.values()]
    ax.legend(handles, [sup_name[k] for k in sup_color], loc="lower right", ncol=1)
    save(fig, "ch2_eda_lop")


def eda_size() -> None:
    fig, axs = plt.subplots(1, 3, figsize=(6.6, 2.3), gridspec_kw={"width_ratios": [1.7, 1, 1]})
    h = EDA["size_hist"]
    small = {"<8", "8–16"}
    axs[0].bar(range(len(h)), [b["boxes"] for b in h], 0.8,
               color=[VERM if b["bin"] in small else (ORANGE if b["bin"] in {"16–24", "24–32"} else BLUE) for b in h], zorder=2)
    axs[0].set_xticks(range(len(h)), [b["bin"] for b in h], rotation=45, ha="right")
    axs[0].set_title("(a) Kích thước biển √(w·h) (px)")
    axs[0].set_ylabel("Số biển")
    axs[0].grid(axis="x", visible=False)
    t = EDA["totals"]
    axs[0].text(0.98, 0.95, f"< 16 px: {comma(t['pct_lt16'], 1)}%\n< 32 px: {comma(t['pct_lt32'], 1)}%",
                transform=axs[0].transAxes, ha="right", va="top", fontsize=7.5, color=INK)

    r = EDA["resolutions"]
    axs[1].bar(range(len(r)), [x["images"] for x in r], 0.7, color=SKY, zorder=2)
    axs[1].set_xticks(range(len(r)), [x["res"].replace("x", "×") for x in r], rotation=45, ha="right")
    axs[1].set_title("(b) Độ phân giải ảnh")
    axs[1].set_ylabel("Số ảnh")
    axs[1].grid(axis="x", visible=False)

    s = EDA["signs_per_image"]
    axs[2].bar([x["n"] for x in s], [x["images"] for x in s], 0.75, color=GREEN, zorder=2)
    axs[2].set_xticks([0, 2, 4, 6, 8, 10], ["0", "2", "4", "6", "8", "≥10"])
    axs[2].set_title("(c) Số biển trên ảnh")
    axs[2].set_ylabel("Số ảnh")
    axs[2].grid(axis="x", visible=False)
    fig.tight_layout(w_pad=1.2)
    save(fig, "ch2_eda_kich_thuoc")


# ---------------------------------------------------------------- Chương 3: kết quả
def training() -> None:
    tr = RES["training"]
    ep = [r["epoch"] for r in tr]
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.4))
    axs[0].plot(ep, [r["train_box"] for r in tr], color=BLUE, lw=1.6, label="box (train)")
    axs[0].plot(ep, [r["val_box"] for r in tr], color=BLUE, lw=1.6, ls="--", label="box (val)")
    axs[0].plot(ep, [r["train_cls"] for r in tr], color=ORANGE, lw=1.6, label="cls (train)")
    axs[0].plot(ep, [r["val_cls"] for r in tr], color=ORANGE, lw=1.6, ls="--", label="cls (val)")
    axs[0].axvline(66, color=GRAY, lw=0.8, ls=":")
    axs[0].text(65, axs[0].get_ylim()[1] * 0.97, "tắt mosaic", ha="right", va="top", fontsize=7, color=MUTED)
    axs[0].set_title("(a) Hàm mất mát")
    axs[0].set_xlabel("Epoch")
    axs[0].yaxis.set_major_formatter(vn1)
    axs[0].legend(ncol=2, fontsize=7.2, loc="upper right", bbox_to_anchor=(1, 0.9))
    axs[1].plot(ep, [r["map50"] for r in tr], color=GREEN, lw=1.6, label="mAP@50")
    axs[1].plot(ep, [r["map50_95"] for r in tr], color=PURPLE, lw=1.6, label="mAP@50:95")
    axs[1].plot(ep, [r["precision"] for r in tr], color=BLUE, lw=1.0, alpha=0.7, label="Precision")
    axs[1].plot(ep, [r["recall"] for r in tr], color=ORANGE, lw=1.0, alpha=0.7, label="Recall")
    axs[1].set_title("(b) Chỉ số trên tập val")
    axs[1].set_xlabel("Epoch")
    axs[1].set_ylim(0.25, 1.0)
    axs[1].yaxis.set_major_formatter(vn)
    axs[1].legend(ncol=2, fontsize=7.2, loc="lower right")
    fig.tight_layout(w_pad=1.5)
    save(fig, "ch3_huan_luyen")


def size_recall() -> None:
    rows = RES["t3"]
    groups = ["< 16 px", "16–32 px", "32–64 px", "≥ 64 px", "Tất cả"]
    keys = ["recall_<16px", "recall_16-32", "recall_32-64", "recall_>=64", "recall"]
    names = {"imgsz 960": "Suy luận 960 (như khi huấn luyện)", "imgsz 1280": "Suy luận 1280 (mặc định)",
             "960 + cắt ô 640": "960 + cắt ô 640 (kiểu SAHI)"}
    series = {names[r["cau_hinh"]]: [r[k] for k in keys] for r in rows}
    fig, ax = plt.subplots(figsize=(6.4, 2.5))
    grouped(ax, groups, series, [GRAY, BLUE, ORANGE])
    ax.set_ylim(0.55, 1.04)
    ax.set_ylabel("Recall (conf 0,25)")
    ax.yaxis.set_major_formatter(vn)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.2))
    save(fig, "ch3_t3_kich_thuoc")


def t4() -> None:
    cond = {"goc": "Ảnh gốc", "toi_gamma2.5": "Tối (γ 2,5)", "rat_toi_gamma3.5": "Rất tối (γ 3,5)",
            "nhieu_sigma15": "Nhiễu (σ 15)", "mo_chuyen_dong": "Mờ chuyển động"}
    modes = ["không xử lý", "tăng cường thích nghi", "luôn gamma + CLAHE"]
    labels = {"không xử lý": "Không xử lý", "tăng cường thích nghi": "Tăng cường thích nghi (đề xuất)",
              "luôn gamma + CLAHE": "Luôn gamma + CLAHE (đối chứng)"}
    data = {m: [next(r["R"] for r in RES["t4"] if r["dieu_kien"] == c and r["che_do"] == m) for c in cond] for m in modes}
    fig, ax = plt.subplots(figsize=(6.4, 2.5))
    grouped(ax, list(cond.values()), {labels[m]: v for m, v in data.items()}, [GRAY, BLUE, ORANGE])
    ax.set_ylim(0.6, 0.96)
    ax.set_ylabel("Recall (YOLO 960, conf 0,25)")
    ax.yaxis.set_major_formatter(vn)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.2))
    save(fig, "ch3_t4_tang_cuong")


def e8() -> None:
    methods = ["SIFT-BoVW + SVM", "HOG + SVM", "HOG + màu + SVM", "YOLO11 (học sâu)"]
    sizes = ["<16px", "16-32", "32-64", ">=64", "tất cả"]
    groups = ["< 16 px", "16–32 px", "32–64 px", "≥ 64 px", "Tất cả"]
    series = {m: [next(r["accuracy"] for r in RES["e8"] if r["phuong_phap"] == m and r["kich_thuoc"] == s) for s in sizes]
              for m in methods}
    series = {("YOLO11s (học sâu)" if k.startswith("YOLO") else k): v for k, v in series.items()}
    fig, ax = plt.subplots(figsize=(6.6, 2.6))
    grouped(ax, groups, series, [GRAY, SKY, GREEN, BLUE], fs=6.2)
    ax.set_ylim(0.45, 1.06)
    ax.set_ylabel("Accuracy phân loại")
    ax.yaxis.set_major_formatter(vn)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.2))
    save(fig, "ch3_e8_phan_loai")


def e8_paired() -> None:
    rows = RES["e8_paired"]
    order = ["<16px", "16-32", "32-64", ">=64", "tất cả"]
    lab = {"<16px": "< 16 px", "16-32": "16–32 px", "32-64": "32–64 px", ">=64": "≥ 64 px", "tất cả": "Tất cả"}
    rows = sorted(rows, key=lambda r: order.index(r["kich_thuoc"]))
    fig, ax = plt.subplots(figsize=(4.6, 2.0))
    ys = list(range(len(rows)))[::-1]
    for y, r in zip(ys, rows):
        sig = r["ci95_low"] > 0 or r["ci95_high"] < 0
        c = VERM if sig else GRAY
        ax.plot([r["ci95_low"] * 100, r["ci95_high"] * 100], [y, y], color=c, lw=2, solid_capstyle="round")
        ax.plot(r["delta_acc"] * 100, y, "o", color=c, ms=6, mec="white", mew=1.2, zorder=3)
        ax.text(8.2, y, f"{r['delta_acc'] * 100:+.1f}".replace(".", ",").replace("-", "−") + f"  (n = {r['n']})",
                va="center", fontsize=7.3, color=INK)
    ax.axvline(0, color=INK, lw=0.8)
    ax.set_yticks(ys, [lab[r["kich_thuoc"]] for r in rows])
    ax.set_xlabel("Δ accuracy (điểm %): HOG + màu + SVM − YOLO11s, CI 95%")
    ax.set_xlim(-16, 16)
    ax.grid(axis="y", visible=False)
    save(fig, "ch3_e8_ghep_cap")


def per_class() -> None:
    rows = sorted(RES["per_class"], key=lambda r: r["recall"])
    fig, ax = plt.subplots(figsize=(6.3, 6.0))
    ys = range(len(rows))
    for y, r in zip(ys, rows):
        lo, hi = (float(x) for x in r["recall_ci95"].split("-"))
        ax.plot([lo, hi], [y, y], color=SKY, lw=2.2, solid_capstyle="round", zorder=2)
        ax.plot(r["recall"], y, "o", color=BLUE, ms=5, mec="white", mew=1, zorder=3)
        ax.plot(r["recall_ge16px"], y, "D", color=ORANGE, ms=3.6, zorder=3)
        ax.text(1.005, y, f"n = {r['n']}", va="center", fontsize=6.8, color=MUTED, transform=ax.get_yaxis_transform())
    ax.set_yticks(list(ys), [r["ten"] for r in rows], fontsize=7.6)
    ax.set_xlim(0.3, 1.02)
    ax.xaxis.set_major_formatter(vn1)
    ax.set_xlabel("Recall tại conf 0,25 (val + test)")
    ax.grid(axis="y", visible=False)
    h = [plt.Line2D([], [], color=BLUE, marker="o", ls="", ms=5), plt.Line2D([], [], color=SKY, lw=2.2),
         plt.Line2D([], [], color=ORANGE, marker="D", ls="", ms=3.6)]
    ax.legend(h, ["Recall", "CI 95% (Wilson)", "Recall biển ≥ 16 px"], loc="upper left")
    save(fig, "ch3_theo_lop")


def similarity() -> None:
    rows = RES["similarity"]
    lab = ["Giống train\n(pHash ≤ 10)", "Trung bình\n(11–14)", "Khác train\n(≥ 15)"]
    series = {"Recall": [r["recall"] for r in rows], "Recall (biển ≥ 16 px)": [r["recall_ge16px"] for r in rows],
              "Precision": [r["precision"] for r in rows]}
    fig, ax = plt.subplots(figsize=(4.8, 2.4))
    grouped(ax, lab, series, [BLUE, SKY, ORANGE])
    ax.set_ylim(0.6, 1.04)
    ax.yaxis.set_major_formatter(vn)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.2), fontsize=7.8)
    save(fig, "ch3_tuong_dong")


if __name__ == "__main__":
    eda_classes()
    eda_size()
    training()
    size_recall()
    t4()
    e8()
    e8_paired()
    per_class()
    similarity()
