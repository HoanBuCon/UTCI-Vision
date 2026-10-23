"""Suy luận nhanh không qua web: ảnh / thư mục ảnh / video -> ảnh, video đã vẽ + JSON. Phụ trách: TV3 — S2.

    python scripts/infer.py --source <đường dẫn> [--debug]

TODO: pipeline.Recognizer(video=<là video>) -> visualize.draw -> outputs/infer/.
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True)
    parser.add_argument("--out", default="outputs/infer")
    parser.add_argument("--debug", action="store_true")
    parser.parse_args()
    raise NotImplementedError("TODO(TV3, S2)")


if __name__ == "__main__":
    main()
