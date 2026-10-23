"""utci_vision.training, utci_vision.registry, notebook fine-tune."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile

import pandas as pd
import pytest

from utci_vision.env import ROOT
from utci_vision.registry import FIELDS, log_run
from utci_vision.training import RunRecord, extract_dataset, new_run_id, verify_checksum, verify_extracted


def test_run_record_roundtrip(tmp_path):
    rid = new_run_id("yolo11s.pt", 960, smoke=True)
    assert rid.endswith("_yolo11s_960_smoke")
    path = RunRecord(run_id=rid, author="TV3", dataset_version="v1", metrics={"yolo": {"map50": 0.5}}).save(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["run_id"] == rid and "environment" in data and "_t0" not in data


def test_registry_has_environment_columns(tmp_path):
    reg = tmp_path / "registry.csv"
    log_run("E1", "TV1", "cfg", "v1", {"map50": 0.8}, registry=reg, environment={"platform": "kaggle", "torch": "2.x"})
    df = pd.read_csv(reg)
    assert list(df.columns) == FIELDS and df.loc[0, "platform"] == "kaggle"


def test_dataset_checksums(tmp_path):
    ds = tmp_path / "ds"
    ds.mkdir()
    (ds / "data.yaml").write_text("path: .\nnames: [a]\n", encoding="utf-8")
    (ds / "manifest.csv").write_text("image\nx.jpg\n", encoding="utf-8")
    sha = hashlib.sha256((ds / "manifest.csv").read_bytes()).hexdigest()
    (ds / "VERSION.json").write_text(json.dumps({"version": "v1", "manifest_sha256": sha}), encoding="utf-8")
    assert verify_extracted(ds) == sha

    zp = tmp_path / "utci_v1.zip"
    with zipfile.ZipFile(zp, "w") as zf:
        for f in ds.iterdir():
            zf.write(f, f"utci_v1/{f.name}")
    sha_file = tmp_path / "utci_v1.sha256"
    sha_file.write_text(hashlib.sha256(zp.read_bytes()).hexdigest(), encoding="utf-8")
    verify_checksum(zp, sha_file)
    assert (extract_dataset(zp, tmp_path / "out") / "data.yaml").exists()
    sha_file.write_text("0" * 64, encoding="utf-8")
    with pytest.raises(ValueError):
        verify_checksum(zp, sha_file)


def test_notebooks_in_sync_with_template():
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_notebooks.py"), "--check"], cwd=ROOT)
    assert result.returncode == 0, "Chạy python scripts/build_notebooks.py"
