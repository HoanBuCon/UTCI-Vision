"""Sinh train_local / train_colab / train_kaggle.ipynb từ notebooks/train/_template.py (ADR-006).

    python scripts/build_notebooks.py           # ghi 3 notebook
    python scripts/build_notebooks.py --check   # CI: báo lỗi nếu notebook lệch template

Cú pháp template: "# %%" ô code chung, "# %% [markdown]" ô markdown chung,
"# %% [colab]" / "# %% [markdown, kaggle]"... chỉ đưa vào notebook của nền tảng đó.
Chuỗi "{platform}" trong ô markdown được thay bằng tên nền tảng.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "notebooks" / "train" / "_template.py"
PLATFORMS = {"local": "Local", "colab": "Google Colab", "kaggle": "Kaggle"}
MARKER = re.compile(r"^# %%(?:\s*\[(?P<tags>[^\]]*)\])?\s*$")


def parse_template(text: str) -> list[tuple[str, set[str], str]]:
    """-> [(kind 'code'|'markdown', platforms, source)]; bỏ phần chú thích trước ô đầu tiên."""
    cells, current = [], None
    for line in text.splitlines():
        m = MARKER.match(line)
        if m:
            if current:
                cells.append(current)
            tags = {t.strip() for t in (m.group("tags") or "").split(",") if t.strip()}
            kind = "markdown" if "markdown" in tags else "code"
            platforms = (tags - {"markdown"}) or set(PLATFORMS)
            unknown = platforms - set(PLATFORMS)
            if unknown:
                raise ValueError(f"Thẻ nền tảng không hợp lệ: {unknown}")
            current = (kind, platforms, [])
        elif current is not None:
            current[2].append(line)
    if current:
        cells.append(current)
    return [(kind, plats, "\n".join(lines).strip("\n")) for kind, plats, lines in cells]


def build(platform: str, cells: list[tuple[str, set[str], str]]) -> nbformat.NotebookNode:
    nb = nbformat.v4.new_notebook()
    for kind, plats, source in cells:
        if platform not in plats:
            continue
        if kind == "markdown":
            md = "\n".join(line[2:] if line.startswith("# ") else line.lstrip("#") for line in source.splitlines())
            nb.cells.append(nbformat.v4.new_markdown_cell(md.replace("{platform}", PLATFORMS[platform])))
        else:
            nb.cells.append(nbformat.v4.new_code_cell(source))
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.metadata["language_info"] = {"name": "python"}
    if platform == "colab":
        nb.metadata["accelerator"] = "GPU"
    for i, cell in enumerate(nb.cells):
        cell["id"] = f"{platform}-{i:02d}"  # id ổn định -> diff gọn, --check so sánh được
    nbformat.validate(nb)
    return nb


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    cells = parse_template(TEMPLATE.read_text(encoding="utf-8"))
    stale = []
    for platform in PLATFORMS:
        out = TEMPLATE.parent / f"train_{platform}.ipynb"
        content = nbformat.writes(build(platform, cells)) + "\n"
        if args.check:
            if not out.exists() or out.read_text(encoding="utf-8") != content:
                stale.append(out.name)
        else:
            out.write_text(content, encoding="utf-8")
            print(f"Đã ghi {out.relative_to(ROOT)}")
    if stale:
        print(f"Notebook lệch template: {stale} — chạy python scripts/build_notebooks.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
