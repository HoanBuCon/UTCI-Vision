"""Môi trường chạy: cổng dịch vụ từ `.env` (không dùng cổng mặc định) và thông tin torch/CUDA/GPU (ADR-005)."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MIN_TORCH = (2, 4)
GPU_PACKAGE_PREFIXES = ("torch", "torchvision", "torchaudio", "nvidia-", "triton")


def load_dotenv(path: Path = ROOT / ".env") -> None:
    """Nạp KEY=VALUE từ .env vào os.environ (không ghi đè biến đã có)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.partition("=")
        if sep and not key.strip().startswith("#"):
            os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Ports:
    """Cổng của mọi tiến trình — cấu hình qua .env, giá trị mặc định cố ý tránh 8000/8080/5173/8888."""

    api: int
    web: int
    dev: int
    jupyter: int

    @classmethod
    def from_env(cls) -> Ports:
        load_dotenv()
        return cls(
            api=int(os.environ.get("UTCI_API_PORT", 18100)),
            web=int(os.environ.get("UTCI_WEB_PORT", 18080)),
            dev=int(os.environ.get("UTCI_DEV_PORT", 15173)),
            jupyter=int(os.environ.get("UTCI_JUPYTER_PORT", 18888)),
        )


def git_commit(repo: Path = ROOT) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=repo, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "no-git"


def detect_platform() -> str:
    """local | colab | kaggle."""
    if "COLAB_RELEASE_TAG" in os.environ or "google.colab" in sys.modules:
        return "colab"
    if "KAGGLE_KERNEL_RUN_TYPE" in os.environ:
        return "kaggle"
    return "local"


def _version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def environment_summary() -> dict:
    info = {"platform": detect_platform(), "python": platform.python_version(), "os": platform.platform()}
    try:
        import torch

        cuda_ok = torch.cuda.is_available()
        info |= {
            "torch": torch.__version__,
            "cuda": torch.version.cuda,
            "cuda_available": cuda_ok,
            "gpu": torch.cuda.get_device_name(0) if cuda_ok else None,
        }
    except ImportError:
        info |= {"torch": None, "cuda": None, "cuda_available": False, "gpu": None}
    for pkg in ("ultralytics", "opencv-python", "opencv-python-headless", "lightgbm", "scikit-learn", "vietocr"):
        info[pkg] = _version(pkg)
    return info


def check_environment() -> list[str]:
    """Danh sách cảnh báo (rỗng = ổn)."""
    info, warnings = environment_summary(), []
    if info["torch"] is None:
        warnings.append("Chưa cài PyTorch — tự cài theo GPU tại https://pytorch.org/get-started/locally/")
    else:
        if tuple(int(x) for x in info["torch"].split("+")[0].split(".")[:2]) < MIN_TORCH:
            warnings.append(f"torch {info['torch']} thấp hơn mức tối thiểu {MIN_TORCH[0]}.{MIN_TORCH[1]}")
        if info["torch"].startswith("2.4.0") and sys.platform == "win32":
            warnings.append("Ultralytics không hỗ trợ torch 2.4.0 trên Windows")
        if not info["cuda_available"]:
            warnings.append("Không thấy GPU CUDA — chạy CPU (đủ cho suy luận, chậm khi fine-tune)")
    if info["opencv-python"] and info["opencv-python-headless"]:
        warnings.append("Có cả opencv-python và opencv-python-headless — gỡ bản headless")
    if info["vietocr"] is None:
        warnings.append("Chưa cài VietOCR: pip install --no-deps -r requirements-nodeps.txt")
    return warnings
