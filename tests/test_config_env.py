"""configs/, utci_vision.config, utci_vision.env."""

from __future__ import annotations

import pytest
import yaml

from utci_vision.config import load_classes, load_config, raw_class_map
from utci_vision.env import ROOT, Ports, check_environment, environment_summary


def test_classes_map_raw_dataset_yaml():
    classes = load_classes()
    mapping = raw_class_map(classes)
    assert len(classes) == 27 and len(mapping) == 32
    other = classes[-1]
    assert other.superclass == "other" and other.raw_ids == (5, 11, 12, 22, 25, 27)
    data_yaml = ROOT / "dataset" / "merged_dataset_traffic_signs" / "data.yaml"
    if data_yaml.exists():  # lớp không gộp giữ nguyên tên gốc
        raw_names = yaml.safe_load(data_yaml.read_text(encoding="utf-8"))["names"]
        assert all(c.name == raw_names[c.raw_ids[0]] for c in classes if len(c.raw_ids) == 1)
    assert {c.superclass for c in classes} == {"prohibitory", "warning", "mandatory", "info", "other"}
    assert {c.value_unit for c in classes if c.has_value} == {"km/h", "m"}


def test_raw_class_map_rejects_gaps_and_duplicates():
    from utci_vision.config import ClassInfo

    ok = (ClassInfo(0, "a", "a", "info", raw_ids=(0, 2)), ClassInfo(1, "b", "b", "info", raw_ids=(1,)))
    assert raw_class_map(ok) == {0: 0, 2: 0, 1: 1}
    with pytest.raises(AssertionError):
        raw_class_map((ClassInfo(0, "a", "a", "info", raw_ids=(0, 2)),))
    with pytest.raises(AssertionError):
        raw_class_map((ClassInfo(0, "a", "a", "info", raw_ids=(0,)), ClassInfo(1, "b", "b", "info", raw_ids=(0,))))


@pytest.mark.parametrize("name", ["data", "yolo", "pipeline", "verifier", "ocr", "api"])
def test_configs_load(name):
    assert load_config(name)


def test_yolo_config_is_finetuning_without_flip():
    cfg = load_config("yolo")
    assert cfg["model"].endswith(".pt")  # khởi tạo từ trọng số pretrained, không phải .yaml (train từ đầu)
    assert cfg["train"]["fliplr"] == 0.0 and cfg["train"]["lr0"] <= 0.002


def test_environment_summary_has_platform():
    assert environment_summary()["platform"] in {"local", "colab", "kaggle"}
    assert isinstance(check_environment(), list)


def test_ports_are_custom_and_overridable(monkeypatch):
    ports = Ports.from_env()
    assert not {ports.api, ports.web, ports.dev, ports.jupyter} & {8000, 8080, 5173, 8888, 80}
    monkeypatch.setenv("UTCI_API_PORT", "19999")
    assert Ports.from_env().api == 19999


def test_env_example_has_no_inline_comments():
    for line in (ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            assert "#" not in line, f"ghi chú cuối dòng làm hỏng giá trị: {line}"
