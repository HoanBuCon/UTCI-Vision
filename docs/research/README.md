# Tài liệu nghiên cứu liên quan

> Tra cứu 11/11/2026 (từ khoá tiếng Anh). PDF lưu ở `docs/research/papers/` — **chỉ trên máy, không commit**
> (bản quyền + dung lượng ≈ 54 MB); tải lại bằng link bên dưới. Bài đánh dấu ★ được trích dẫn trong
> [04_BAO_CAO_DE_XUAT.md](../04_BAO_CAO_DE_XUAT.md).

## 1. Thị giác máy tính truyền thống cho biển báo

| # | Tài liệu | File local | Ý chính dùng cho dự án |
|---|---|---|---|
| ★1 | N. Dalal, B. Triggs. *Histograms of Oriented Gradients for Human Detection.* CVPR 2005. [PDF](https://lear.inrialpes.fr/people/triggs/pubs/Dalal-cvpr05.pdf) | `03_Dalal2005_HOG.pdf` | Định nghĩa HOG: histogram hướng gradient trên lưới ô, chuẩn hoá theo khối — đặc trưng truyền thống chính của bộ xác minh |
| ★2 | S. Houben et al. *Detection of Traffic Signs in Real-World Images: The German Traffic Sign Detection Benchmark.* IJCNN 2013. [PDF](https://www.ini.rub.de/upload/file/1470692848_e7f65a6c27d4c0ec0c71/HoubenEtAl_GTSDB_IJCNN2013.pdf) | `02_Houben2013_GTSDB_detection_benchmark.pdf` | Baseline phát hiện kinh điển: Viola-Jones (Haar), **HOG + LDA**, và thuật toán chuyên biệt dùng **màu + hình dạng** (Hough-like voting). Tách đánh giá phát hiện khỏi phân loại, đánh giá theo nhóm biển (cấm / nguy hiểm / hiệu lệnh) |
| ★3 | L. Vieira. *Comparing Performance of Preprocessing Techniques for Traffic Sign Recognition Using a HOG-SVM.* arXiv 2504.09424, 2024. [PDF](https://arxiv.org/pdf/2504.09424) | `04_Preprocessing_HOG_SVM_TSR_2025.pdf` | HOG-SVM trên GTSRB: 89,65% → **91,25%** khi đổi tiền xử lý (YUV tốt nhất; có thử CLAHE). Mốc tham chiếu cho thí nghiệm HOG+SVM của nhóm |
| 4 | Stallkamp et al., GTSRB (2011/2012) — theo các nguồn thứ cấp: HOG + LDA ≈ **95,7%**, CNN tốt nhất ≈ 99,5–99,7% ([tổng hợp](https://idus.us.es/bitstream/11441/80679/1/NEUNET-D-17-00381.pdf)) | — | Khoảng cách điển hình giữa đặc trưng thủ công và CNN trên **ảnh crop lớn, rõ** (GTSRB) |
| 5 | *Fast Traffic Sign Recognition Using Color Segmentation and Deep Convolutional Networks.* ACIVS 2016. [link](https://www.researchgate.net/publication/309328175) | — | Phân đoạn màu thu hẹp vùng tìm kiếm, **giảm dương tính giả** và thời gian tính trước khi CNN phân loại |
| 6 | *A novel traffic sign detection method via color segmentation and robust shape matching.* Neurocomputing 2015. [link](https://www.sciencedirect.com/science/article/abs/pii/S0925231215006712) | — | Bất biến màu + PHOG + SVM giảm tỉ lệ dương tính giả |
| 7 | *Traffic Sign Classification using Hybrid HOG-SURF Features and CNN.* 2019. [PDF](https://www.scitepress.org/Papers/2019/73925/73925.pdf) | — | Kết hợp HOG/SURF với CNN: 98,48% GTSRB với 1,5M tham số — đặc trưng thủ công bổ trợ được cho học sâu |

## 2. Học sâu & biển nhỏ

| # | Tài liệu | File local | Ý chính |
|---|---|---|---|
| ★8 | R. Sapkota et al. *YOLO advances to its genesis: a decadal and comprehensive review of the You Only Look Once (YOLO) series.* Artificial Intelligence Review 58:274, 2025 (arXiv 2406.19407). [PDF](https://arxiv.org/pdf/2406.19407) | `12_YOLO_review_decadal_2024.pdf` | Tổng quan YOLOv1 → YOLOv12 (gồm YOLO11) và ứng dụng giao thông — chương lý thuyết |
| ★9 | F. C. Akyon et al. *Slicing Aided Hyper Inference and Fine-tuning for Small Object Detection.* ICIP 2022. [PDF](https://arxiv.org/pdf/2202.06934) | `01_Akyon2022_SAHI_small_object.pdf` | Suy luận cắt lát tăng AP +5–7%, cộng fine-tune trên lát cắt +12–15% AP cho vật thể nhỏ (VisDrone, xView) |
| 10 | *A Small Object Detection Algorithm for Traffic Signs Based on Improved YOLOv7.* Sensors 2023. [link](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10459082/) | — | Thêm lớp phát hiện vật thể nhỏ ở neck cho TT100K (đa số biển nhỏ) |
| 11 | *STC-YOLO: Small Object Detection Network for Traffic Signs in Complex Environments.* Sensors 2023. [link](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10255978/) | — | +9,3% mAP so với YOLOv5 trên TT100K |
| 12 | *ESA-YOLO: scale-aware traffic sign detection based on YOLOv11 under adverse weather.* PLOS ONE 2025. [link](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12617897/) | — | YOLO11n cải tiến: +3,8% mAP@50 trên TT100K, ít hơn 20% tham số |
| 13 | *YOLO-CCA: A Context-Based Approach for Traffic Sign Detection.* arXiv 2412.04289, 2024. [PDF](https://arxiv.org/pdf/2412.04289) | `07_YOLO-CCA_context_traffic_sign_2024.pdf` | Dùng ngữ cảnh xung quanh biển để giảm nhầm lẫn |
| 14 | Zalo AI Challenge 2020 — Traffic Sign Detection: RetinaNet + **image tiling** ([repo](https://github.com/ptran1203/traffic_sign_detection), [dataset](https://datasetninja.com/zalo-traffic-sign)) | — | Ảnh 1622×626 từ Street View, biển rất nhỏ; cắt ô là giải pháp chủ đạo. **Một phần dataset của dự án có nguồn từ đây** (độ phân giải 1622×626 chiếm 41% ảnh) |

## 3. Biển báo Việt Nam

| # | Tài liệu | File local | Ý chính |
|---|---|---|---|
| ★15 | P. X. Tung et al. *Research and Development of a Traffic Sign Recognition Module in Vietnam.* ETASR 14(1), 2024. [PDF](https://etasr.com/index.php/ETASR/article/download/6658/3428/24748) | `09_Tung2024_ETASR_Vietnam_TSR_YOLOv5.pdf` | YOLOv5 rút gọn (MobileNet) chạy Jetson; dataset tự thu ngoài đường. Nhận xét: mô hình train trên GTSRB **không chuyển được** sang biển Việt Nam; phương pháp truyền thống nhanh nhưng kém chính xác khi ánh sáng / góc nhìn / che khuất thay đổi |
| ★16 | T. T. A. Cu et al. *Detection of Vietnamese Traffic Danger and Warning Signs via Deep Learning.* JESTEC 19(1), 2024. [PDF](https://jestec.taylors.edu.my/Vol%2019%20Issue%201%20February%20%202024/19_1_10.pdf) | `10_JESTEC2024_Vietnam_warning_signs_YOLOv5.pdf` | > 11 138 ảnh, 10 lớp biển nguy hiểm; YOLOv5 > 98% "accuracy" (chỉ số và cách chia khác dự án — không so sánh trực tiếp) |
| 17 | *Vietnamese Traffic Sign Recognition Using Deep Learning.* ICIIT 2024. [link](https://dl.acm.org/doi/fullHtml/10.1145/3654522.3654528) | — | Dataset 46 lớp, so sánh họ YOLO với Faster R-CNN |
| 18 | Repo tham khảo [Secret350/Real-time-Traffic-Objects-Detection](https://github.com/Secret350/Real-time-Traffic-Objects-Detection) | — | Cùng nguồn dataset; mAP@50 0,78 trên split gốc của Roboflow |

## 4. Tổng quát hoá, ít dữ liệu, theo vết

| # | Tài liệu | File local | Ý chính |
|---|---|---|---|
| ★19 | C. Ertler et al. *The Mapillary Traffic Sign Dataset for Detection and Classification on a Global Scale.* ECCV 2020. [PDF](https://arxiv.org/pdf/1909.04422) | `05_Ertler2020_Mapillary_Traffic_Sign_Dataset.pdf` | Có lớp **`other-sign`** cho biển ngoài danh mục — tiền lệ cho lớp "Biển báo khác" (ADR-009); đánh giá theo kích thước biển |
| ★20 | *TSCLIP: Robust CLIP Fine-Tuning for Worldwide Cross-Regional Traffic Sign Recognition.* arXiv 2409.15077, 2024. [PDF](https://arxiv.org/pdf/2409.15077) | `08_TSCLIP_cross_regional_TSR_2024.pdf` | Mô hình đạt tốt trên dữ liệu huấn luyện thường **giảm mạnh ở vùng / bối cảnh mới** — khớp phát hiện của nhóm (precision 0,75 trên cảnh ít giống train) |
| 21 | *FUSED-Net: Detecting Traffic Signs with Limited Data.* arXiv 2409.14852, 2024. [PDF](https://arxiv.org/pdf/2409.14852) | `13_FUSED-Net_limited_data_TSD_2024.pdf` | Phát hiện biển khi ít mẫu (few-shot) — hướng tham khảo cho lớp hiếm |
| ★22 | A. Bewley et al. *Simple Online and Realtime Tracking (SORT).* ICIP 2016. [PDF](https://arxiv.org/pdf/1602.00763) | `06_Bewley2016_SORT.pdf` | Kalman + ghép IoU (Hungarian) — cơ sở cho `tracking.py` |
| 23 | S. Šegvić et al. *Exploiting temporal and spatial constraints in traffic sign detection from a moving vehicle.* MVA 2014. [link](https://www.bib.irb.hr/587014) | — | Recall cao dễ đạt, **precision mới khó**; tăng precision bằng chuỗi theo vết + **giai đoạn phân biệt (verification) riêng** — đúng kiến trúc YOLO → tracking → bộ xác minh |
| ★24 | G. Ke et al. *LightGBM: A Highly Efficient Gradient Boosting Decision Tree.* NeurIPS 2017. [PDF](https://proceedings.neurips.cc/paper_files/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf) | `11_Ke2017_LightGBM.pdf` | Bộ phân loại của bộ xác minh |

## Lưu ý khi trích dẫn
- Số liệu của các bài khác dataset, cách chia và chỉ số (accuracy phân loại ≠ mAP phát hiện) — **không so sánh trực tiếp** với kết quả của nhóm; chỉ dùng làm bối cảnh.
- Một số nguồn (preprint, ResearchGate) chưa qua bình duyệt; ưu tiên trích bài ★ đã đọc bản PDF.
