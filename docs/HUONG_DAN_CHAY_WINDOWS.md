# Chạy hệ thống trên Windows

Kiểm tra trên máy local ngày 12/11/2026: Python 3.11, RTX 3050 Laptop 6 GB, PyTorch 2.14.1+cu130, torchvision 0.29.1+cu130. Môi trường nằm trong `.venv`; các lệnh dưới đây chạy từ thư mục gốc `UTCI-Vision` bằng PowerShell.

## 1. Trạng thái đã chuẩn bị

- Đã cài thư viện trong `requirements.txt`, VietOCR bằng `--no-deps`, package dự án bằng editable install; cài thêm pytest, ruff, nbformat để kiểm tra mã.
- Đã chạy `npm.cmd ci`, build và kiểm tra TypeScript thành công.
- Đã tạo `.env` từ mẫu, chọn `UTCI_DEVICE=0` để API dùng GPU.
- Đã chép `yolo11.pt` và `run_record.json` từ lần huấn luyện bên dưới vào `models/current/`. Không ghi thêm bản trùng vào sổ thí nghiệm vì run này đã có trong `experiments/registry.csv`.
- VietOCR đã tải và nạp thành công; đã lưu trọng số cùng cấu hình vào `models/vietocr/` để những lần sau không cần tải lại.

## 2. Thư mục runs_out chứa gì?

Thư mục `runs_out/20261029-1030_yolo11s_960/` là kết quả của **một lần huấn luyện**, không phải nhiều mô hình độc lập.

| Tệp | Ý nghĩa |
|---|---|
| `run_record.json` | Ghi cấu hình, môi trường Colab/Tesla T4, thời gian chạy và chỉ số của lần huấn luyện |
| `yolo11.pt` | Trọng số dùng để suy luận; SHA-256 trùng `yolo/weights/best.pt` |
| `yolo/weights/best.pt` | Checkpoint được chọn theo tiêu chí xác thực của Ultralytics |
| `yolo/weights/last.pt` | Checkpoint ở cuối lần huấn luyện; khác nội dung với `best.pt` |
| `yolo/weights/epoch*.pt` | Checkpoint định kỳ; có thể chứa trạng thái phục vụ tiếp tục huấn luyện nên lớn hơn bản suy luận |
| `yolo/args.yaml` | Tham số thực dùng; các đường dẫn `/content/...` thuộc máy Colab cũ |
| `yolo/results.csv` | 80 dòng kết quả tương ứng 80 epoch |
| `yolo/results.png`, `Box*_curve.png` | Đường cong loss, precision, recall, F1, PR |
| `confusion_matrix*.png` | Ma trận nhầm lẫn |
| `train_batch*.jpg`, `val_batch*.jpg` | Ảnh minh hoạ batch, nhãn và dự đoán |

Run dùng YOLO11s, kích thước huấn luyện 960, batch 8, 80 epoch, AdamW, learning rate ban đầu 0,001, freeze 0. Theo `run_record.json`: precision 0,9204; recall 0,8382; mAP@50 0,8947; mAP@50:95 0,6850. Đây là **số liệu xác thực ghi từ lần huấn luyện**, không phải đánh giá mới trên tập test hoặc toàn bộ hệ thống.

## 3. Khởi động hằng ngày

Chạy nhanh trong một terminal PowerShell hoặc Git Bash:

```powershell
cd D:\Workspace\CV\UTCI-Vision
make dev
```

Lệnh này mở API và web local, đọc cổng từ `.env`. Nhấn `Ctrl+C` để dừng cả hai. Dùng `make dev-status` để kiểm tra cổng. Nếu đã có dịch vụ chiếm cổng, lệnh sẽ báo và giữ nguyên dịch vụ đó.

Chạy riêng từng phần bằng `make dev-api` và `make dev-web`, hoặc dùng các lệnh trực tiếp dưới đây.

Mở hai terminal PowerShell trong VS Code.

Terminal thứ nhất chạy API:

```powershell
cd D:\Workspace\CV\UTCI-Vision
.\.venv\Scripts\python.exe -m utci_vision.api
```

Chờ dòng `Application startup complete`. API: http://127.0.0.1:18100. Tài liệu API: http://127.0.0.1:18100/docs.

Terminal thứ hai chạy giao diện:

```powershell
cd D:\Workspace\CV\UTCI-Vision
npm.cmd --prefix web run dev
```

Mở **http://localhost:15173/demo/dl**, tải ảnh biển báo lên. Dùng `localhost` cho giao diện vì Vite có thể lắng nghe trên địa chỉ IPv6 của localhost thay vì `127.0.0.1`.

Dừng bằng `Ctrl+C` trong mỗi terminal. Nếu có lỗi cổng đang được sử dụng, kiểm tra tiến trình cũ trước khi chạy thêm:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 18100,15173 -ErrorAction SilentlyContinue
```

## 4. Cấu hình và luồng xử lý

API nạp cấu hình qua `config.py`, đọc cổng và thiết bị trong `.env`. `pipeline.py` điều phối tăng cường ảnh thích nghi → YOLO11 → theo dõi cho video → xác minh/đọc chữ. Ảnh tĩnh chạy tác vụ đọc đồng bộ; video dùng tác vụ nền theo đối tượng theo dõi.

| Tệp | Cấu hình chính |
|---|---|
| `.env` | API 18100, giao diện dev 15173, Docker web 18080; thiết bị API local là GPU 0 |
| `configs/pipeline.yaml` | Suy luận YOLO ở kích thước 1280, conf 0,25, IoU NMS 0,5; bật tracking và OCR; tắt bộ xác minh theo mặc định |
| `configs/yolo.yaml` | Cấu hình huấn luyện; không điều khiển kích thước suy luận mặc định của API |
| `configs/classes.yaml` | 27 lớp, tên tiếng Việt và thông tin của từng loại biển |
| `configs/ocr.yaml` | VietOCR, cắt vùng chữ/số, giới hạn kích thước và xử lý chuỗi sau nhận dạng |
| `configs/traditional.yaml` | Phát hiện ứng viên bằng màu/hình dạng, phân loại HOG + HSV + SVM |
| `configs/verifier.yaml` | Đặc trưng màu/hình dạng/Hu/HOG-PCA và bộ xác minh LightGBM tùy chọn |
| `configs/api.yaml` | Ảnh tối đa 10 MB, video tối đa 200 MB và 180 giây |
| `configs/data.yaml` | Dữ liệu và cách chia tập; không cần dataset đầy đủ để tải ảnh mới lên nhận diện |

Không cần cài CUDA Toolkit riêng cho bước suy luận đã được kiểm tra; bản PyTorch CUDA trong `.venv` đã chạy được với driver hiện tại. Khi cần cài lại PyTorch, đối chiếu [hướng dẫn chính thức](https://pytorch.org/get-started/locally/).

## 5. Các phần còn thiếu trên máy này

- Chưa có `models/current/hog_svm.joblib`: trang demo truyền thống và so sánh chưa chạy được. Lấy mô hình đã huấn luyện từ nhóm, hoặc khôi phục đúng dataset rồi chạy `.\.venv\Scripts\python.exe scripts/train_hog_svm.py`.
- Chưa có `models/current/verifier.joblib`: không bật tùy chọn xác minh trên web. Bộ này đang tắt mặc định.
- Chưa có `dataset/processed/v1`: danh sách ảnh mẫu có thể rỗng; vẫn có thể tải ảnh mới lên. Chưa thể đánh giá lại trên test hoặc huấn luyện các mô hình bổ trợ khi thiếu dữ liệu.
- `/api/v1/health` báo `degraded` do thiếu mô hình truyền thống. Kiểm tra từng mục: `detector.loaded` và `ocr.loaded` phải là `true` để dùng luồng học sâu và đọc chữ.
- VietOCR được cài `--no-deps` theo quy ước dự án. `pip check` vẫn báo các ràng buộc cũ của VietOCR không khớp; không tự hạ Pillow/einops hoặc cài toàn bộ phụ thuộc cũ chỉ để xoá cảnh báo. Việc nạp mô hình và suy luận thực tế đã được kiểm tra.

## 6. Kiểm tra đã thực hiện

- GPU: CUDA khả dụng, phép nhân ma trận chạy trên RTX 3050.
- `pytest -q`: 76 bài kiểm thử đạt.
- `ruff check src scripts tests`: đạt.
- `npm.cmd --prefix web run build` và kiểm tra TypeScript: đạt.
- API nhận ảnh kiểm tra và trả HTTP 200 cùng các khung bao/lớp dự đoán. Ảnh thử lấy từ ảnh ghép batch xác thực có sẵn; phép thử này chỉ xác nhận luồng chạy, không phải đo độ chính xác.

Log kiểm tra và bản tóm tắt môi trường nằm trong `outputs/setup/`; log cài thư viện nằm trong `.venv/setup-*.log`.
