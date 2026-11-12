# Tài liệu tham khảo dùng trong báo cáo cuối kỳ — đã xác thực

> Kiểm tra ngày 12–13/11/2026 bằng tra cứu web: mỗi mục được đối chiếu tác giả, tên bài, nơi đăng, năm, trang và DOI với
> ít nhất một nguồn chính thức (nhà xuất bản, DOI, CVF Open Access, arXiv, trang tác giả) hoặc chỉ mục thư mục độc lập.
> Khoá BibTeX tương ứng trong `BaoCao/Nhom07/references.bib`. Mục chưa xác minh được DOI thì **không ghi DOI** (chỉ ghi
> URL của nhà xuất bản). Danh mục rộng hơn (24 tài liệu, có chú giải) ở [README.md](README.md).

## Trạng thái

| Ký hiệu | Nghĩa |
|---|---|
| ✅ | Khớp đủ: tác giả, nơi đăng, năm, trang và DOI |
| ☑️ | Khớp nơi đăng và năm; DOI không có hoặc chưa xác minh — chỉ ghi URL nhà xuất bản |
| ⚠️ | Bản tiền ấn phẩm (arXiv), chưa bình duyệt — chỉ dùng làm bối cảnh |

## Danh mục

| Khoá | Tài liệu | Nơi đăng | DOI / nguồn | Trạng thái | Dùng ở |
|---|---|---|---|---|---|
| `stallkamp2012gtsrb` | Stallkamp, Schlipsing, Salmen, Igel — Man vs. computer: benchmarking ML algorithms for traffic sign recognition | Neural Networks 32: 323–332, 2012 | 10.1016/j.neunet.2012.02.016 | ✅ | Ch1 §1.6 |
| `houben2013gtsdb` | Houben et al. — Detection of traffic signs in real-world images: GTSDB | IJCNN 2013 | 10.1109/IJCNN.2013.6706807 | ✅ | Ch1, Ch3 (E8) |
| `zhu2016tt100k` | Zhu, Liang, Zhang, Huang, Li, Hu — Traffic-sign detection and classification in the wild | CVPR 2016, pp. 2110–2118 | CVF Open Access | ☑️ | Ch1, Ch2 |
| `escalera1997road` | de la Escalera, Moreno, Salichs, Armingol — Road traffic sign detection and classification | IEEE Trans. Industrial Electronics 44(6): 848–859, 1997 | 10.1109/41.649946 | ✅ | Ch1, Ch2 |
| `maldonado2007svm` | Maldonado-Bascón et al. — Road-sign detection and recognition based on SVMs | IEEE T-ITS 8(2): 264–278, 2007 | 10.1109/TITS.2007.895311 | ✅ | Ch1, Ch2 |
| `segvic2014temporal` | Šegvić, Brkić, Kalafatić, Pinz — Exploiting temporal and spatial constraints in TSD from a moving vehicle | Machine Vision and Applications 25(3): 649–665, 2014 | 10.1007/s00138-011-0396-y | ✅ | Ch1, Ch2 |
| `vieira2025hogsvm` | Vieira — Comparing preprocessing techniques for TSR using a HOG-SVM (89,65% → 91,25% với YUV) | arXiv 2504.09424, 2025 | arXiv | ⚠️ | Ch1, Ch3 |
| `tung2024vietnam` | Pham X. T., Nguyen L. T., Pham V. B. N. — Research and development of a TSR module in Vietnam | ETASR 14(1): 12740–12744, 2024 | etasr.com/…/6658 (DOI chưa xác minh) | ☑️ | Mở đầu, Ch1 |
| `cu2024vietnamese` | Cu T. T. A. et al. — Detection of Vietnamese traffic danger and warning signs via deep learning | JESTEC 19(1): 133–145, 2024 | jestec.taylors.edu.my (PDF) | ☑️ | Mở đầu, Ch1 |
| `sapkota2025yolo` | Sapkota et al. — YOLO advances to its genesis: a decadal and comprehensive review | Artificial Intelligence Review 58(9): 274, 2025 | 10.1007/s10462-025-11253-3 | ✅ | Ch1 |
| `khanam2024yolo11` | Khanam, Hussain — YOLOv11: an overview of the key architectural enhancements | arXiv 2410.17725, 2024 | arXiv | ⚠️ | Ch1, Ch2 |
| `ultralytics_yolo11` | Jocher, Qiu — Ultralytics YOLO11, v11.0.0 | Phần mềm, 2024 | github.com/ultralytics/ultralytics (theo trích dẫn chính thức) | ☑️ | Ch2 |
| `akyon2022sahi` | Akyon, Altinuc, Temizel — Slicing aided hyper inference and fine-tuning for small object detection | ICIP 2022, pp. 966–970 | 10.1109/ICIP46576.2022.9897990 | ✅ | Ch1, Ch2, Ch3 (T3) |
| `lin2014coco` | Lin et al. — Microsoft COCO: common objects in context | ECCV 2014, LNCS 8693: 740–755 | 10.1007/978-3-319-10602-1_48 | ✅ | Ch1, Ch2 |
| `redmon2016yolo` | Redmon, Divvala, Girshick, Farhadi — You only look once | CVPR 2016, pp. 779–788 | 10.1109/CVPR.2016.91 | ✅ | Ch1 |
| `ren2015faster` | Ren, He, Girshick, Sun — Faster R-CNN | IEEE TPAMI 39(6): 1137–1149, 2017 | 10.1109/TPAMI.2016.2577031 | ✅ | Ch1 |
| `ertler2020mapillary` | Ertler et al. — The Mapillary traffic sign dataset | ECCV 2020 (LNCS) | 10.1007/978-3-030-58592-1_5 | ✅ | Mở đầu, Ch1, Ch2 |
| `bewley2016sort` | Bewley, Ge, Ott, Ramos, Upcroft — Simple online and realtime tracking | ICIP 2016, pp. 3464–3468 | 10.1109/ICIP.2016.7533003 | ✅ | Ch1, Ch2 |
| `kalman1960filter` | Kalman — A new approach to linear filtering and prediction problems | J. Basic Engineering 82(1): 35–45, 1960 | 10.1115/1.3662552 | ✅ | Ch1, Ch2 |
| `kuhn1955hungarian` | Kuhn — The Hungarian method for the assignment problem | Naval Research Logistics Quarterly 2(1–2): 83–97, 1955 | 10.1002/nav.3800020109 (không nhầm bản in lại 2005) | ✅ | Ch1, Ch2 |
| `dalal2005hog` | Dalal, Triggs — Histograms of oriented gradients for human detection | CVPR 2005, pp. 886–893 | 10.1109/CVPR.2005.177 | ✅ | Ch1, Ch2 |
| `lowe2004sift` | Lowe — Distinctive image features from scale-invariant keypoints | IJCV 60(2): 91–110, 2004 | 10.1023/B:VISI.0000029664.99615.94 | ✅ | Ch1, Ch2 |
| `csurka2004bovw` | Csurka, Dance, Fan, Willamowski, Bray — Visual categorization with bags of keypoints | ECCV Workshop on Statistical Learning in CV, 2004 | (không có DOI) | ☑️ | Ch1, Ch2 |
| `cortes1995svm` | Cortes, Vapnik — Support-vector networks | Machine Learning 20(3): 273–297, 1995 | 10.1007/BF00994018 | ✅ | Ch1, Ch2 |
| `hu1962moments` | Hu — Visual pattern recognition by moment invariants | IRE Trans. Information Theory 8(2): 179–187, 1962 | 10.1109/TIT.1962.1057692 | ✅ | Ch1, Ch2 |
| `zuiderveld1994clahe` | Zuiderveld — Contrast limited adaptive histogram equalization | Graphics Gems IV, pp. 474–485, Academic Press, 1994 | (sách, không có DOI) | ☑️ | Ch1, Ch2 |
| `tomasi1998bilateral` | Tomasi, Manduchi — Bilateral filtering for gray and color images | ICCV 1998, pp. 839–846 | 10.1109/ICCV.1998.710815 | ✅ | Ch1, Ch2 |
| `ke2017lightgbm` | Ke et al. — LightGBM: a highly efficient gradient boosting decision tree | NIPS 2017, pp. 3146–3154 | proceedings.neurips.cc | ☑️ | Ch1, Ch2 |
| `wilson1927` | Wilson — Probable inference, the law of succession, and statistical inference | JASA 22(158): 209–212, 1927 | 10.2307/2276774 (JSTOR) | ✅ | Ch2 |
| `efron1993bootstrap` | Efron, Tibshirani — An Introduction to the Bootstrap | Chapman & Hall, 1993 | (sách) | ☑️ | Ch2 |
| `qcvn41_2019` | QCVN 41:2019/BGTVT — Quy chuẩn kỹ thuật quốc gia về báo hiệu đường bộ | Thông tư 54/2019/TT-BGTVT, hiệu lực 01/07/2020 | thuvienphapluat.vn | ☑️ | Ch2, Ch3 |
| `roboflow_dataset` | Bộ dữ liệu merge_Real-time Viet Nam Traffic Dtctn 2 (v1), CC BY 4.0 | Roboflow Universe | URL trong DATA_CARD | ☑️ | Ch2, Phụ lục |
| `zalo2020tsd` | Zalo AI Challenge 2020 — Traffic Sign Detection | Dataset Ninja | datasetninja.com/zalo-traffic-sign | ☑️ | Ch1, Ch2 |

## Phát hiện khi xác thực

- **QCVN 41:2019/BGTVT đã được thay thế** bởi QCVN 41:2024/BGTVT (Thông tư 51/2024/TT-BGTVT, hiệu lực 01/01/2025).
  Danh mục lớp và ý nghĩa biển của dự án theo bản 2019 → ghi ở mục Hạn chế của báo cáo; nên rà soát `configs/classes.yaml`.
- DOI dạng `10.48084/etasr.6658` của bài ETASR **chưa xác minh được** qua tra cứu → báo cáo chỉ ghi URL bài trên trang tạp chí.
- `ren2015faster`, `redmon2016yolo`, `ertler2020mapillary`, `bewley2016sort` trước đây trích bản arXiv → đã đổi sang bản xuất bản
  chính thức (TPAMI 2017, CVPR 2016, ECCV 2020, ICIP 2016).
- Số liệu của các bài được trích (SAHI +5,1–6,8 AP khi suy luận, 12,7–14,5 khi tinh chỉnh; SORT ≈ 260 Hz; GTSDB 900 ảnh;
  TT100K 100 nghìn ảnh / 30 nghìn biển; HOG-SVM 89,65% → 91,25%) được đối chiếu với tóm tắt / bản PDF của chính bài đó.

## Nguồn tra cứu chính
DOI.org và trang nhà xuất bản (IEEE, Springer, Elsevier, Wiley, ASME, JSTOR), CVF Open Access, arXiv, ECVA, dblp, OpenAlex,
trang tác giả (UBC, RUB INI), etasr.com, jestec.taylors.edu.my, docs.ultralytics.com, thuvienphapluat.vn.
