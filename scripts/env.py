"""Môi trường (ADR-005).

python scripts/env.py check    # torch/CUDA/GPU tự cài + thư viện dùng chung + cổng dịch vụ
python scripts/env.py freeze   # requirements.lock, đã LOẠI torch/CUDA
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict

from utci_vision.env import GPU_PACKAGE_PREFIXES, ROOT, Ports, check_environment, environment_summary


def check() -> None:
    print(json.dumps(environment_summary() | {"ports": asdict(Ports.from_env())}, ensure_ascii=False, indent=2))
    warnings = check_environment()
    print(*(f"[!] {w}" for w in warnings), sep="\n") if warnings else print("[OK] Môi trường sẵn sàng.")


def freeze() -> None:
    frozen = subprocess.check_output([sys.executable, "-m", "pip", "freeze", "--exclude-editable"], text=True)
    kept = [ln for ln in frozen.splitlines() if ln and not ln.lower().startswith(GPU_PACKAGE_PREFIXES)]
    header = "# Sinh bởi `python scripts/env.py freeze` — KHÔNG chứa torch/CUDA (mỗi người tự cài, ADR-005)\n"
    (ROOT / "requirements.lock").write_text(header + "\n".join(kept) + "\n", encoding="utf-8")
    print(f"requirements.lock: {len(kept)} gói")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("cmd", choices=["check", "freeze"])
    {"check": check, "freeze": freeze}[parser.parse_args().cmd]()
