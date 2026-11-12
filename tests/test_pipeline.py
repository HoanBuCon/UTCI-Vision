"""tracking, ocr (hậu xử lý), pipeline.Recognizer với detector giả — không cần trọng số."""

from __future__ import annotations

import numpy as np
import pytest

from utci_vision.config import load_config
from utci_vision.ocr import correct_text, parse_meaning, parse_value, vote
from utci_vision.pipeline import Components, Recognizer
from utci_vision.structures import Detection, SignText, SignValue
from utci_vision.tracking import Tracker


def test_tracker_keeps_id_votes_label_and_confirms_after_min_hits():
    tr = Tracker(iou_threshold=0.3, max_age=2, min_hits=3, vote_window=5)
    out = []
    for i in range(6):
        x = 100 + 4 * i  # biển trôi dần sang phải
        cls = 9 if i == 2 else 5  # một frame YOLO đọc nhầm lớp
        out.append(tr.update([Detection((x, 50, x + 30, 80), cls, 0.8)], i))
    assert out[0] == [] and out[1] == []  # chưa đủ min_hits
    assert all(len(o) == 1 and o[0].track_id == 1 and o[0].class_id == 5 for o in out[2:])
    for i in range(6, 10):  # mất dấu quá max_age -> xoá track
        tr.update([], i)
    assert tr.tracks == []


def test_tracker_separates_two_signs():
    tr = Tracker(0.3, 5, 1, 5)
    dets = tr.update([Detection((0, 0, 20, 20), 1, 0.9), Detection((200, 0, 220, 20), 2, 0.9)], 0)
    assert {d.track_id for d in dets} == {1, 2}


@pytest.mark.parametrize(
    ("raw", "unit", "expected"),
    [
        ("50", "km/h", 50),
        ("6O", "km/h", 60),
        ("45", "km/h", None),
        ("3,5m", "m", 3.5),
        ("2.0m", "m", 2.0),
        ("12", "m", None),
    ],
)
def test_parse_value(raw, unit, expected):
    valid = load_config("ocr")["value"]["valid_values"]
    v = parse_value(raw, unit, valid)
    assert (v.number if v else None) == expected


def test_parse_meaning_time_distance_except():
    m = parse_meaning("Trừ xe buýt 6h-22h, cách 100m")
    assert m["time_ranges"] == [["06:00", "22:00"]] and m["distance_m"] == 100
    assert m["except_vehicles"][0].startswith("xe buýt")


def test_correct_text_and_vote():
    assert correct_text("KIỀM TRA", ["KIỂM TRA", "BẾN XE BUÝT"], 80) == "KIỂM TRA"
    assert correct_text("xyz", ["KIỂM TRA"], 80) == "xyz"
    best = vote([SignValue(50, "km/h", 0.6), SignValue(60, "km/h", 0.9), SignValue(50, "km/h", 0.5)])
    assert best.number == 50  # tổng tin cậy 1.1 > 0.9
    assert vote([SignText("a", "A", 0.4), SignText("b", "B", 0.7)]).text == "B" and vote([]) is None


class FakeDetector:
    def __init__(self, boxes):
        self.boxes = boxes

    def detect(self, images, conf=None, imgsz=None):
        return [[Detection(b, 5, 0.9) for b in self.boxes] for _ in images]


def _cfg(*off):
    cfg = load_config("pipeline")
    cfg["ocr"]["enabled"] = False
    cfg["verifier"]["enabled"] = False
    for k in off:
        cfg[k]["enabled"] = False
    return cfg


def test_recognizer_image_mode_enhances_dark_frames_only():
    rec = Recognizer(_cfg(), Components(detector=FakeDetector([(10, 10, 40, 40)])))
    dark = np.full((240, 320, 3), 20, np.uint8)
    r = rec.process(dark, debug=True)
    assert [d.class_id for d in r.detections] == [5] and "gamma" in r.debug["ops"] and "enhanced" in r.debug["images"]
    assert set(r.latency_ms) >= {"enhance", "detector", "total"}
    bright = np.dstack([np.tile(np.linspace(60, 230, 320, dtype=np.uint8), (240, 1))] * 3)  # sáng, tương phản, mượt
    assert rec.process(bright, debug=True).debug["ops"] == []


def test_recognizer_video_mode_tracks():
    rec = Recognizer(_cfg(), Components(detector=FakeDetector([(10, 10, 40, 40)])), video=True)
    frame = np.full((240, 320, 3), 120, np.uint8)
    results = [rec.process(frame) for _ in range(4)]
    rec.close()
    assert results[0].detections == [] and results[3].detections[0].track_id == 1
    assert results[3].frame_idx == 3 and "tracking" in results[3].latency_ms


def test_recognizer_without_tracking_in_video_runs_per_frame():
    rec = Recognizer(_cfg("tracking"), Components(detector=FakeDetector([(10, 10, 40, 40)])), video=True)
    assert rec.tracker is None and len(rec.process(np.zeros((64, 64, 3), np.uint8)).detections) == 1
