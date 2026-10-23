"""UTCI-VISION — nhận diện biển báo giao thông Việt Nam.

Mỗi module ở gốc là một khâu của pipeline (ADR-001), nhãn kỹ thuật ghi trong docstring:
enhance [CV] · detector [DL] · tracking [CV] · verifier [CV+ML] · ocr [CV+DL] · pipeline (điều phối).
Gói con: data (công cụ dữ liệu), evaluation (metric, thí nghiệm), api (FastAPI).
"""

__version__ = "0.1.0"
