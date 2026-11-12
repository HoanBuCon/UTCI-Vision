# Nguồn phương pháp cho bộ hình Chương 1

Các sơ đồ học máy, OCR và demo màu/hình thái được nhóm tự vẽ hoặc sinh từ ảnh tổng hợp. Hình quan hệ AI, hình CNN và hình nhận diện biển báo dùng các tệp người biên soạn cung cấp trong `figures`.

- AI, ML, DL: Goodfellow, Bengio, Courville, *Deep Learning*, Chương 1, Hình 1.4: https://www.deeplearningbook.org/contents/intro.html
- Các hình thức học: Google, *What is Machine Learning?*: https://developers.google.com/machine-learning/intro-to-ml/what-is-ml
- Học bán giám sát: Google Cloud, *What is Machine Learning? Types and uses*: https://cloud.google.com/learn/what-is-machine-learning
- CNN: Stanford CS231n, *Convolutional Neural Networks*: https://cs231n.github.io/convolutional-networks/
- Không gian màu: OpenCV, *Color conversions*: https://docs.opencv.org/4.13.0/de/d25/imgproc_color_conversions.html
- Hình thái học: OpenCV, *Morphological Transformations*: https://docs.opencv.org/4.13.0/d9/d61/tutorial_py_morphological_ops.html
- Đặc trưng hình dạng: OpenCV, *Contour Features*: https://docs.opencv.org/4.13.0/dd/d49/tutorial_py_contour_features.html
- OCR tổng quát: tài liệu chính thức PaddleOCR, *Overview*: https://paddlepaddle.github.io/PaddleOCR/v2.10.0/en/ppocr/overview.html

## Các ảnh được cung cấp

- `sodoquanhe.jpg`: nội dung thực tế là PNG, 685×685 pixel. Bản `.png` giữ nguyên nội dung và kích thước để XeLaTeX đọc đúng định dạng. Dùng tại mục 1.1.2, thay sơ đồ elip tự vẽ trước đó; chưa xác minh tác giả gốc nên chú thích ghi ảnh do người biên soạn cung cấp.

- `Thuat-toan-CNN-co-cau-truc-nhu-the-nao.jpg`: nội dung thực tế là WebP, 708×353 pixel. Bản `.png` được chuyển định dạng bằng Pillow, giữ nguyên kích thước và nội dung, để XeLaTeX đọc được. Trang có đăng hình tương ứng: https://interdata.vn/blog/convolutional-neural-network-la-gi/ (liên kết ảnh: https://interdata.vn/blog/wp-content/uploads/2025/03/Thuat-toan-CNN-co-cau-truc-nhu-the-nao.webp). Đây là nguồn đăng lại, chưa xác minh tác giả gốc; lý thuyết CNN và bảng so sánh vẫn dựa vào Stanford CS231n và sách *Deep Learning*.
- `anhnhandien.svg`: sơ đồ draw.io do người biên soạn cung cấp, có ảnh raster nhúng sẵn. Bản `.pdf` được xuất bằng Chrome headless với khổ trang 1110×575 px, lề 0, giữ cả chữ trong `foreignObject`; không thay các ảnh hay nhãn bên trong. Chưa xác minh nguồn gốc các ảnh nhúng, nên không gán nguồn bên ngoài cho sơ đồ.

## Cách sinh lại

1. Chạy `python figures/source/generate_demos.py` từ thư mục Nhom07 (chỉ dùng thư viện chuẩn).
2. Chạy `figures/source/build_figures.ps1` để tạo SVG và PDF vector.

Demo màu dùng sRGB/D65. Các kênh RGB, HSV và Lab được chuẩn hoá về [0,1] để hiển thị bằng thang xám; đây không phải ảnh màu HSV/Lab được hiển thị như RGB.

Demo hình thái dùng ảnh nhị phân tổng hợp với tiền cảnh trắng, kernel vuông 3×3 và nền ngoài bằng 0. Co, giãn, mở, đóng được tính từ dữ liệu ảnh; script kiểm tra quan hệ tập hợp và tính lũy đẳng của phép mở. Các hình học phía dưới minh hoạ biên, khung bao và tâm, không phải kết quả benchmark.

Các elip đồng tâm biểu diễn DL nằm trong ML, ML nằm trong AI. Các nét đứt chỉ mối liên hệ với ứng dụng thị giác máy tính, không biểu diễn quan hệ tập con mới. Sơ đồ học máy thể hiện bốn hình thức thường gặp, không khẳng định đây là danh sách đầy đủ mọi cách phân loại. Sơ đồ OCR thể hiện các bước tổng quát, không khẳng định VietOCR tự phát hiện vùng chữ.
