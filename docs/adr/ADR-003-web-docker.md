# ADR-003: Web React + FastAPI, đóng gói Docker Compose

- **Trạng thái:** Accepted (nhóm duyệt 2026-10-22) · **Người đề xuất:** TV1, TV3

## Bối cảnh
Demo phải là bản web, chạy bằng Docker trên máy giảng viên/nhóm (Windows, có hoặc không có GPU NVIDIA).
Repo tham khảo dùng PyQt5 + X11 trong Docker — khó chạy trên Windows và không phải web.

## Quyết định
- **Backend:** FastAPI (Python 3.11) import trực tiếp package `utci_vision`; mô hình nạp một lần khi khởi động.
  REST cho ảnh/video (video chạy nền theo job), WebSocket cho webcam. Không dùng hàng đợi ngoài (Redis/Celery) — đủ cho demo 1–vài người dùng.
- **Frontend:** React + TypeScript + Vite, build tĩnh, phục vụ bằng Nginx; Nginx reverse-proxy `/api` (kể cả WebSocket) sang backend.
- **Docker Compose:** service `api` (image CPU mặc định, torch CPU) và `web` (Nginx). Profile `gpu` dùng image CUDA + NVIDIA Container Toolkit (WSL2).
  Trọng số mô hình mount từ `./models` (không đóng vào image).
- Webcam: xử lý vẽ ở client (canvas), server chỉ trả JSON → giảm băng thông và độ trễ.

## Phương án đã loại
- Streamlit: nhanh nhưng khó làm realtime webcam mượt và khó tuỳ biến giao diện sản phẩm.
- PyQt5: không phải web.
- Gradio: tương tự Streamlit.

## Hệ quả
- (+) `make up` (hoặc `make up-gpu`) là chạy; mở `http://localhost:18080` — cổng theo `.env` (ADR-007).
- (−) Thêm khối lượng frontend (TV2 phụ trách, TV3 hỗ trợ); cần thống nhất schema JSON sớm (Sprint 1).
- Endpoint: `GET /api/v1/health`, `GET /api/v1/classes`, `POST /api/v1/detect/image`, `POST /api/v1/jobs/video`, `GET /api/v1/jobs/{id}`, `WS /api/v1/stream`.
