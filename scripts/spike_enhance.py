"""Spike S1 (TV2): đo chất lượng ảnh trên toàn dataset để chọn ngưỡng tăng cường, xuất hình trước/sau.

    python scripts/spike_enhance.py [--n 30]

Kết quả: reports/spike_enhance/quality.csv, report/figures/spike_enhance/*.png và ngưỡng đề xuất in ra màn hình
(phân vị 5% độ sáng / tương phản, 95% Laplacian) để điền configs/pipeline.yaml > quality.
"""

from __future__ import annotations

import argparse

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from utci_vision.config import load_config, resolve  # noqa: E402
from utci_vision.data.labels import list_images  # noqa: E402
from utci_vision.enhance import FrameQuality, assess, enhance, needed_ops  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--n", type=int, default=30, help="số ảnh tối nhất để vẽ trước/sau")
    args = parser.parse_args()

    data_cfg, pipe_cfg = load_config("data"), load_config("pipeline")
    raw = resolve(data_cfg["raw_dir"])
    rows = []
    for split in data_cfg["raw_splits"]:
        for path in list_images(raw / split):
            q = assess(cv2.imread(str(path)), pipe_cfg["quality"]["downscale_width"])
            rows.append({"split": split, "path": str(path), **vars(q)})
    df = pd.DataFrame(rows)
    out_csv = resolve("reports/spike_enhance")
    out_csv.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv / "quality.csv", index=False)

    proposed = {
        "dark_mean_v": round(float(df["mean_v"].quantile(0.05)), 3),
        "low_contrast_std_l": round(float(df["std_l"].quantile(0.05)), 3),
        "noisy_laplacian": round(float(df["laplacian_var"].quantile(0.95)), 0),
    }
    current = {k: pipe_cfg["quality"][k] for k in proposed}
    print(df[["mean_v", "std_l", "laplacian_var"]].describe(percentiles=[0.05, 0.5, 0.95]).round(3).to_string())
    print("Ngưỡng hiện tại :", current)
    print("Đề xuất (P5/P95):", proposed)
    hit = df.apply(
        lambda r: bool(
            needed_ops(FrameQuality(r["mean_v"], r["std_l"], r["laplacian_var"]), {**pipe_cfg["quality"], **proposed})
        ),
        axis=1,
    )
    print(f"Tỉ lệ ảnh sẽ được tăng cường với ngưỡng đề xuất: {hit.mean():.1%}")

    fig_dir = resolve("report/figures/spike_enhance")
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, col, thr in zip(axes, ["mean_v", "std_l", "laplacian_var"], proposed.values()):
        ax.hist(df[col], bins=60, color="#4c72b0")
        ax.axvline(thr, color="red", linestyle="--", label=f"ngưỡng {thr}")
        ax.set_title(col)
        ax.legend()
    fig.tight_layout()
    fig.savefig(fig_dir / "quality_distribution.png", dpi=150)

    darkest = df.nsmallest(args.n, "mean_v")
    cols = 6
    for start in range(0, len(darkest), cols):
        chunk = darkest.iloc[start : start + cols]
        fig, axes = plt.subplots(2, len(chunk), figsize=(3.2 * len(chunk), 4.4), squeeze=False)
        for i, (_, r) in enumerate(chunk.iterrows()):
            img = cv2.imread(r["path"])
            ops = needed_ops(
                FrameQuality(r["mean_v"], r["std_l"], r["laplacian_var"]), {**pipe_cfg["quality"], **proposed}
            ) or {"gamma", "clahe"}
            out = enhance(img, ops, pipe_cfg["enhance"])
            for row, im, title in ((0, img, f"V={r['mean_v']:.2f}"), (1, out, "+".join(sorted(ops)))):
                axes[row, i].imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
                axes[row, i].set_title(title, fontsize=9)
                axes[row, i].axis("off")
        fig.tight_layout()
        fig.savefig(fig_dir / f"before_after_{start // cols + 1:02d}.png", dpi=110)
        plt.close("all")
    print(f"Hình: {fig_dir}")


if __name__ == "__main__":
    main()
