#!/usr/bin/env python3
"""
EDA & làm sạch dữ liệu biển báo giao thông (TV5 - Sprint 1, FR-DATA-01..03)

Cách dùng (PowerShell, chạy từ thư mục gốc repo):
  python eda_data.py --data "D:\\dataset_traffic_sigh\\merge_Real-time Viet Nam Traffic Dtctn 2.v1i.yolov11" all
  python eda_data.py --data "..." excluded      # sau khi đã điền 2 file review_*.csv

Lệnh con:
  eda       Biểu đồ phân bố lớp / kích thước bbox / độ phân giải + summary.md
  dedup     Tìm cụm ảnh gần trùng (dHash), ưu tiên cụm nằm ở nhiều tập (rò rỉ train↔test)
  review    Lưới ảnh 118 ảnh không bbox + review_unlabeled.csv để điền quyết định
  sheets    Contact-sheet crop biển báo theo từng lớp
  excluded  Đọc các file review_*.csv đã điền -> ghi excluded.txt
  all       eda + dedup + review + sheets (không gồm excluded vì cần người duyệt)

Thư viện cần: pillow, numpy, matplotlib (pyyaml nếu có thì dùng, không có vẫn chạy).
"""

import argparse
import ast
import csv
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SPLITS = ["train", "valid", "test"]
SPLIT_COLORS = {"train": "#4C72B0", "valid": "#DD8452", "test": "#55A868"}
IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CSV_ENC = "utf-8-sig"  # để Excel trên Windows mở đúng tiếng Việt


# ----------------------------------------------------------------------------- tiện ích
def load_names(root: Path):
    text = (root / "data.yaml").read_text(encoding="utf-8")
    try:
        import yaml

        names = yaml.safe_load(text)["names"]
    except ImportError:
        names = ast.literal_eval(re.search(r"names:\s*(\[.*?\])", text, re.S).group(1))
    if isinstance(names, dict):
        names = [names[k] for k in sorted(names)]
    return list(names)


def parse_label_line(parts):
    """Hỗ trợ cả bbox (5 số) lẫn polygon (class x1 y1 x2 y2 ...)."""
    c = int(float(parts[0]))
    vals = list(map(float, parts[1:]))
    if len(vals) == 4:
        cx, cy, w, h = vals
    else:
        xs, ys = vals[0::2], vals[1::2]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
    return c, cx, cy, w, h


def scan(root: Path):
    recs = []
    for split in SPLITS:
        img_dir = root / split / "images"
        for img in sorted(img_dir.iterdir()):
            if img.suffix.lower() not in IMG_EXT:
                continue
            with Image.open(img) as im:
                img_w, img_h = im.size
            lbl = root / split / "labels" / (img.stem + ".txt")
            boxes = []
            if lbl.exists():
                for line in lbl.read_text(encoding="utf-8").splitlines():
                    p = line.split()
                    if len(p) >= 5:
                        boxes.append(parse_label_line(p))
            recs.append(dict(split=split, path=img, W=img_w, H=img_h, boxes=boxes))
    print(f"Đã quét {len(recs)} ảnh.")
    return recs


def rel_name(r):
    return f"{r['split']}/images/{r['path'].name}"


def font(size):
    for f in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def tile_of(img, tile):
    return ImageOps.pad(img.convert("RGB"), (tile, tile), color=(225, 225, 225))


def make_grid(tiles, labels, cols, tile, title=None):
    rows = max(1, math.ceil(len(tiles) / cols))
    lab_h, head = 18, (42 if title else 0)
    sheet = Image.new("RGB", (cols * tile, head + rows * (tile + lab_h)), "white")
    d = ImageDraw.Draw(sheet)
    if title:
        d.text((8, 8), title, fill="black", font=font(22))
    f = font(12)
    max_chars = max(6, tile // 7)
    for i, (t, lab) in enumerate(zip(tiles, labels)):
        r, c = divmod(i, cols)
        x, y = c * tile, head + r * (tile + lab_h)
        sheet.paste(t, (x, y))
        d.rectangle([x, y, x + tile - 1, y + tile - 1], outline=(180, 180, 180))
        d.text((x + 3, y + tile + 2), lab[:max_chars], fill="black", font=f)
    return sheet


def save_fig(fig, path_noext: Path):
    fig.tight_layout()
    fig.savefig(path_noext.with_suffix(".png"), dpi=300)
    fig.savefig(path_noext.with_suffix(".pdf"))  # vector cho LaTeX
    plt.close(fig)


# ----------------------------------------------------------------------------- 1. EDA
def cmd_eda(recs, names, out: Path):
    fig_dir = out / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    nc = len(names)
    inst = {s: np.zeros(nc, int) for s in SPLITS}
    side = defaultdict(list)  # cạnh bbox quy đổi (px) theo split
    cls_side = defaultdict(list)
    rel_wh, centers = [], []
    per_img = defaultdict(list)
    res = Counter()
    n_img = Counter(r["split"] for r in recs)
    n_empty = Counter(r["split"] for r in recs if not r["boxes"])
    bad_cls = 0

    for r in recs:
        res[(r["W"], r["H"])] += 1
        per_img[r["split"]].append(len(r["boxes"]))
        for c, cx, cy, w, h in r["boxes"]:
            if not 0 <= c < nc:
                bad_cls += 1
                continue
            inst[r["split"]][c] += 1
            s = math.sqrt(max(w * r["W"] * h * r["H"], 0))
            side[r["split"]].append(s)
            cls_side[c].append(s)
            rel_wh.append((w, h))
            centers.append((cx, cy))

    total = sum(inst.values())
    labels = [f"{i:02d} {n}" for i, n in enumerate(names)]

    # Hình 1: phân bố lớp (stacked theo split)
    order = np.argsort(total)
    fig, ax = plt.subplots(figsize=(10, 11))
    left = np.zeros(nc)
    for s in SPLITS:
        ax.barh(np.arange(nc), inst[s][order], left=left, color=SPLIT_COLORS[s], label=s)
        left += inst[s][order]
    for y, v in enumerate(total[order]):
        ax.text(v, y, f" {v}", va="center", fontsize=7)
    ax.set_yticks(np.arange(nc), [labels[i] for i in order], fontsize=7)
    ax.set_xlabel("Số bbox")
    ax.set_title("Phân bố số bbox theo lớp và theo tập")
    ax.legend()
    save_fig(fig, fig_dir / "fig1_class_distribution")

    # Hình 2: kích thước bbox
    all_side = np.concatenate([np.array(side[s]) for s in SPLITS if side[s]])
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    bins = np.geomspace(max(all_side.min(), 1), all_side.max() + 1, 50)
    for s in SPLITS:
        if side[s]:
            axes[0].hist(side[s], bins=bins, histtype="step", lw=1.5, color=SPLIT_COLORS[s], label=s, density=True)
    for t, lab in ((32, "32px (small)"), (96, "96px (medium)")):
        axes[0].axvline(t, ls="--", c="gray")
        axes[0].text(t, axes[0].get_ylim()[1] * 0.9, f" {lab}", fontsize=8)
    axes[0].set_xscale("log")
    axes[0].set_xlabel("Cạnh bbox quy đổi √(w·h) (px)")
    axes[0].set_ylabel("Mật độ")
    axes[0].set_title("Phân bố kích thước bbox")
    axes[0].legend()
    wh = np.array(rel_wh)
    axes[1].scatter(wh[:, 0], wh[:, 1], s=2, alpha=0.25)
    axes[1].set_xlabel("w (tỉ lệ theo ảnh)")
    axes[1].set_ylabel("h (tỉ lệ theo ảnh)")
    axes[1].set_title("Chiều rộng - chiều cao bbox (chuẩn hoá)")
    save_fig(fig, fig_dir / "fig2_bbox_size")

    # Hình 3: độ phân giải ảnh
    top = res.most_common(10)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar([f"{w}×{h}" for (w, h), _ in top], [c for _, c in top], color="#4C72B0")
    for i, (_, c) in enumerate(top):
        ax.text(i, c, str(c), ha="center", va="bottom", fontsize=8)
    ax.set_ylabel("Số ảnh")
    ax.set_title(f"Độ phân giải ảnh ({len(res)} loại khác nhau, hiển thị tối đa 10)")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    save_fig(fig, fig_dir / "fig3_resolution")

    # Hình 4: số bbox mỗi ảnh
    fig, ax = plt.subplots(figsize=(8, 4))
    mx = max(max(v) for v in per_img.values())
    for s in SPLITS:
        ax.hist(
            per_img[s],
            bins=np.arange(mx + 2) - 0.5,
            histtype="step",
            lw=1.5,
            color=SPLIT_COLORS[s],
            label=s,
            density=True,
        )
    ax.set_xlabel("Số bbox trong một ảnh")
    ax.set_ylabel("Tỉ lệ ảnh")
    ax.set_title("Số đối tượng mỗi ảnh")
    ax.legend()
    save_fig(fig, fig_dir / "fig4_objects_per_image")

    # Hình 5: heatmap vị trí tâm bbox
    ct = np.array(centers)
    fig, ax = plt.subplots(figsize=(5.5, 5))
    hb = ax.hist2d(ct[:, 0], ct[:, 1], bins=40, range=[[0, 1], [0, 1]], cmap="viridis")
    fig.colorbar(hb[3], ax=ax, label="Số bbox")
    ax.invert_yaxis()
    ax.set_title("Vị trí tâm bbox trong ảnh")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    save_fig(fig, fig_dir / "fig5_bbox_center_heatmap")

    # Hình 6: kích thước bbox theo lớp
    fig, ax = plt.subplots(figsize=(10, 11))
    data = [cls_side.get(i, [np.nan]) for i in range(nc)]
    import warnings

    with warnings.catch_warnings():  # matplotlib mới báo deprecate 'vert' nhưng vẫn chạy
        warnings.simplefilter("ignore")
        ax.boxplot(data, vert=False, showfliers=False)
    ax.set_yticks(np.arange(1, nc + 1), labels, fontsize=7)
    ax.set_xscale("log")
    ax.axvline(32, ls="--", c="gray")
    ax.set_xlabel("Cạnh bbox quy đổi (px)")
    ax.set_title("Kích thước bbox theo lớp")
    save_fig(fig, fig_dir / "fig6_bbox_size_per_class")

    # Bảng số liệu
    with open(out / "class_stats.csv", "w", newline="", encoding=CSV_ENC) as f:
        w = csv.writer(f)
        w.writerow(["id", "class", *SPLITS, "total", "median_side_px"])
        for i in range(nc):
            med = float(np.median(cls_side[i])) if cls_side[i] else 0
            w.writerow([i, names[i], *[int(inst[s][i]) for s in SPLITS], int(total[i]), round(med, 1)])

    small = (all_side < 32).mean() * 100
    medium = ((all_side >= 32) & (all_side < 96)).mean() * 100
    weak_test = [names[i] for i in range(nc) if inst["test"][i] < 10]
    lines = [
        "# Tóm tắt EDA dữ liệu biển báo\n",
        "## Tổng quan theo tập\n",
        "| Tập | Số ảnh | Ảnh không bbox | Số bbox | bbox/ảnh TB |",
        "|---|---|---|---|---|",
    ]
    for s in SPLITS:
        nb = int(inst[s].sum())
        lines.append(f"| {s} | {n_img[s]} | {n_empty[s]} | {nb} | {nb / max(n_img[s], 1):.2f} |")
    lines += [
        "",
        f"- Tổng: {len(recs)} ảnh, {int(total.sum())} bbox, {nc} lớp.",
        f"- Kích thước bbox: small (<32px) {small:.1f}% · medium (32–96px) {medium:.1f}% · "
        f"large (≥96px) {100 - small - medium:.1f}%.",
        f"- Độ phân giải phổ biến nhất: {top[0][0][0]}×{top[0][0][1]} ({top[0][1]} ảnh); "
        f"{len(res)} độ phân giải khác nhau.",
        f"- Lớp nhiều nhất: {names[int(np.argmax(total))]} ({int(total.max())}); "
        f"ít nhất: {names[int(np.argmin(total))]} ({int(total.min())}); "
        f"tỉ lệ mất cân bằng {total.max() / max(total.min(), 1):.1f}×.",
    ]
    if "Gioi han toc do" in names:
        k = names.index("Gioi han toc do")
        lines.append(
            "- Lớp **Gioi han toc do** (đầu vào OCR): " + ", ".join(f"{s} {int(inst[s][k])}" for s in SPLITS) + " bbox."
        )
    if weak_test:
        lines.append(
            f"- ⚠ {len(weak_test)} lớp có <10 bbox trong tập test "
            f"(kết quả benchmark theo lớp kém tin cậy): {', '.join(weak_test)}."
        )
    if bad_cls:
        lines.append(f"- ⚠ {bad_cls} bbox có class id nằm ngoài 0..{nc - 1}.")
    lines += ["", "Hình: `figures/fig1..fig6` (PNG 300 dpi + PDF). Bảng chi tiết: `class_stats.csv`."]
    (out / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[eda] Xong -> {fig_dir} và {out / 'summary.md'}")


# ----------------------------------------------------------------------------- 2. Dedup
POP = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)


def dhash(path, size=8):
    with Image.open(path) as im:
        g = im.convert("L").resize((size + 1, size), Image.BILINEAR)
    a = np.asarray(g, dtype=np.int16)
    return np.packbits((a[:, 1:] > a[:, :-1]).flatten())


def cmd_dedup(recs, out: Path, thr: int, rf_prefix: bool, sample: int, force: bool):
    rev = out / "review"
    rev.mkdir(parents=True, exist_ok=True)
    print("[dedup] Đang tính dHash...")
    hashes = np.stack([dhash(r["path"]) for r in recs])
    n = len(recs)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for s in range(0, n, 256):
        d = POP[hashes[s : s + 256, None, :] ^ hashes[None, :, :]].sum(-1, dtype=np.int32)
        for i, j in zip(*np.nonzero(d <= thr)):
            if j > i + s:
                parent[find(i + s)] = find(j)
    if rf_prefix:  # gom các bản augment của cùng ảnh gốc Roboflow
        src = defaultdict(list)
        for i, r in enumerate(recs):
            if ".rf." in r["path"].name:
                src[r["path"].name.split(".rf.")[0]].append(i)
        for idx in src.values():
            for k in idx[1:]:
                parent[find(k)] = find(idx[0])

    groups = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(i)
    clusters = [g for g in groups.values() if len(g) > 1]
    clusters.sort(key=lambda g: (-len({recs[i]["split"] for i in g}), -len(g)))
    cross = [g for g in clusters if len({recs[i]["split"] for i in g}) > 1]
    same = [g for g in clusters if g not in cross]
    print(
        f"[dedup] {len(clusters)} cụm gần trùng: {len(cross)} cụm nằm ở nhiều tập, {len(same)} cụm trong cùng một tập."
    )

    rows, shown = [], []
    random.Random(0).shuffle(same)
    for k, g in enumerate(cross + same, 1):
        cid = f"C{k:04d}"
        typ = "cross_split" if g in cross else "same_split"
        g = sorted(g, key=lambda i: SPLITS.index(recs[i]["split"]))
        rows.append(
            [
                cid,
                typ,
                len(g),
                "+".join(sorted({recs[i]["split"] for i in g})),
                " | ".join(rel_name(recs[i]) for i in g),
                "",
                "",
            ]
        )
        if typ == "cross_split" or len(shown) - len(cross) < sample:
            shown.append((cid, g))

    csv_path = rev / "review_dups.csv"
    if csv_path.exists() and not force:
        print(f"[dedup] {csv_path.name} đã tồn tại -> KHÔNG ghi đè (thêm --force nếu muốn).")
    else:
        with open(csv_path, "w", newline="", encoding=CSV_ENC) as f:
            w = csv.writer(f)
            w.writerow(["cluster_id", "type", "n", "splits", "files", "decision", "note"])
            w.writerows(rows)

    per_page, tile, cols = 8, 150, 8
    for p in range(0, len(shown), per_page):
        tiles, labels = [], []
        for cid, g in shown[p : p + per_page]:
            row = g[:cols]
            for i in row:
                with Image.open(recs[i]["path"]) as im:
                    tiles.append(tile_of(im, tile))
                labels.append(f"{cid} {recs[i]['split']} {recs[i]['path'].stem}")
            for _ in range(cols - len(row)):  # mỗi cụm một hàng
                tiles.append(Image.new("RGB", (tile, tile), "white"))
                labels.append("")
        sheet = make_grid(tiles, labels, cols, tile, title=f"Cụm gần trùng (dHash ≤ {thr}) - trang {p // per_page + 1}")
        sheet.save(rev / f"dups_{p // per_page + 1:02d}.jpg", quality=90)
    print(f"[dedup] Xong -> {rev}/dups_*.jpg ({len(shown)} cụm được vẽ) và {csv_path.name}")


# ----------------------------------------------------------------------------- 3. Review ảnh không nhãn
def cmd_review(recs, out: Path, force: bool):
    rev = out / "review"
    rev.mkdir(parents=True, exist_ok=True)
    empty = [r for r in recs if not r["boxes"]]
    csv_path = rev / "review_unlabeled.csv"
    if csv_path.exists() and not force:
        print(f"[review] {csv_path.name} đã tồn tại -> KHÔNG ghi đè (thêm --force nếu muốn).")
    else:
        with open(csv_path, "w", newline="", encoding=CSV_ENC) as f:
            w = csv.writer(f)
            w.writerow(["idx", "split", "file", "decision", "note"])
            for k, r in enumerate(empty, 1):
                w.writerow([f"{k:03d}", r["split"], rel_name(r), "", ""])
    per_page, cols, tile = 30, 6, 230
    for p in range(0, len(empty), per_page):
        tiles, labels = [], []
        for k, r in enumerate(empty[p : p + per_page], p + 1):
            with Image.open(r["path"]) as im:
                tiles.append(tile_of(im, tile))
            labels.append(f"#{k:03d} {r['split']} {r['path'].stem}")
        sheet = make_grid(
            tiles, labels, cols, tile, title=f"Ảnh không có bbox ({len(empty)} ảnh) - trang {p // per_page + 1}"
        )
        sheet.save(rev / f"unlabeled_{p // per_page + 1:02d}.jpg", quality=90)
    print(f"[review] {len(empty)} ảnh -> {rev}/unlabeled_*.jpg và {csv_path.name}")


# ----------------------------------------------------------------------------- 4. Contact-sheet theo lớp
def cmd_sheets(recs, names, out: Path, per_class: int):
    sd = out / "contact_sheets"
    sd.mkdir(parents=True, exist_ok=True)
    by_cls = defaultdict(list)
    for r in recs:
        for b in r["boxes"]:
            if 0 <= b[0] < len(names):
                by_cls[b[0]].append((r, b))
    rng = random.Random(0)
    tile, cols = 112, 8
    for c, name in enumerate(names):
        items = by_cls.get(c, [])
        pick = rng.sample(items, min(per_class, len(items)))
        tiles, labels = [], []
        cache_path, cache_img = None, None
        for r, (_, cx, cy, w, h) in sorted(pick, key=lambda t: str(t[0]["path"])):
            if r["path"] != cache_path:
                cache_img = Image.open(r["path"]).convert("RGB")
                cache_path = r["path"]
            img_w, img_h = cache_img.size
            pw, ph = w * img_w * 1.2, h * img_h * 1.2  # nới 10% mỗi phía
            x0, y0 = max(cx * img_w - pw / 2, 0), max(cy * img_h - ph / 2, 0)
            x1, y1 = min(cx * img_w + pw / 2, img_w), min(cy * img_h + ph / 2, img_h)
            if x1 - x0 < 1 or y1 - y0 < 1:
                continue
            tiles.append(tile_of(cache_img.crop((x0, y0, x1, y1)), tile))
            labels.append(f"{r['split'][:2]} {r['path'].stem}")
        if not tiles:
            continue
        safe = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
        sheet = make_grid(
            tiles, labels, cols, tile, title=f"{c:02d} {name}  ({len(items)} bbox, hiển thị {len(tiles)})"
        )
        sheet.save(sd / f"class_{c:02d}_{safe}.jpg", quality=90)
    print(f"[sheets] Xong -> {sd}")


# ----------------------------------------------------------------------------- 5. excluded.txt
def cmd_excluded(out: Path):
    rev = out / "review"
    excluded, relabel, undecided = {}, [], []

    p = rev / "review_unlabeled.csv"
    if p.exists():
        with open(p, encoding=CSV_ENC) as f:
            for row in csv.DictReader(f):
                d = row["decision"].strip().lower()
                if d == "exclude":
                    excluded[row["file"]] = "unlabeled: " + (row["note"] or "loại")
                elif d == "relabel":
                    relabel.append(row["file"])
                elif d != "bg":
                    undecided.append(f"unlabeled #{row['idx']}")

    p = rev / "review_dups.csv"
    if p.exists():
        with open(p, encoding=CSV_ENC) as f:
            for row in csv.DictReader(f):
                d = row["decision"].strip().lower()
                files = [x.strip() for x in row["files"].split("|")]
                reason = f"near-duplicate {row['cluster_id']}"
                if d == "exclude_eval":  # giữ bản train, loại bản ở valid/test
                    drop = [x for x in files if not x.startswith("train/")]
                elif d == "exclude_train":  # giữ bản valid/test, loại bản ở train
                    drop = [x for x in files if x.startswith("train/")]
                elif d == "keep_one":  # giữ ảnh đầu tiên, loại phần còn lại
                    drop = files[1:]
                else:
                    drop = []
                    if d not in ("ok", "") or (d == "" and row["type"] == "cross_split"):
                        undecided.append(row["cluster_id"])
                for x in drop:
                    excluded.setdefault(x, reason + (f": {row['note']}" if row["note"] else ""))

    out.mkdir(parents=True, exist_ok=True)
    lines = ["# Ảnh bị loại khỏi huấn luyện/đánh giá. Định dạng: <đường dẫn tương đối>\\t<lý do>"]
    lines += [f"{k}\t{v}" for k, v in sorted(excluded.items())]
    (out / "excluded.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "relabel_todo.txt").write_text("\n".join(relabel) + "\n", encoding="utf-8")
    print(f"[excluded] {len(excluded)} ảnh -> {out / 'excluded.txt'}")
    print(f"[excluded] {len(relabel)} ảnh cần gán nhãn bổ sung -> {out / 'relabel_todo.txt'}")
    if undecided:
        print(
            f"[excluded] ⚠ {len(undecided)} mục chưa điền/sai giá trị decision: "
            f"{', '.join(undecided[:15])}{' ...' if len(undecided) > 15 else ''}"
        )


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["eda", "dedup", "review", "sheets", "excluded", "all"])
    ap.add_argument(
        "--data",
        type=Path,
        default=None,
        help="thư mục dataset chứa data.yaml (mặc định: raw_dir trong configs/data.yaml)",
    )
    ap.add_argument("--out", type=Path, default=Path("reports/data"))
    ap.add_argument("--thr", type=int, default=4, help="ngưỡng Hamming dHash (0-64) cho gần trùng")
    ap.add_argument("--rf-prefix", action="store_true", help="gom thêm theo tên ảnh gốc Roboflow")
    ap.add_argument("--dup-sample", type=int, default=40, help="số cụm cùng-tập vẽ minh hoạ")
    ap.add_argument("--per-class", type=int, default=48, help="số crop mỗi contact-sheet")
    ap.add_argument("--force", action="store_true", help="ghi đè file review_*.csv đã có")
    a = ap.parse_args()
    if a.data is None:
        from utci_vision.config import load_config, resolve

        a.data = resolve(load_config("data")["raw_dir"])

    if a.cmd == "excluded":
        return cmd_excluded(a.out)
    names = load_names(a.data)
    recs = scan(a.data)
    if a.cmd in ("eda", "all"):
        cmd_eda(recs, names, a.out)
    if a.cmd in ("dedup", "all"):
        cmd_dedup(recs, a.out, a.thr, a.rf_prefix, a.dup_sample, a.force)
    if a.cmd in ("review", "all"):
        cmd_review(recs, a.out, a.force)
    if a.cmd in ("sheets", "all"):
        cmd_sheets(recs, names, a.out, a.per_class)


if __name__ == "__main__":
    main()
