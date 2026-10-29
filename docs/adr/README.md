# Architecture Decision Records

Mỗi quyết định kỹ thuật quan trọng là một file `ADR-NNN-ten-ngan.md` gồm: Trạng thái, Bối cảnh, Quyết định, Hệ quả.
Trạng thái: `Proposed` → `Accepted` / `Rejected` / `Superseded by ADR-xxx`. Không xoá ADR cũ.

| ADR | Tiêu đề | Trạng thái |
|---|---|---|
| [001](ADR-001-pipeline-thong-nhat.md) | Một hệ thống — YOLO11 làm lõi, CV/ML/OCR bổ trợ theo track | Accepted |
| [002](ADR-002-loc-va-chia-lai-du-lieu.md) | Lọc & chia lại dữ liệu theo cụm gần trùng; vai trò train/val/test | Proposed (TV5 chốt ở Review S1) · mục 3 thay bởi 009 |
| [003](ADR-003-web-docker.md) | Web React + FastAPI, đóng gói Docker Compose | Accepted |
| [004](ADR-004-yolo11.md) | Detector YOLO11 — fine-tune từ pretrained | Accepted |
| [005](ADR-005-chinh-sach-phien-ban.md) | Không khoá torch/CUDA — chỉ khoá thư viện dùng chung | Accepted |
| [006](ADR-006-notebook-huan-luyen.md) | Fine-tune qua 3 notebook sinh từ một template | Accepted |
| [007](ADR-007-cong-custom-makefile.md) | Cổng custom qua `.env` + Makefile | Accepted |
| 008 | Bộ xác minh: tập đặc trưng & ngưỡng | Chờ thí nghiệm E3 (TV1, Sprint 3) |
| [009](ADR-009-gop-lop-hiem.md) | Gộp 6 lớp hiếm vào "Biển báo khác" (32 → 27 lớp) | Accepted |
