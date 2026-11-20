# TỔNG HỢP DỰ ÁN UTCI-VISION — Học, trình bày và bảo vệ

**Đề tài:** Hệ thống nhận diện biển báo giao thông (UTCI-Vision) · **Học phần:** Thị giác máy tính, ICTU · **Nhóm 7**
**Giảng viên hướng dẫn:** TS. Nguyễn Thị Thanh Nhàn · **Ngày tổng hợp:** 20/11/2026
**Dùng cho:** (1) các bài kiểm tra thường xuyên còn lại, (2) buổi bảo vệ cuối kỳ (Sprint 6, dự kiến tuần 27/11–04/12/2026).

> **Tiêu chí của tài liệu này:** đọc xong, **cả 5 thành viên biết và hiểu như nhau**, nói cùng một con số, cùng một cách giải thích,
> cùng một giới hạn. Ai cũng phải trả lời được mọi câu hỏi, không chỉ phần mình làm.

Đây là tài liệu học nội bộ để trên máy (đã thêm vào `.gitignore`), **không phải** một chương báo cáo và **không thay** `BaoCao/Nhom07/guide.md`.
`guide.md` vẫn là tài liệu đi sâu cho bài kiểm tra 2 (từng công thức, từng tiêu chí); file này là bản **tổng hợp toàn dự án + bảo vệ cuối kỳ**.
Mọi con số dưới đây lấy từ báo cáo LaTeX `BaoCao/Nhom07` và các hồ sơ `docs/danh_gia/*`; không có số nào được chạy mới.

---

## Mục lục

0. [Meta-prompt đã dùng](#0-meta-prompt-đã-dùng)
1. [Cách dùng tài liệu và lộ trình học](#1-cách-dùng-tài-liệu-và-lộ-trình-học)
2. [Dự án trong một trang](#2-dự-án-trong-một-trang)
3. [Nhóm, vai trò và lịch sử dự án](#3-nhóm-vai-trò-và-lịch-sử-dự-án)
4. [Bài toán, mục tiêu, phạm vi](#4-bài-toán-mục-tiêu-phạm-vi)
5. [Dữ liệu](#5-dữ-liệu)
6. [Kiến trúc hệ thống và từng khâu](#6-kiến-trúc-hệ-thống-và-từng-khâu)
7. [Huấn luyện, giao thức đánh giá và độ đo](#7-huấn-luyện-giao-thức-đánh-giá-và-độ-đo)
8. [Thực nghiệm và kết quả](#8-thực-nghiệm-và-kết-quả)
9. [Phần mềm: mã nguồn, API, web, Docker](#9-phần-mềm-mã-nguồn-api-web-docker)
10. [Báo cáo LaTeX: cấu trúc và cách biên dịch](#10-báo-cáo-latex-cấu-trúc-và-cách-biên-dịch)
11. [Hạn chế và hướng phát triển](#11-hạn-chế-và-hướng-phát-triển)
12. [Những điểm phải thống nhất trước khi nói](#12-những-điểm-phải-thống-nhất-trước-khi-nói)
13. [Trình bày: bài kiểm tra thường xuyên](#13-trình-bày-bài-kiểm-tra-thường-xuyên)
14. [Trình bày: bảo vệ cuối kỳ — slide, phân vai, kịch bản, demo](#14-trình-bày-bảo-vệ-cuối-kỳ--slide-phân-vai-kịch-bản-demo)
15. [Bảo vệ: nguyên tắc trả lời và bộ câu hỏi](#15-bảo-vệ-nguyên-tắc-trả-lời-và-bộ-câu-hỏi)
16. [Lịch luyện tập và phiếu tự kiểm tra](#16-lịch-luyện-tập-và-phiếu-tự-kiểm-tra)
17. [Bảng tra nguồn nhanh](#17-bảng-tra-nguồn-nhanh)
18. [Lý thuyết nền — tóm tắt Chương 1](#18-lý-thuyết-nền--tóm-tắt-chương-1)
19. [Nghiên cứu liên quan — tóm tắt §1.6](#19-nghiên-cứu-liên-quan--tóm-tắt-16)
20. [Bản đồ hình và bảng trong báo cáo](#20-bản-đồ-hình-và-bảng-trong-báo-cáo)
21. [Bảng viết tắt](#21-bảng-viết-tắt)

> **Đọc file này là đủ để bảo vệ, không cần đọc lại báo cáo.** Mọi nội dung có thể bị hỏi trong báo cáo (lý thuyết Chương 1,
> nghiên cứu liên quan, phương pháp, kết quả, từng hình/bảng theo số thứ tự) đã được tóm lại ở đây. Chỉ mở PDF khi cần chỉ hình lúc trình bày.

---

## 0. Meta-prompt đã dùng

```text
Vai trò: bạn là trưởng nhóm kỹ thuật kiêm người phản biện của đồ án môn Thị giác máy tính (ICTU),
viết cho các thành viên mới học CV.

Nhiệm vụ: đọc đầy đủ thư mục D:\UTCI-Vision — README, docs/ (phương án, techstack, SRS, sprint plan,
báo cáo đề xuất, ADR, đánh giá S1/S3, data card, bàn giao, research), báo cáo LaTeX BaoCao/Nhom07
(mở đầu, chương 1–3, kết luận, phụ lục, phân công, guide.md), configs/, src/utci_vision/ và web/.
Viết MỘT file markdown tổng hợp ở gốc dự án: TONG_HOP_DU_AN.md, thêm vào .gitignore.
Không tạo handover, không sửa báo cáo, không sửa guide.md, không chạy lại huấn luyện/đánh giá.

Mục đích: dùng cho cả bài kiểm tra thường xuyên và bảo vệ cuối kỳ. Tiêu chí: mọi thành viên
biết và hiểu như nhau.

Nội dung bắt buộc:
- Dự án trong một trang; câu giới thiệu 30 giây và 2 phút.
- Nhóm, vai trò TV1–TV5 theo tên, lịch sử sprint, quyết định đã chốt.
- Bài toán, mục tiêu M1–M4, phạm vi; các con số phải thuộc.
- Dữ liệu: nguồn, nhãn, audit, pHash, gộp lớp 32→27, chia cụm, EDA.
- Từng khâu theo khung: vấn đề → đầu vào → làm gì → đầu ra → bằng chứng → giới hạn.
- Huấn luyện, giao thức đánh giá, độ đo có ví dụ tính tay.
- Mọi thí nghiệm (S1, T0/T1, T3, T4/E4, E8, E1/E2, OCR, tốc độ) kèm điều kiện đo và câu được phép nói.
- Phần mềm (mã, API, web, Docker, cổng, lệnh), báo cáo LaTeX (cấu trúc, biên dịch).
- Hạn chế, hướng phát triển; danh sách điểm chưa khớp giữa các tài liệu.
- Trình bày: kiểm tra thường xuyên (tóm 10 tiêu chí) và bảo vệ cuối kỳ (15–20 slide,
  phân vai theo tên nhưng ai cũng học đủ, lời nói mẫu, demo từng bước, phương án dự phòng).
- Bộ câu hỏi phản biện có đáp án; lịch luyện tập đến 04/12; phiếu tự kiểm tra.

Quy tắc: không bịa số; mọi số kèm tập, ngưỡng, kích thước, phần cứng. Phân biệt detection với
classification crop, mAP với accuracy, confidence với độ chính xác, thời gian detector với đầu cuối,
32 lớp gốc / 27 lớp mô hình / 28 lớp nội bộ SVM. LightGBM, SVM là ML, không phải DL.
Không khẳng định OCR/tracking đã được đo định lượng. Chỗ nào tài liệu mâu thuẫn: ghi nguồn,
ghi mức chắc chắn, đề xuất cách nói an toàn. Văn phong tiếng Việt dễ hiểu, từng bước.
```

Phần còn lại là kết quả thực hiện meta-prompt này.

---

## 1. Cách dùng tài liệu và lộ trình học

**Nguyên tắc học:** với mỗi khâu của hệ thống, ai cũng phải nói được **6 câu**:
*Giải quyết vấn đề gì? → Nhận gì? → Làm gì? → Trả gì? → Bằng chứng nào cho thấy nó có ích? → Giới hạn là gì?*
Đó cũng là thứ tự trả lời khi giảng viên hỏi sâu.

**Lộ trình cho người chưa làm phần kỹ thuật (khoảng 4 buổi, mỗi buổi 1,5–2 giờ):**

| Buổi | Đọc mục | Kết quả cần đạt |
|---|---|---|
| 1 | §2, §4, §5, §18 | Nói được đề tài trong 30 giây; giải thích 32 → 27 lớp và vì sao chia theo cụm; nắm lý thuyết nền |
| 2 | §6, §7, §19 | Tự vẽ lại pipeline chính và pipeline đối chứng; tự tính P/R/F1 từ ví dụ; biết công trình nào làm nền cho khâu nào |
| 3 | §8, §11, §12, §20 | Thuộc bảng "con số phải nhớ"; nói được điều kiện đo của mỗi số; giải thích được từng hình/bảng theo số thứ tự |
| 4 | §13–§16 | Tập slide phần mình, trả lời ngẫu nhiên 10 câu ở §15 (gồm cả nhóm D lý thuyết) |

**Người đã làm kỹ thuật** vẫn đọc §2, §7, §8, §12, §15: người làm OCR phải biết vì sao chưa có CER; người làm web phải biết
confidence không phải độ chính xác; người huấn luyện phải nói được CV truyền thống đóng góp gì.

Các công thức cần biết (Gamma, CLAHE, HOG 324 chiều, IoU, mAP, CI, tích chập, PCA, pHash…) đều có trong §6, §7 và §18.
`BaoCao/Nhom07/guide.md` chỉ là tài liệu tham khảo thêm, không bắt buộc đọc.

---

## 2. Dự án trong một trang

### 2.1. Thông tin chung

| Mục | Giá trị |
|---|---|
| Tên đề tài | Hệ thống nhận diện biển báo giao thông (tên dự án: UTCI-Vision) |
| Đầu vào | Ảnh tĩnh, video, webcam |
| Đầu ra | Khung bao + tên lớp (27 lớp) + điểm tin cậy; giá trị số (km/h, m) và chữ khi đủ rõ; mã theo vết với video; ý nghĩa và mã hiệu QCVN |
| Lõi học sâu | YOLO11s fine-tune từ COCO (phát hiện + phân loại), VietOCR pretrained (đọc chữ/số) |
| CV truyền thống | Đánh giá chất lượng + tăng cường thích nghi (Gamma, CLAHE, lọc song phương); theo vết Kalman + Hungarian; cắt vùng chữ; pipeline đối chứng HSV → hình thái học → contour/hình dạng → HOG + histogram HSV → SVM |
| Học máy (ML) | SVM (đối chứng), LightGBM (bộ xác minh, **tắt mặc định**) |
| Dữ liệu | Roboflow *merge_Real-time Viet Nam Traffic Dtctn 2*, CC BY 4.0 (gộp từ nguồn có Zalo AI 2020) |
| Phần mềm | FastAPI (REST + WebSocket) · React 19 + Vite + TypeScript · Docker Compose (CPU/GPU) · Nginx |
| Repo | https://github.com/HoanBuCon/UTCI-Vision · Trello: board "faketime-traffic-signs-cant-detect" |
| Báo cáo | `BaoCao/Nhom07/main.tex` → PDF khoảng 97 trang (lớp `ictureport.cls`, XeLaTeX + Biber) |

### 2.2. Câu giới thiệu 30 giây (ai cũng phải thuộc ý, không cần thuộc chữ)

> "Nhóm xây dựng hệ thống nhận diện biển báo giao thông Việt Nam từ ảnh, video và webcam. Lõi là YOLO11s fine-tune để tìm
> và phân loại 27 lớp biển; trước YOLO có bước đánh giá chất lượng và chỉ tăng cường ảnh khi cần; với video có theo vết
> Kalman; khi vùng đủ rõ thì đọc số bằng VietOCR. Song song, nhóm xây một hệ thống chỉ dùng CV truyền thống — màu, hình dạng,
> HOG và SVM — để so sánh trực tiếp hai hướng tiếp cận trên cùng tập kiểm thử."

### 2.3. Bản 2 phút (thêm kết quả)

Thêm vào sau bản 30 giây:

> "Dữ liệu khó vì hơn một nửa số biển có cạnh dưới 32 pixel. Nhóm chia dữ liệu theo cụm ảnh gần trùng để tập kiểm thử không chứa
> cảnh lặp của tập huấn luyện. Ba kết quả chính: suy luận ở 1280 px thay vì 960 px tăng recall biển dưới 16 px từ 0,634 lên 0,737 mà
> không giảm precision; tăng cường thích nghi tăng recall ảnh rất tối từ 0,686 lên 0,822 mà không làm hại ảnh nhiễu; ở khâu phân loại,
> HOG + màu + SVM đạt 91,0 % so với 92,4 % của YOLO, nghĩa là điểm yếu của CV truyền thống nằm ở khâu tìm biển. Bộ xác minh LightGBM
> không cải thiện thật nên tắt mặc định. Hệ thống mặc định đạt precision 0,862, recall 0,917 trên tập kiểm thử. OCR và theo vết
> chạy được nhưng chưa đo định lượng vì không có nhãn chữ và video thật."

### 2.4. Mười con số phải thuộc (kèm điều kiện)

| # | Con số | Điều kiện phải nói kèm |
|---|---|---|
| 1 | **32 → 27 lớp** | 26 lớp giữ riêng + 1 lớp gộp "Biển báo khác" (6 lớp có < 60 cụm cảnh) |
| 2 | **5.386 ảnh, 13.476 biển** | Sau lọc; chia 3.707 / 853 / 826 ảnh (train/val/test) |
| 3 | **53,7 % biển < 32 px; 18,3 % < 16 px** | Cạnh tương đương √(w·h) |
| 4 | **mAP@50 ≈ 0,89–0,91** | YOLO11s, 960 px, test; thư viện 0,905, nhóm tính lại 0,892 |
| 5 | **Recall < 16 px: 0,634 → 0,737** | T3, cùng trọng số, 960 → 1280 px, precision giữ 0,861 |
| 6 | **Recall ảnh rất tối: 0,686 → 0,822** | T4, ảnh làm tối giả lập γ 3,5, YOLO 960 px |
| 7 | **91,0 % vs 92,4 %** | E8, accuracy phân loại; HOG + màu + SVM được cho sẵn vị trí, YOLO phải tự tìm |
| 8 | **ΔP = +0,005, CI [−0,012; +0,022]** | T1, bộ xác minh ở cùng recall → không có ý nghĩa → tắt |
| 9 | **P 0,862 · R 0,917 · F1 0,889** | E1, cấu hình mặc định, test, ngưỡng 0,25, IoU 0,5 |
| 10 | **22,5 ms/ảnh** | RTX 4060 Laptop; chỉ gồm chất lượng + tăng cường + phát hiện, **không** gồm OCR |

---

## 3. Nhóm, vai trò và lịch sử dự án

### 3.1. Thành viên

| Mã | Thành viên | Vai trò chính (theo báo cáo, `frontmatter/phancong.tex`) |
|---|---|---|
| TV1 | **Trần Trọng Hoàn** (nhóm trưởng) | Tech lead, ML, đánh giá: kiến trúc, review; bộ xác minh LightGBM, hậu xử lý OCR; thiết kế và chạy thí nghiệm T0–T4, E1–E8; phân tích lỗi, phản biện |
| TV2 | **Nông Hữu Thịnh** | CV, frontend: tăng cường ảnh, đặc trưng vùng, tracking, cắt vùng OCR; React; kiểm tra độ ổn định video |
| TV3 | **Nguyễn Quang Minh** | Dev chính, DL, backend, DevOps: fine-tune YOLO11; notebook; pipeline, VietOCR, FastAPI, WebSocket; Docker, CI, tối ưu |
| TV4 | **Vũ Ngọc Quý** | Chủ trì báo cáo, slide, video, nội dung biển báo; cùng các thành viên đánh giá, kiểm thử, gán nhãn OCR |
| TV5 | **Trần Văn Dưỡng** | Dữ liệu và kiểm thử: audit, lọc, chia, đóng gói dữ liệu; video thử; benchmark; kiểm thử chấp nhận và hồi quy |

Khi giảng viên hỏi "em làm phần nào?", trả lời đúng bảng trên **và** nói được phần đó nối với phần khác ở đâu.
Không nhận công việc của người khác; không nói "phần đó bạn X làm nên em không biết".

### 3.2. Lịch sử theo sprint (sprint 1 tuần, chuyển vào thứ Sáu)

| Sprint | Thời gian | Kết quả chính |
|---|---|---|
| S1 | 23/10–30/10 | Repo, CI, Makefile, cổng custom; audit dữ liệu; 3 notebook; fine-tune baseline YOLO11s 960; chốt schema API; quyết định gộp lớp hiếm (ADR-009) |
| S2 | 30/10–06/11 | Dữ liệu v1 (lọc, pHash, chia cụm, đóng gói); fine-tune YOLO11s trên v1; tăng cường CV, tracking |
| S3 | 06/11–13/11 | Nghiên cứu 24 tài liệu, báo cáo đề xuất; T0/T1, E8, T4; pipeline đầy đủ, API ảnh/video/WebSocket; E1/E2/E4/T3; Docker offline; web UI mới |
| S4 | 13/11–20/11 | Báo cáo LaTeX cuối (viết lại Ch2, viết mới Ch3, Kết luận, Phụ lục; 68 tài liệu tham khảo; hình draw.io, biểu đồ sinh bằng script); guide bài kiểm tra 2 |
| S5 | 20/11–27/11 | (Kế hoạch) tối ưu, chốt trọng số, kiểm thử chấp nhận, hoàn thiện báo cáo |
| S6 | 27/11–04/12 | (Kế hoạch) sửa lỗi, tag v1.0, slide 15–20 trang, video demo 3–5 phút, diễn tập ≥ 2 lần, bảo vệ |

### 3.3. Các quyết định đã chốt (ai cũng phải biết lý do)

| # | Quyết định | Lý do |
|---|---|---|
| D1 | Dữ liệu đóng băng ở v1: không thêm ảnh, không gán lại nhãn | Yêu cầu phạm vi của nhóm; để mọi thí nghiệm so sánh được với nhau |
| D2 | CV truyền thống chính trong hệ thống = đánh giá chất lượng + tăng cường thích nghi, và theo vết Kalman | T4 cho thấy có ích với ảnh tối, không hại ảnh nhiễu |
| D3 | Bộ xác minh LightGBM là tùy chọn, **tắt mặc định** | T1: không hơn điểm YOLO ở cùng recall; E2: giảm recall biển nhỏ |
| D4 | Suy luận 1280 px (train 960 px) | T3: recall biển < 16 px tăng 10,3 điểm, precision giữ nguyên, chậm thêm khoảng 15 % |
| D5 | Cắt ô 640 chỉ là tùy chọn | T3: recall cao nhất nhưng precision 0,749, chậm 2,5 lần |
| D6 | HOG + màu + SVM là phương pháp đối chứng; SIFT-BoVW là đối chứng âm | E8 |
| D7 | VietOCR chạy offline; bỏ dòng có độ tin cậy < 0,75 | Docker không cần mạng; tránh trả chuỗi rác trên biển nhỏ |
| D8 | Gộp 6 lớp < 60 cụm cảnh → 27 lớp (ADR-009) | Lớp quá ít cảnh độc lập không đủ để học và đánh giá |
| D9 | Mọi cổng là cổng custom (API 18100, web 18080, Vite 15173, Jupyter 18888) — ADR-007 | Tránh xung đột với dịch vụ khác trên máy thành viên |
| D10 | Fine-tune chỉ bằng notebook (local / Colab / Kaggle), sinh từ một template — ADR-006 | Ai cũng chạy được trên GPU miễn phí, cùng một quy trình |

---

## 4. Bài toán, mục tiêu, phạm vi

### 4.1. Bài toán gồm ba nhiệm vụ

1. **Phát hiện (detection):** tìm vị trí biển trong cả cảnh bằng khung bao.
2. **Phân loại (classification):** gán tên lớp cho vùng biển đã tìm.
3. **Nhận dạng chữ/số (OCR):** đọc nội dung bên trong vùng biển khi đủ rõ.

Với video, thêm **theo vết (tracking)**: gắn cùng một mã cho các lần xuất hiện của một biển qua nhiều khung hình.

**Ví dụ phải nói được:** gặp biển giới hạn tốc độ → hệ thống trả khung bao, lớp "Giới hạn tốc độ", điểm tin cậy, rồi mới đọc "40"
và gắn "km/h". Tên lớp **không** cho biết con số; con số phải đọc từ ảnh. Nếu vùng số quá nhỏ thì vẫn trả lớp và khung bao, để trống giá trị.

Biểu diễn toán học (Chương 2, `eq:output_problem`): đầu ra tại thời điểm t là tập các bộ (khung bao b, lớp c, điểm s, mã vết k, thông tin bổ sung o).
Giá trị "chưa có" ký hiệu ⊥, khác với số 0. Với ảnh tĩnh, mã vết rỗng.

### 4.2. Khó khăn

- Biển ở xa rất nhỏ (53,7 % dưới 32 px).
- Ánh sáng yếu, mờ, nhiễu làm đổi màu và hình dạng; góc nghiêng làm biển tròn thành elip.
- Nhiều lớp chỉ khác nhau một ký hiệu nhỏ.
- Nền đường phố có áo, xe, quảng cáo cùng màu với biển.
- Dữ liệu mất cân bằng (chênh 22 lần giữa lớp nhiều nhất và ít nhất sau gộp).

### 4.3. Bốn mục tiêu (M1–M4) và kết quả

| Mục tiêu | Nội dung | Đạt được |
|---|---|---|
| M1 | Hệ thống hoàn chỉnh: ảnh, video, webcam → vị trí, lớp, giá trị số, ý nghĩa QCVN cho 27 lớp | Có: API + web + Docker chạy offline |
| M2 | Đánh giá riêng từng phương pháp, so sánh đặc trưng thủ công với học sâu | E8, T4, T1 (có cả kết quả âm) |
| M3 | Cải thiện biển nhỏ và ảnh tối mà không thêm dữ liệu | T3 (1280 px), T4 (tăng cường thích nghi) |
| M4 | Đánh giá đáng tin cậy, có CI, tái lập được | Chia cụm, ngưỡng vận hành, theo kích thước/lớp/mức tương đồng, bootstrap + Wilson, sổ đăng ký thí nghiệm |

**Định hướng học thuật:** xây dựng, giải thích và kiểm chứng một hệ thống kết hợp — **không** đề xuất kiến trúc mạng mới.

### 4.4. Phạm vi (nói sai phần này là mất điểm nhanh nhất)

- 27 lớp mô hình. "Biển báo khác" là **lớp gộp có dữ liệu huấn luyện cụ thể**, không phải bộ nhận diện mọi biển lạ.
- Đọc số: **tốc độ (km/h)** và **chiều cao (m)**. Giới hạn **trọng lượng (T) không thuộc phạm vi** vì lớp này đã bị gộp (README ghi "km/h, m, T" là chưa cập nhật — xem §12).
- Biển phụ chưa phải lớp phát hiện riêng; được tìm bằng xử lý ảnh ngay dưới biển chính.
- Không có nhãn chữ → OCR chỉ đánh giá định tính. Không có video đường phố thật → chưa đo độ ổn định theo vết.
- Không xử lý đèn tín hiệu, vạch kẻ đường, điều khiển xe.
- Danh mục theo **QCVN 41:2019/BGTVT**; quy chuẩn này đã được thay bằng **QCVN 41:2024/BGTVT từ 01/01/2025** → đã ghi trong Hạn chế.

### 4.5. 27 lớp (theo `configs/classes.yaml`)

Năm nhóm biển (siêu lớp): **Biển cấm** (đỏ, tròn), **Biển nguy hiểm** (vàng, tam giác), **Biển hiệu lệnh** (xanh, tròn),
**Biển chỉ dẫn** (xanh, chữ nhật), **Biển báo khác** (lớp gộp).

| Nhóm | Các lớp |
|---|---|
| Biển cấm | Biển cấm phương tiện · Cấm đi ngược chiều · Cấm đỗ xe · Cấm dừng và đỗ xe · Cấm quay đầu · Cấm rẽ phải · Cấm rẽ trái · Giới hạn chiều cao (đọc số, m) · Giới hạn tốc độ (đọc số, km/h) |
| Biển nguy hiểm | Chỗ ngoặt nguy hiểm · Chú ý chướng ngại vật · Đi chậm · Đường bị thu hẹp · Đường giao nhau · Đường người đi bộ cắt ngang · Giao nhau với đường không ưu tiên · Gồ giảm tốc phía trước · Trẻ em |
| Biển hiệu lệnh | Biển gộp làn đường theo phương tiện · Nơi giao nhau chạy theo vòng xuyến · Phải đi vòng sang bên phải |
| Biển chỉ dẫn | Bến xe buýt · Biển chỉ dẫn hướng đi · Chỗ quay xe · Đường một chiều · Vạch sang đường cho người đi bộ |
| Khác (gộp 6 lớp) | Cấm đi thẳng và rẽ phải · Cấm rẽ trái và phải · Cấm rẽ trái và quay đầu xe · Giao nhau với đường sắt có rào chắn · Giới hạn trọng lượng · Kiểm tra |

---

## 5. Dữ liệu

### 5.1. Nguồn — nói đúng đóng góp của nhóm

- Bộ dữ liệu có sẵn trên Roboflow Universe: *merge_Real-time Viet Nam Traffic Dtctn 2* (phiên bản 1, xuất 21/10/2026), **CC BY 4.0**.
- Gộp từ nhiều nguồn, trong đó có ảnh Zalo AI Challenge 2020 (ảnh 1622×626).
- **Nhóm không tự quay ảnh, không tự gán toàn bộ nhãn.** Đóng góp của nhóm: kiểm tra, lọc, gom cụm gần trùng, ánh xạ lớp, chia lại, đóng gói, phân tích EDA.

### 5.2. Nhãn YOLO

Mỗi dòng: `class_id x_c/W y_c/H w/W h/H` (tọa độ tâm và kích thước, chuẩn hóa theo ảnh).
Ví dụ ảnh 1000×500, dòng `20 0.5 0.4 0.1 0.2` → lớp id 20, tâm (500, 200), khung 100×100 px.
Nhãn detection (lớp + khung) **không đủ** cho OCR (cần bản chép chữ) và tracking (cần video liên tục có định danh).

### 5.3. Năm bước chuẩn bị (Hình `fig:data_flow`)

| Bước | Làm gì | Kết quả |
|---|---|---|
| 1. Kiểm tra | Toàn bộ 5.453 ảnh, 13.478 nhãn gốc, 32 lớp | Không có ảnh hỏng định dạng hay khung vượt biên; loại **12 ảnh lỗi nội dung + 55 ảnh còn biển chưa gán nhãn = 67 ảnh** (có danh sách lý do) |
| 2. Gom ảnh gần trùng | pHash 8×8 (64 bit); Hamming ≤ 6 → cùng cụm (nối bắc cầu) | **3.889 cụm cảnh** |
| 3. Gộp lớp hiếm | 6 lớp có < 60 cụm → "Biển báo khác" | 27 lớp |
| 4. Chia theo cụm | 70/15/15, phân tầng theo lớp và độ phân giải, seed 42; cả cụm đi vào một tập | Không ảnh test nào gần trùng ảnh train |
| 5. Đóng gói | Phiên bản v1 + mã băm SHA-256 + báo cáo chia | Tái lập được |

**Vì sao bỏ bản chia gốc?** Bản gốc có 4 cụm gần trùng vắt qua nhiều tập, và 6/32 lớp không có trong tập kiểm thử.

**Vì sao không chia ngẫu nhiên từng ảnh?** Hai khung hình liên tiếp của một đoạn đường gần như giống nhau. Nếu một ảnh vào train, ảnh kia vào test,
mô hình được "chấm" trên cảnh đã quen → con số đẹp nhưng không nói gì về đường mới.

### 5.4. Bảng chia tập (`tab:split`)

| | Train | Val | Test | Tổng |
|---|---|---|---|---|
| Số ảnh | 3.707 | 853 | 826 | 5.386 |
| Số biển | 9.450 | 2.009 | 2.017 | 13.476 |
| Tỉ lệ ảnh | 68,8 % | 15,8 % | 15,3 % | 100 % |

53 ảnh không có biển được giữ làm ảnh nền. Tỉ lệ không đúng 70/15/15 vì cụm phải đi nguyên khối.

**Vai trò của từng tập (phải nói đúng):**
- **Train:** học tham số YOLO; tạo vùng cắt để học SVM.
- **Val:** chọn epoch YOLO; chọn C của SVM; học bộ xác minh LightGBM.
- **Test:** đánh giá cuối. (Báo cáo viết "không tham gia lựa chọn nào" — xem lưu ý ở §12.)

### 5.5. EDA — đặc điểm dẫn tới thiết kế

| Đặc điểm | Số liệu | Hệ quả thiết kế |
|---|---|---|
| Biển rất nhỏ | Cạnh trung vị 30 px; 18,3 % < 16 px; 53,7 % < 32 px; vài lớp có 38–48 % < 16 px | Phân tích theo kích thước; T3 (1280 px, cắt ô) |
| Bốn độ phân giải | 960×540 (2.346), 1622×626 (2.213, Zalo), 1920×1080 (798), 540×960 (29) | Phân tầng khi chia; ảnh Zalo nhiều biển xa |
| Mất cân bằng | Nhiều nhất Giới hạn tốc độ 1.705 biển; ít nhất Chỗ quay xe 76 biển → chênh 22 lần (trước gộp 55 lần); biển cấm 57 % | Xem chỉ số theo lớp, macro-F1, không chỉ trung bình |
| Nhiều biển / ảnh | TB 2,5 biển; 73 ảnh có ≥ 10 biển | Cần detector, không thể phân loại cả ảnh |
| Không có nhãn chữ, video thật | — | OCR định tính; chưa đo tracking |

---

## 6. Kiến trúc hệ thống và từng khâu

### 6.1. Sơ đồ — tự vẽ lại được không nhìn tài liệu

```text
HỆ THỐNG CHÍNH (dùng chung cho API ảnh, video, webcam — src/utci_vision/pipeline.py)

Ảnh / khung hình
  → (1) Đánh giá chất lượng [CV]        đo độ sáng, tương phản, độ nét trên ảnh thu nhỏ 320 px
  → (2) Tăng cường thích nghi [CV]       chỉ khi cần: Gamma + CLAHE / CLAHE / lọc song phương
  → (3) YOLO11s 1280 px [DL]             khung bao + lớp (27) + điểm; ngưỡng 0,25; NMS IoU 0,5
  → (4) Bộ xác minh LightGBM [CV+ML]     TÙY CHỌN, TẮT mặc định
  → (5) Theo vết [CV] (chỉ video)        Kalman + Hungarian theo IoU + bỏ phiếu nhãn
  → (6) Đọc số/chữ [CV + DL]             cắt vùng bằng CV → VietOCR → regex + từ điển
  → Kết quả có cấu trúc + tên/ý nghĩa QCVN → FastAPI → React

  Ảnh tĩnh: các khâu chạy tuần tự.
  Video/webcam: phát hiện + theo vết mỗi khung; xác minh và OCR chạy NỀN theo từng vết
  (khi vết mới xuất hiện hoặc sau mỗi 10 khung), không chặn luồng phát hiện.

HỆ THỐNG ĐỐI CHỨNG (chỉ CV truyền thống + ML, không dùng mạng nơ-ron)

Ảnh → HSV, ngưỡng đỏ/xanh/vàng → mở/đóng 3×3 → contour → lọc hình dạng (tròn/tam giác/chữ nhật)
    → cắt nới 10 %, resize 32×32 → HOG 324 + histogram HSV 64 = 388 chiều → SVM RBF 28 lớp (27 biển + nền)
```

**Ghi nhớ:** hệ thống đối chứng **không dùng trong sản phẩm**; nó tồn tại để so sánh hai phương pháp trên cùng ảnh và cùng tập kiểm thử.

### 6.2. Cấu hình mặc định (`configs/pipeline.yaml`)

| Khâu | Mặc định |
|---|---|
| Đánh giá chất lượng | Bật; ảnh thu nhỏ rộng 320 px; ngưỡng tối μV < 0,30; tương phản thấp σL < 0,13; "nhiễu" Laplacian > 4000 |
| Tăng cường | Bật (chỉ áp khi chất lượng yêu cầu); Gamma đích 0,5, kẹp 0,4–3,0; CLAHE clip 2,0 lưới 8×8; song phương d=5, σ=50 |
| YOLO | `imgsz 1280`, `conf 0.25`, `iou 0.5`, FP16 trên GPU; `proposal_conf 0.10` chỉ dùng khi bật xác minh |
| Theo vết | Bật; IoU ghép ≥ 0,3; xác nhận sau 3 lần; xóa sau 15 khung mất dấu; cửa sổ bỏ phiếu 10 |
| Tác vụ nền theo vết | 2 worker; làm mới sau 10 khung |
| Bộ xác minh | **Tắt** |
| OCR | Bật |

### 6.3. Khâu 1–2: Đánh giá chất lượng và tăng cường thích nghi [CV]

- **Vấn đề:** ảnh tối/tương phản thấp làm mất tín hiệu biển; nhưng xử lý mạnh mọi ảnh lại làm hại ảnh tốt hoặc ảnh nhiễu.
- **Đầu vào:** ảnh màu, thu nhỏ rộng 320 px để đo nhanh.
- **Làm gì:** đo 3 chỉ báo, chọn phép xử lý theo quy tắc (lấy hợp các điều kiện thỏa):
  - μV (trung bình kênh V của HSV, 0–1) < 0,30 → **Gamma + CLAHE**
  - σL (độ lệch chuẩn kênh L của Lab, 0–1) < 0,13 → **CLAHE**
  - phương sai Laplacian > 4000 → **lọc song phương**
  - Không thỏa điều kiện nào → giữ nguyên ảnh.
- **Gamma:** γ = clip(ln μV / ln 0,5; 0,4; 3,0); I' = 255·(I/255)^(1/γ). Ảnh tối (μV < 0,5) → γ > 1 → số mũ 1/γ < 1 → ảnh sáng lên.
  Nói "đưa độ sáng về **gần** 0,5", không nói "bằng đúng 0,5".
- **CLAHE:** cân bằng histogram **cục bộ** theo ô 8×8, có giới hạn tương phản (clip 2,0) để không khuếch đại quá; áp trên kênh L để hạn chế làm lệch màu đỏ/xanh/vàng.
- **Lọc song phương:** làm mịn vùng giống nhau, giữ biên.
- **Đầu ra:** chỉ số chất lượng + ảnh (đã xử lý hoặc nguyên).
- **Bằng chứng:** T4 — ảnh rất tối 0,686 → 0,822; "luôn CLAHE" làm hại ảnh nhiễu (0,799 → 0,706) còn chế độ thích nghi thì không.
- **Giới hạn:** ngưỡng tối bỏ sót 20–32 % ảnh đã làm tối; Laplacian không phân biệt nhiễu với tán lá/chữ → lọc song phương chưa kích hoạt trong T4, **chưa có bằng chứng khử nhiễu**; ảnh tối là giả lập, không phải ảnh đêm thật; ngưỡng chọn từ thống kê Sprint 1, chưa chọn lại trên val.

### 6.4. Khâu 3: YOLO11s phát hiện + phân loại [DL]

- **Vấn đề:** cần tìm **và** phân loại nhiều biển trong cả cảnh phức tạp.
- **Đầu vào:** cả ảnh (sau tăng cường nếu có). **Đầu ra:** danh sách khung, lớp, điểm.
- **Vì sao YOLO11s:** một mô hình làm cả định vị lẫn phân loại; một giai đoạn, nhanh, hợp ảnh/video; biến thể "s" nhỏ, vừa GPU tầm trung; có trọng số pretrained COCO.
  **Không** nói "tốt nhất": nhóm chưa so có kiểm soát n/s/m hay các họ detector khác.
- **Fine-tune:** khởi tạo từ COCO rồi cập nhật **toàn bộ mạng** trên dữ liệu 27 lớp. Không train từ đầu.

| Cấu hình huấn luyện | Giá trị |
|---|---|
| Kích thước ảnh | 960 px (cạnh dài), giữ tỉ lệ, đệm |
| Epoch / batch | 80 / 8 |
| Tối ưu | AdamW, lr 0,001, cosine, 3 epoch warm-up |
| Tăng cường dữ liệu | Mặc định thư viện; **tắt lật ngang** (biển trái/phải đổi nghĩa); **tắt mosaic 15 epoch cuối** |
| Chọn trọng số | Epoch có mAP@50:95 cao nhất trên **val** |
| Môi trường | Colab Tesla T4, Ultralytics 8.4.183, 2 giờ 52 phút; một lần chạy, seed 42 |
| Suy luận | 1280 px, ngưỡng 0,25, NMS IoU 0,5, FP16 |

- **Train 960 mà suy luận 1280 có mâu thuẫn không?** Không. Cùng trọng số; phóng ảnh làm biển nhỏ chiếm nhiều ô hơn trên bản đồ đặc trưng.
  Nội suy **không tạo thêm chi tiết**, chỉ giúp mạng khai thác tín hiệu sẵn có. Kiểm chứng bằng T3, không suy ra "càng to càng tốt" (biển ≥ 64 px giảm nhẹ 0,976 → 0,958).
- **NMS:** nhiều khung cùng chỉ một biển → giữ khung điểm cao, bỏ khung trùng (IoU > 0,5).
- **Cắt ô 640 (kiểu SAHI):** tùy chọn; recall cao hơn nhưng mất ngữ cảnh, lỗi mép ô, precision giảm, chậm 2,5 lần.

### 6.5. Khâu 4: Bộ xác minh LightGBM [CV + ML, tùy chọn]

- **Ý tưởng:** đánh giá lại từng phát hiện của YOLO bằng đặc trưng thủ công để loại báo nhầm. **Không** tìm lại biển YOLO bỏ sót.
- **Đầu vào (vector z):** ngữ cảnh YOLO (điểm, lớp, kích thước, vị trí) + tỉ lệ màu HSV + đặc trưng hình học + 7 moment Hu + HOG giảm chiều bằng PCA (16 thành phần) + độ sáng/độ nét.
- **Mô hình:** LightGBM 400 cây, lr 0,05, 31 lá, cân bằng lớp + **hiệu chỉnh xác suất isotonic**.
- **Nhãn huấn luyện:** phát hiện của YOLO trên **val** ở ngưỡng thấp 0,10; đúng lớp và IoU ≥ 0,5 → dương, còn lại → âm.
- **Kết quả:** không vượt điểm YOLO → **tắt mặc định** (chi tiết §8.5). Vẫn bật được trên giao diện khi muốn ít báo nhầm hơn.
- **Gọi đúng tên:** LightGBM là **học máy (cây tăng cường)**, không phải học sâu. Báo cáo gắn nhãn "[CV + DL]" vì có ngữ cảnh YOLO — khi nói, dùng "**CV + ML, có ngữ cảnh từ YOLO**" (§12).

### 6.6. Khâu 5: Theo vết [CV] (chỉ video/webcam)

- **Vấn đề:** cùng một biển xuất hiện ở nhiều khung; nhãn có thể "nhảy" giữa các khung do mờ.
- **Làm gì (kiểu SORT):**
  1. Kalman lưu trạng thái 8 chiều: tâm (cx, cy), kích thước (w, h) và vận tốc thay đổi của 4 đại lượng này **trên ảnh** → dự đoán khung ở khung hình sau.
  2. Tính IoU giữa khung dự đoán và phát hiện mới.
  3. Hungarian ghép một–một sao cho tổng IoU lớn nhất; cặp IoU < 0,3 bị loại.
  4. Vết xác nhận sau 3 lần quan sát; xóa sau 15 khung mất dấu.
  5. Nhãn hiển thị = lớp có tổng điểm lớn nhất trong 10 quan sát gần nhất (bỏ phiếu có trọng số).
- **Đầu ra:** mã vết ổn định + nhãn đã bỏ phiếu; OCR chọn khung có (diện tích × độ nét) lớn nhất của vết.
- **Giới hạn:** Kalman mô tả **chuyển động biểu kiến trên ảnh**, không đo tốc độ xe; **chưa đo** mức giảm "nhảy nhãn" vì chưa có video đường phố thật (công cụ `evaluate.py flicker` đã có). Ghép ảnh tĩnh thành video **không hợp lệ** để đo.

### 6.7. Khâu 6: Đọc số và chữ [CV + DL]

- **Vì sao phải cắt vùng trước?** VietOCR cần nhìn một dòng chữ/số, không phải cả ảnh đường phố.
- **Số (tốc độ, chiều cao):** cắt đĩa trong viền đỏ (78 % đường kính), phóng 3 lần, yêu cầu chiều cao vùng ≥ 40 px (nhỏ hơn thì chờ khung gần hơn).
- **Chữ / biển phụ:** tìm tấm chữ nhật sáng phía dưới biển chính (vùng tìm cao 1,2 lần biển), tách dòng bằng chiếu histogram theo hàng, CLAHE, chỉnh nghiêng.
- **Đọc:** VietOCR cấu hình VGG-Transformer (VGG trích đặc trưng, Transformer giải mã), **pretrained, không fine-tune**.
- **Hậu xử lý:** regex tách số + đơn vị; tốc độ phải thuộc danh sách hợp lệ 5–120 km/h; chiều cao 1,5–6 m; chữ so với từ điển bằng độ tương đồng chuỗi ≥ 80/100; dòng có độ tin cậy < 0,75 bị bỏ.
  Lưu cả chuỗi gốc và chuỗi đã xử lý.
- **Nguyên tắc "không đoán":** 50 và 60 đều hợp lệ → nếu ảnh không phân biệt được thì để trống. Không dùng tên lớp để tự điền số.
- **Giới hạn:** **chưa có nhãn chữ** → không có CER, không có tỉ lệ khớp toàn chuỗi. Các ví dụ đọc đúng "40 km/h", "60 km/h", "2,0 m" là **định tính**.

### 6.8. Hệ thống đối chứng: màu + hình dạng + HOG + SVM [CV + ML]

| Bước | Chi tiết | Lưu ý khi giải thích |
|---|---|---|
| Phân đoạn màu HSV | Đỏ H ∈ [0,10] ∪ [160,179] (đỏ nằm ở hai đầu vòng màu), S ≥ 70, V ≥ 50; xanh H ∈ [95,130]; vàng H ∈ [15,35] | Mặt nạ màu **chưa phải** kết quả nhận diện; áo đỏ cũng lọt |
| Hình thái học | Mở rồi đóng, phần tử 3×3 | Mở: xóa đốm nhỏ; đóng: nối viền đứt |
| Ứng viên theo hình dạng | Diện tích 60 px² → 25 % ảnh; tỉ lệ a = w/h; số đỉnh k (xấp xỉ đa giác 0,04 chu vi); độ đặc ρ = A/A_bao-lồi; độ tròn **bao lồi** 4πA/P² | Viền đỏ biển cấm là vòng rỗng → dùng bao lồi |
| Quy tắc hình | Tròn: 0,6 ≤ a ≤ 1,6 và độ tròn ≥ 0,75 · Tam giác: đỏ/vàng, k = 3, 0,7 ≤ a ≤ 1,5, ρ > 0,6 · Chữ nhật: xanh, 4 ≤ k ≤ 6, 0,5 ≤ a ≤ 3, ρ > 0,8 | NMS IoU 0,3; loại mảnh màu nằm trong biển lớn |
| Đặc trưng | Cắt nới 10 %, 32×32; **HOG** 9 hướng, ô 8×8, khối 2×2 → 3×3 khối × 36 = **324**; **histogram HSV** 16×4 = **64**; ghép **388** | HOG trên ảnh xám bỏ màu; màu là thông tin quy chuẩn → bổ sung nhau |
| SVM | RBF, chuẩn hóa đặc trưng, **28 lớp nội bộ = 27 biển + 1 nền**; 15.449 mẫu train (6.000 nền), val 3.509; chọn C ∈ {1, 10} trên val → C = 10; ẩn ứng viên xác suất < 0,30 | Lớp nền lấy từ ứng viên trên ảnh train có IoU < 0,1 với biển thật; **không** nói "nhận 28 loại biển" |
| SIFT-BoVW (đối chứng âm) | SIFT trên vùng 64×64, k-means MiniBatch 256 từ, histogram từ → cùng SVM | Dự kiến kém vì biển ít kết cấu → E8 xác nhận |

Kết quả SVM trên val (12/11): accuracy biển 0,880, nhận đúng nền 0,971.

### 6.9. Khâu nào là CV, ML, DL? (hay bị hỏi)

| Khâu | Loại |
|---|---|
| Đánh giá chất lượng, Gamma, CLAHE, song phương | CV truyền thống |
| HSV, hình thái học, contour, đặc trưng hình dạng, HOG, histogram, SIFT | CV truyền thống (trích đặc trưng) |
| SVM, LightGBM, isotonic, PCA | Học máy (ML) |
| Kalman, Hungarian, IoU | CV truyền thống (theo vết) / tối ưu tổ hợp |
| YOLO11s, VietOCR | Học sâu (DL) |
| Regex, từ điển | Luật / hậu xử lý |

Vì vậy: nhánh đối chứng = "**CV truyền thống kết hợp ML**"; bộ xác minh = "**CV + ML dùng ngữ cảnh detector**".

---

## 7. Huấn luyện, giao thức đánh giá và độ đo

### 7.1. Ai học trên tập nào

| Mô hình | Học trên | Chọn tham số trên |
|---|---|---|
| YOLO11s | Train | Val (chọn epoch) |
| SVM đối chứng | Vùng cắt từ train (9.449 vùng biển + nền) | Val (chọn C) |
| LightGBM xác minh | Phát hiện YOLO trên val | — (đánh giá trên test) |
| VietOCR | Không huấn luyện (pretrained) | — |

Mọi lần chạy được ghi vào `experiments/registry.csv` (mã thí nghiệm, commit, cấu hình, môi trường, kết quả).

### 7.2. Giao thức đánh giá (cố định cho mọi thí nghiệm)

- **Điểm vận hành:** P, R, F1 tại ngưỡng hiển thị **0,25**, **đúng lớp** và **IoU ≥ 0,5**. Precision ở ngưỡng tối ưu F1 của thư viện không phải thứ người dùng thấy.
  Ma trận nhầm lẫn mặc định của Ultralytics ghép cả dự đoán điểm 0,001 → không dùng làm bằng chứng.
- **Theo kích thước và theo lớp:** 4 nhóm < 16, 16–32, 32–64, ≥ 64 px; recall từng lớp.
- **Khoảng tin cậy:** bootstrap theo ảnh 500–2.000 lần (ghép cặp khi so hai cấu hình trên cùng ảnh); Wilson cho tỉ lệ theo lớp.
  Hai cấu hình chỉ được coi là khác nhau khi CI của hiệu **không chứa 0**.
- **Mức tương đồng với train:** chia ảnh test theo khoảng cách pHash tới ảnh train gần nhất (≤ 10, 11–14, ≥ 15 bit) — thay cho tập ngoài phân phối mà đề tài không có.
- **Ảnh xấu giả lập:** tối I' = 255(I/255)^γ với γ 2,5 / 3,5; nhiễu Gauss σ 15; mờ chuyển động ngang 9 px.
- **Tốc độ:** luôn ghi phần cứng, kích thước ảnh, các khâu được tính.

### 7.3. Độ đo — ví dụ tính tay (ai cũng phải tự làm được)

**IoU = diện tích giao / diện tích hợp.** Hai khung cùng diện tích 100, giao 60 → hợp = 100 + 100 − 60 = 140 → IoU ≈ 0,429 < 0,5 → không khớp.

**TP / FP / FN:** đúng lớp và khớp một nhãn chưa ghép → TP; sai lớp, không khớp hoặc trùng → FP; biển thật chưa được phát hiện đúng → FN.
Khung đúng vị trí nhưng **sai lớp** → không phải TP (thường tạo 1 FP và 1 FN).

**Ví dụ:** 10 biển thật, hệ thống trả 12 khung, 8 khung khớp đúng → TP = 8, FP = 4, FN = 2.
P = 8/12 ≈ 0,667 · R = 8/10 = 0,8 · F1 = 2PR/(P+R) ≈ 0,727.

- **Precision:** trong những gì báo ra, bao nhiêu đúng. **Recall:** trong các biển thật, tìm đúng bao nhiêu.
- **AP:** tóm tắt đường precision–recall của một lớp; **mAP** = trung bình AP các lớp. mAP@50 dùng IoU 0,5; mAP@50:95 trung bình 10 ngưỡng IoU 0,50–0,95 (đòi khung khớp chặt hơn).
  **mAP 0,905 không có nghĩa "đúng 90,5 % biển".**
- **Accuracy** (chỉ dùng cho phân loại vùng cắt, E8) = số vùng đúng / số vùng. **Macro-F1** = trung bình F1 từng lớp (lớp hiếm nặng ngang lớp phổ biến).
- **CER** = (S + D + I)/N (thay, xóa, chèn ký tự / độ dài chuỗi chuẩn). Ví dụ "40" đọc thành "60" → CER = 1/2 = 0,5. **Chưa tính được** vì không có nhãn chữ.
- **FPS** = số khung / thời gian. FPS detector ≠ thời gian API có OCR ≠ FPS webcam đầu cuối.

**Ba ngưỡng IoU khác nhau, đừng lẫn:** 0,5 để chấm detection · 0,5 cho NMS · 0,3 để ghép vết.
**Confidence 0,9 không có nghĩa đúng 90 %.** Đó là điểm của mô hình, chưa được hiệu chỉnh thành xác suất.

---

## 8. Thực nghiệm và kết quả

Môi trường: huấn luyện trên Colab T4; **mọi đánh giá và đo tốc độ trên RTX 4060 Laptop**. Trừ khi ghi khác: tập test 826 ảnh, 2.017 biển.

### 8.1. Danh sách thí nghiệm (`tab:experiments`)

| Mã | Câu hỏi | Thiết kế |
|---|---|---|
| S1 | YOLO11s học tốt đến đâu trên dữ liệu cùng nguồn? | Huấn luyện 960 px; mAP, CI, theo lớp, kích thước, tương đồng |
| T0, T1 | Đặc trưng thủ công có giúp loại phát hiện sai của YOLO? | Ablation tập đặc trưng bộ xác minh; P ở cùng recall |
| T3 | Tăng recall biển nhỏ mà không huấn luyện lại? | Suy luận 960 / 1280 / cắt ô 640 |
| T4, E4 | Tăng cường thích nghi có giúp khi ảnh xấu? | Tối, nhiễu, mờ; không xử lý / thích nghi / luôn áp |
| E8 | Đặc trưng thủ công + SVM so với YOLO ở phân loại? | Cùng 2.017 biển; theo kích thước; ghép cặp |
| E1, E2 | Hệ thống mặc định đạt bao nhiêu; mỗi khâu đóng góp gì? | Cấu hình mặc định; ablation từng khâu |

(E5 = OCR, E6 = ổn định nhãn video: **chưa đo** định lượng.)

### 8.2. S1 — Baseline YOLO11s (960 px, test)

| Chỉ số | Ultralytics | Nhóm tính lại | CI 95 % |
|---|---|---|---|
| mAP@50 | 0,905 | 0,892 | [0,868; 0,917] |
| mAP@50:95 | 0,684 | 0,676 | [0,657; 0,702] |
| Precision @ 0,25 | — | 0,860 | [0,842; 0,878] |
| Recall @ 0,25 | — | 0,893 | [0,875; 0,913] |

- Hai cách tính lệch khoảng 0,01 do khác cách đệm ảnh → nói "**mAP@50 khoảng 0,89–0,91**".
- Val: mAP@50 0,894, mAP@50:95 0,683 ≈ test → chọn epoch không quá khớp val.
- Precision 0,920 thư viện báo là ở ngưỡng tối ưu F1; ở ngưỡng 0,25 là 0,860.
- Hội tụ: loss train và val giảm đều đến epoch 80; mAP@50:95 val 0,645 (ep 30) → 0,672 (ep 50) → 0,685 (ep 80); bước tụt loss quanh epoch 66 do tắt mosaic.
  Nói "**chưa thấy dấu hiệu quá khớp trên đường cong**", không nói "chắc chắn không quá khớp".

**Theo kích thước (val + test, ngưỡng 0,25):**

| Cạnh biển | Số biển | Đúng lớp | Sai lớp | Bỏ sót |
|---|---|---|---|---|
| < 16 px | 702 | 0,617 | 0,056 | 0,328 |
| 16–32 px | 1.427 | 0,922 | 0,036 | 0,043 |
| 32–64 px | 1.261 | 0,964 | 0,013 | 0,023 |
| ≥ 64 px | 636 | 0,975 | 0,003 | 0,022 |

→ **Điểm yếu chính là TÌM biển nhỏ, không phải phân loại sai.**

**Theo lớp:** 24/27 lớp recall ≥ 0,81. Ba lớp yếu có nguyên nhân rõ:
- Vạch sang đường cho người đi bộ (0,57; n = 30) và Giới hạn chiều cao (0,68; n = 65): 57 % và 34 % biển < 16 px; với biển ≥ 16 px recall 1,00 và 0,84.
- Biển chỉ dẫn hướng đi (R 0,70, P 0,60): nhãn gốc gộp cả bảng chữ nhật lẫn biển tròn xanh → **lỗi định nghĩa lớp trong dữ liệu**, không sửa được vì dữ liệu đóng băng.
- Số lượng dữ liệu tương quan yếu với chất lượng lớp (Spearman 0,16–0,32). Lớp hiếm vẫn đạt 0,81–0,97 nhưng CI rộng (23–31 biển).
- Cặp nhầm lớn nhất ≤ 6 %: Biển gộp làn ↔ Chỉ dẫn hướng đi; Cấm dừng và đỗ ↔ Cấm đỗ; Giới hạn tốc độ → Biển cấm phương tiện.

**Theo mức tương đồng với train:** dù không ảnh test nào gần trùng train (pHash ≤ 6), khoảng 1/3 ảnh test vẫn khá giống (cùng tuyến, cùng camera).
Recall 0,978 (giống) → 0,805 (khác); precision 0,942 → 0,749. Chỉ xét biển ≥ 16 px, recall vẫn giảm 0,978 → 0,893.
→ **Con số trên nhóm "khác train" là ước lượng gần hơn cho đường mới.** (Số ảnh nhóm: 243 / 271 / 265 = 779 ảnh — xem §12.)

### 8.3. T3 — Biển nhỏ: độ phân giải suy luận và cắt ô

| Cách suy luận (cùng trọng số 960) | P | R | F1 | R < 16 px | ms/ảnh |
|---|---|---|---|---|---|
| 960 px | 0,861 | 0,893 | 0,877 | 0,634 | 18,6 |
| **1280 px (mặc định)** | 0,861 | 0,917 | 0,888 | **0,737** | 21,4 |
| 960 + cắt ô 640 | 0,749 | 0,932 | 0,831 | 0,784 | 46,5 |

GPU RTX 4060 Laptop, thời gian **chỉ khâu phát hiện**.
- 1280 px: +10,3 **điểm phần trăm** recall biển < 16 px (không phải +10,3 %), precision giữ nguyên, chậm thêm ≈ 15 %; biển ≥ 64 px giảm nhẹ 0,976 → 0,958.
- Cắt ô: recall cao nhất nhưng precision −0,11 (mất ngữ cảnh, báo nhầm ở mép ô), chậm 2,5 lần → chỉ là tùy chọn cho ảnh tĩnh độ phân giải cao.

### 8.4. T4 / E4 — Tăng cường khi ảnh xấu (YOLO 960 px, CI bootstrap ghép cặp 1.000 lần)

| Điều kiện | Không xử lý (R) | Thích nghi: % ảnh xử lý; R; ΔR (CI) | Luôn Gamma + CLAHE: R; ΔR (CI) |
|---|---|---|---|
| Ảnh gốc | 0,893 | 2,8 %; 0,892; −0,001 (−0,003; 0,000) | 0,890; −0,003 (−0,010; +0,004) |
| Tối γ 2,5 | 0,810 | 68,2 %; 0,853; +0,044 (+0,032; +0,056) | 0,873; +0,063 (+0,049; +0,077) |
| Rất tối γ 3,5 | 0,686 | 80,5 %; **0,822**; **+0,136** (+0,116; +0,155) | 0,854; +0,168 (+0,147; +0,188) |
| Nhiễu σ 15 | 0,799 | 2,8 %; 0,799; 0,000 | **0,706; −0,093** (−0,109; −0,077) |
| Mờ chuyển động | 0,748 | 2,8 %; 0,748; 0,000 | 0,734; −0,014 (−0,024; −0,004) |

Ba ý phải nói:
1. Tăng cường có tác dụng rõ với ảnh tối: khôi phục 53 % (γ 2,5) và 66 % (γ 3,5) phần recall bị mất; precision giảm nhẹ ≈ 0,02.
2. **Bước đánh giá chất lượng là cần thiết:** "luôn CLAHE" làm hại ảnh nhiễu và ảnh mờ; chế độ thích nghi không kích hoạt nên không hại, và gần như không chạm ảnh tốt (2,8 %).
3. Hạn chế: thích nghi **kém hơn "luôn áp" trên ảnh tối** vì ngưỡng bỏ sót ảnh tối; Laplacian không nhận ra nhiễu thật → chưa có bằng chứng khử nhiễu.

E4 (hệ thống đầy đủ, 1280 px, ảnh tối γ 2,5): P 0,884, R 0,866, F1 0,875.

### 8.5. T0 / T1 — Bộ xác minh

- **T0:** 68–71 % phát hiện sai của YOLO là vùng nền (sai lớp 21–25 %, định vị kém 4–8 %) → dư địa lý thuyết lớn. Nhưng chính điểm YOLO đã phân biệt đúng/sai rất tốt: **AUC 0,941**.
- **T1** (học trên val, đánh giá trên test):

| Tập đặc trưng | AUC | P cùng recall (R 0,893) | P / R với ngưỡng chọn trên val |
|---|---|---|---|
| Điểm YOLO (không xác minh) | 0,941 | 0,864 | 0,864 / 0,893 |
| Ngữ cảnh YOLO | 0,929 | 0,864 | 0,886 / 0,879 |
| + màu HSV | 0,933 | 0,863 | 0,880 / 0,881 |
| + màu + hình học + Hu | 0,935 | 0,859 | 0,875 / 0,888 |
| + màu + hình học + Hu + HOG | 0,935 | 0,876 | 0,873 / 0,895 |
| Đầy đủ (thêm độ nét, sáng) | 0,934 | 0,866 | 0,878 / 0,891 |
| Chỉ đặc trưng thủ công | 0,856 | 0,832 | 0,842 / 0,888 |

- Bộ đầy đủ ở cùng recall: **ΔP = +0,005, CI [−0,012; +0,022] → không có ý nghĩa**; mục tiêu P ≥ 0,90 không đạt.
- Đặc trưng thủ công **có tín hiệu** (AUC 0,856 > 0,5) nhưng **trùng lặp** với thông tin CNN đã học. Thiếu mẫu âm (≈ 500 sai vs 1.828 đúng trên val), không thêm được ảnh nền khó vì dữ liệu đóng băng.
- Câu trả lời mẫu: "*Nhóm thử một giả thuyết có lý do, đo trước khi tích hợp; lợi ích chưa đủ bằng chứng nên tắt mặc định và báo cáo như kết quả âm trung thực.*"

### 8.6. E8 — Phân loại: đặc trưng thủ công vs YOLO

**Thiết kế (phải nói trước khi đọc số):** cùng 2.017 biển test. Phương pháp truyền thống được **cho sẵn vị trí** (vùng cắt từ nhãn thật, nới 10 %), học trên 9.449 vùng train, chọn C trên 2.009 vùng val.
YOLO phải **tự tìm**: lớp của YOLO = dự đoán điểm cao nhất có IoU ≥ 0,5; không có → tính sai. Vì truyền thống có lợi thế, phép so công bằng là trên **1.956 biển YOLO tìm thấy**.

| Phương pháp | Accuracy (CI 95 %) | Macro-F1 | Acc. trên biển YOLO tìm thấy | ms |
|---|---|---|---|---|
| SIFT-BoVW + SVM | 0,711 (0,691–0,730) | 0,662 | 0,724 | 2,7 / vùng (CPU) |
| HOG + SVM | 0,888 (0,874–0,901) | 0,852 | 0,901 | 1,6 / vùng (CPU) |
| **HOG + màu + SVM** | **0,910** (0,897–0,922) | 0,872 | 0,920 | 2,0 / vùng (CPU) |
| YOLO11s | **0,924** (0,912–0,935) | 0,917 | 0,953 | 22 / **ảnh** (GPU, gồm cả tìm biển) |

**Theo kích thước** (accuracy, toàn bộ 2.017 biển): YOLO 0,706 / 0,957 / 0,979 / 0,993; HOG + màu 0,812 / 0,929 / 0,953 / 0,892 (< 16 / 16–32 / 32–64 / ≥ 64 px).

Năm kết luận:
1. Đặc trưng thủ công cạnh tranh ở khâu phân loại: kém YOLO 1,4 điểm tổng; thêm màu vào HOG +2,2 điểm. 91,0 % cùng mức HOG-SVM trên GTSRB (89,65–91,25 %) nhưng **không so trực tiếp được** vì khác dữ liệu.
2. Biển nhỏ: điểm yếu của YOLO là **tìm**, không phải phân loại. YOLO bỏ sót 15,5 % biển < 16 px. Trên biển nhỏ YOLO tìm thấy, hai bên **ngang nhau** (+2,0 điểm, CI −2,6 đến +6,6).
3. Biển lớn là nơi đặc trưng thủ công thua rõ nhất (−10,4 điểm, CI −14,3 đến −7,3): thu về 32×32 làm mất chi tiết biển chỉ dẫn, biển có chữ.
4. SIFT không hợp với biển báo: kém HOG 17,7 điểm; số điểm SIFT trung vị = 1 với biển < 16 px (93 % có < 5 điểm). Chỉ nói "**không phù hợp trong thử nghiệm của nhóm**", không nói "SIFT vô dụng".
5. Đặc trưng thủ công rẻ nhưng **cần bước định vị riêng** — chính là phần YOLO làm tốt.
- Ghép cặp tổng thể trên biển YOLO tìm thấy: HOG + màu − YOLO = −3,3 điểm (0,920 vs 0,953).

**So toàn hệ thống trên cùng ảnh** (định tính, `fig:qualitative`): ảnh có 16 biển được gán nhãn → YOLO trả 22 phát hiện (có biển xa không được gán nhãn và vài phát hiện trùng), pipeline truyền thống trả 8;
truyền thống gộp các biển cùng màu đứng sát nhau, bỏ sót biển chỉ dẫn nhiều màu và biển rất nhỏ, báo nhầm trên áo đỏ. Khi YOLO cung cấp vị trí, HOG + màu + SVM đồng ý với YOLO ở 14/22 biển.
→ **Nút thắt của CV truyền thống là định vị bằng màu–hình dạng, không phải phân loại.**

**Tuyệt đối không nói:** "HOG-SVM tìm đúng 91 % biển ngoài đường" hay "hai detector gần ngang nhau".

### 8.7. E1 / E2 — Hệ thống đầy đủ và ablation

**E1 — cấu hình mặc định** (tăng cường thích nghi bật, 1280 px, xác minh tắt, OCR bật):

| Tập | P | R | F1 | R < 16 | R 16–32 | R 32–64 | R ≥ 64 | ms/ảnh |
|---|---|---|---|---|---|---|---|---|
| Test | 0,862 | 0,917 | 0,889 | 0,734 | 0,941 | 0,976 | 0,958 | 22,5 |
| Test làm tối γ 2,5 | 0,884 | 0,866 | 0,875 | 0,662 | 0,860 | 0,948 | 0,958 | 34,8 |

Thời gian: chất lượng + tăng cường (khi cần) + phát hiện, RTX 4060 Laptop. So với YOLO 960 không tăng cường: R 0,893 → 0,917; R < 16 px 0,634 → 0,734 (đạt mục tiêu ≥ 0,70); P giữ nguyên.

**E2 — ablation** (đo ở **960 px**, trước khi đổi mặc định sang 1280):

| Cấu hình | P | R | F1 | R < 16 | P tối | R tối | F1 tối |
|---|---|---|---|---|---|---|---|
| YOLO11s | 0,861 | 0,893 | 0,877 | 0,634 | 0,905 | 0,813 | 0,856 |
| + tăng cường thích nghi | 0,860 | 0,893 | 0,876 | 0,634 | 0,885 | 0,854 | 0,869 |
| + bộ xác minh | 0,946 | 0,841 | 0,891 | 0,526 | 0,960 | 0,796 | 0,871 |

- Tăng cường: không đổi trên ảnh thường (kích hoạt ≈ 3 %), +0,041 recall trên ảnh tối — khớp T4.
- Xác minh: P +0,085 nhưng R −0,052, riêng biển < 16 px −0,108 → **dịch điểm vận hành, không phải cải thiện thật** (T1).
- mAP tính trên đầu ra hệ thống (đã cắt ở 0,25): mAP@50 0,869, mAP@50:95 0,667 — **thấp hơn** mAP mô hình vì đường P–R bị cắt; chỉ dùng để so giữa các cấu hình.
- **Không so E1 (1280) trực tiếp với E2 (960)** rồi quy hết cải thiện cho tăng cường.

### 8.8. OCR — chỉ định tính

Trên ảnh test, đọc đúng "40 km/h", "60 km/h" (giới hạn tốc độ) và "2,0 m" (giới hạn chiều cao). Chữ trên biển nhỏ thường bị loại vì độ tin cậy < 0,75 → để trống thay vì đoán.
Muốn đo định lượng cần tập nhãn chữ riêng (CER, tỉ lệ khớp hoàn toàn) — là hướng phát triển.

### 8.9. Tốc độ (`tab:speed`)

| Phép đo | Kết quả |
|---|---|
| Phát hiện, 960 px, FP16, RTX 4060 Laptop | 18,3 ms (54,6 FPS) |
| Chất lượng + tăng cường + phát hiện, 1280 px, cùng GPU | 22,5 ms/ảnh |
| Ảnh tĩnh qua API trong Docker CPU, **gồm OCR** | 0,9–1,6 s/ảnh (đạt yêu cầu ≤ 3 s) |
| Pipeline CV truyền thống trên CPU, ảnh mẫu | 50–225 ms/ảnh (phụ thuộc số ứng viên) |
| Webcam WebSocket, CPU, 960 px | 9,3 FPS |
| Webcam WebSocket, Docker CPU, 1280 px | 3,5 FPS |
| Video nền 30 khung (Docker CPU) | 10 s |
| Khởi động API, nạp 4 mô hình, không cần mạng | 11 s |

**Chưa đo:** webcam thời gian thực trên GPU qua giao diện web. Không so 2 ms/vùng CPU với 22 ms/ảnh GPU để kết luận phương pháp nào nhanh hơn đầu cuối.

---

## 9. Phần mềm: mã nguồn, API, web, Docker

### 9.1. Cấu trúc mã nguồn

| Tệp / thư mục | Chức năng |
|---|---|
| `src/utci_vision/enhance.py` | [CV] Đánh giá chất lượng; Gamma tự động, CLAHE kênh L, lọc song phương |
| `src/utci_vision/detector.py` | [DL] YOLO11s: suy luận, FP16, cắt ô chồng lấn |
| `src/utci_vision/tracking.py` | [CV] Kalman + Hungarian theo IoU, bỏ phiếu nhãn |
| `src/utci_vision/verifier.py` | [CV + ML] Đặc trưng HSV, hình học, Hu, HOG + ngữ cảnh YOLO → LightGBM |
| `src/utci_vision/ocr.py` | [CV + DL] Cắt vùng số/dòng chữ/biển phụ; VietOCR; regex + từ điển |
| `src/utci_vision/traditional.py` | [CV] Pipeline đối chứng HSV → hình thái → hình dạng → HOG + màu → SVM |
| `src/utci_vision/pipeline.py` | Ghép các khâu theo cấu hình; dùng chung cho API, video, webcam, đánh giá |
| `src/utci_vision/api/` | FastAPI: ảnh, video nền, WebSocket, so sánh, ảnh mẫu |
| `src/utci_vision/evaluation/` | Ghép dự đoán, mAP, bootstrap, Wilson, ảnh xấu giả lập |
| `src/utci_vision/data/` | Audit, dedup pHash, chia cụm, đóng gói, crop |
| `configs/*.yaml` | Lớp (QCVN), dữ liệu, YOLO, pipeline, xác minh, OCR, truyền thống, API, ảnh mẫu |
| `scripts/` | `data.py`, `eda.py`, `analyze_run.py` (S1), `verifier_feasibility.py` (T0/T1), `compare_traditional_dl.py` (E8), `enhance_robustness.py` (T4), `evaluate.py` (E1/E2/E4/T3/flicker/benchmark), `train_hog_svm.py`, `fit_verifier.py`, `infer.py`, `import_run.py`, `export_web_data.py` |
| `notebooks/train/` | 3 notebook fine-tune (local/Colab/Kaggle) sinh từ `_template.py` |
| `web/` | React 19 + Vite + TypeScript + Recharts |
| `tests/` | pytest: đơn vị + hợp đồng API Python ↔ TypeScript |
| `experiments/registry.csv` | Sổ đăng ký mọi lần chạy |

### 9.2. API (`/api/v1`)

| Endpoint | Chức năng |
|---|---|
| `GET /health`, `GET /classes` | Trạng thái 4 mô hình (detector, verifier, classic, ocr); 27 lớp + QCVN |
| `POST /detect/image` | Ảnh hoặc ảnh mẫu; ghi đè `enhance`, `verifier`, `imgsz` (320–1920), `tiled`; `degrade` = dark/noise/blur |
| `GET /samples` | 16 ảnh mẫu (ảnh test) |
| `POST /traditional/analyze` | Pipeline CV truyền thống: ảnh input/enhanced/mask/ứng viên/kết quả, HOG + SIFT |
| `POST /compare` | YOLO và CV truyền thống trên cùng ảnh + bảng so khớp từng biển |
| `POST /jobs/video`, `GET /jobs/{id}` | Xử lý video nền, tiến độ, video kết quả |
| `WS /stream` | Webcam: JPEG vào, JSON ra, back-pressure một khung |

### 9.3. Các trang web (giải thích phương pháp, không chỉ "khoe giao diện")

| Đường dẫn | Trang | Dùng để chứng minh |
|---|---|---|
| `/` | Bảng điều khiển | KPI, trạng thái mô hình |
| `/data` | Mô tả dữ liệu | EDA: chia tập, kích thước, mất cân bằng |
| `/library` | Thư viện biển | 27 lớp theo QCVN |
| `/pipeline` | Pipeline hệ thống | Sơ đồ hai hệ thống + từng khâu trên một ảnh |
| `/demo/dl` | Demo học sâu | Bật/tắt khâu, đổi 960 ↔ 1280, mô phỏng ảnh xấu → T3, T4, E2 trực tiếp |
| `/demo/traditional` | Demo CV truyền thống | Mask HSV, ứng viên, HOG, SIFT, lớp SVM |
| `/compare` | So sánh CV – DL | Hai hệ thống cùng ảnh; biểu đồ E8, T4 |
| `/results` | Kết quả thực nghiệm | Đường cong huấn luyện, CI, E1/E2/T3, theo lớp, tương đồng |
| `/demo/video`, `/demo/webcam` | Video, Webcam | Theo vết; WebSocket |
| `/about` | Giới thiệu | Công nghệ, giấy phép |

### 9.4. Chạy hệ thống

```bash
# Cài lần đầu
make env && make venv          # rồi TỰ cài PyTorch theo GPU (torch >= 2.4)
make install && make check-env

# Phát triển (PowerShell hoặc Git Bash)
make dev                       # API :18100 + web Vite :15173
# Demo bằng Docker
make up                        # CPU  → http://localhost:18080
make up-gpu                    # GPU  (NVIDIA driver + Docker Desktop WSL2)
make ci                        # lint + test + build web + kiểm compose
```

File **không có trong git** cần chép trước khi demo: `models/current/yolo11.pt` (19 MB, run `20261029-1030_yolo11s_960`), `models/vietocr/vgg_transformer.pth` (152 MB),
`models/current/hog_svm.joblib` (33 MB, `train_hog_svm.py` ≈ 5 phút CPU), `models/current/verifier.joblib` (7 MB, `fit_verifier.py`), `dataset/processed/v1/` (ảnh mẫu đọc từ `test/images`).
Hướng dẫn chi tiết Windows: `docs/HUONG_DAN_CHAY_WINDOWS.md`.

### 9.5. Giấy phép (có thể bị hỏi)

Mã dự án Apache-2.0; **Ultralytics YOLO11 là AGPL-3.0** (đồ án học thuật chỉ cần ghi nguồn; phát hành sản phẩm/dịch vụ phải tuân AGPL); dữ liệu CC BY 4.0 (phải ghi nguồn — báo cáo đã ghi); VietOCR mã nguồn mở.

---

## 10. Báo cáo LaTeX: cấu trúc và cách biên dịch

### 10.1. Bố cục (`BaoCao/Nhom07/main.tex`)

| Phần | Tệp | Nội dung |
|---|---|---|
| Bìa | `metadata.tex`, `ictureport.cls` | Tên đề tài, 5 thành viên (Hoàn có dấu # nhóm trưởng), GVHD, 11/2026 |
| Phần đầu (số La Mã) | `frontmatter/` | Lời cảm ơn, mục lục, phân công (theo sprint + theo thành viên), danh mục bảng/hình, viết tắt (28 mục) |
| Mở đầu | `chapters/modau.tex` | Bối cảnh, M1–M4, phạm vi, bố cục |
| Chương 1 — Cơ sở lý thuyết | `chuong1_nentang.tex`, `chuong1_lienquan.tex` | AI/ML/DL, CNN, phát hiện đối tượng, xử lý ảnh (màu, lọc, phân vùng, tần số), đặc trưng (HOG, PCA, pHash); nghiên cứu liên quan + 3 khoảng trống |
| Chương 2 — Phương pháp và mô hình | `chuong2.tex` | Bài toán; dữ liệu + EDA; kiến trúc; DL (YOLO, OCR); CV (tăng cường, đối chứng, SIFT, xác minh, theo vết); giao thức + danh sách thí nghiệm |
| Chương 3 — Kết quả thực hiện | `chuong3.tex` | Thiết lập; S1; T3; T4/E4; E8; T0/T1; E1/E2; OCR; tốc độ; demo web; thảo luận + hạn chế |
| Kết luận | `ketluan.tex` | Kết quả theo M1–M4, 4 bài học, tác động, 5 hướng phát triển |
| Tài liệu tham khảo | `references.bib` | 68 mục, đã đối chiếu DOI/nơi đăng (`docs/research/tai_lieu_bao_cao.md`) |
| Phụ lục | `phuluc.tex` | Cấu trúc mã, đoạn mã lõi, bảng lệnh tái lập → bảng/hình, nguồn gốc dữ liệu, ảnh web |

**Ba khoảng trống nghiên cứu** đề tài nhắm tới (Ch1 §Tổng hợp): (1) so sánh trực tiếp truyền thống vs học sâu trên cùng tập test biển Việt Nam, theo kích thước, có CI;
(2) đo đóng góp từng khâu CV trong hệ thống học sâu, kể cả khâu không cải thiện; (3) cải thiện biển nhỏ và ảnh tối khi không thể thêm dữ liệu.

**Bốn bài học** (Kết luận): đo trước khi thêm khâu · xử lý ảnh truyền thống cần điều kiện áp dụng · so sánh công bằng phải tách khâu · con số tổng dễ gây hiểu nhầm.

### 10.2. Biên dịch

```powershell
cd D:\UTCI-Vision\BaoCao\Nhom07
latexmk -xelatex -outdir=build main.tex
# hoặc thủ công: xelatex → biber → xelatex → xelatex
```

Cần XeLaTeX (do `fontspec`) + Biber. VS Code: mở đúng thư mục `BaoCao/Nhom07`, chọn recipe "XeLaTeX + Biber + XeLaTeX x2". PDF ở `build/main.pdf`.
Lỗi `fontspec requires either XeTeX or LuaTeX` = chọn sai engine. Hình được sinh bằng script trong `figures/source/` (không chép tay số).
Ghi chú local trong `note.md`: "chương 2 sửa phát biểu bài toán gộp 2.1.1 2.1.2" — việc còn lại của báo cáo.

---

## 11. Hạn chế và hướng phát triển

### 11.1. Hạn chế (nói chủ động, đừng đợi bị hỏi)

| Hạn chế | Hệ quả khi nói |
|---|---|
| Một lần huấn luyện, một trọng số, một seed | Chưa biết biến động do huấn luyện; CI bootstrap chỉ phản ánh bất định do mẫu test |
| Dữ liệu cùng nguồn, đóng băng; không có tập ngoài phân phối | Dùng nhóm "khác train" làm ước lượng gần hơn; chưa kết luận cho mọi đường phố |
| Lỗi nhãn đã biết (Biển chỉ dẫn hướng đi) | Báo cáo như hạn chế dữ liệu |
| Không có nhãn chữ | Không có CER/khớp chuỗi; OCR định tính |
| Ảnh xấu là giả lập | Chưa kiểm chứng ảnh đêm thật; ngưỡng tối nên chọn lại trên val |
| Không có video đường phố thật | Chưa đo độ ổn định nhãn (E6); webcam GPU chưa đo |
| Val dùng cho nhiều việc | Chọn epoch YOLO và học bộ xác minh |
| Bootstrap theo ảnh | Ảnh trong cùng cụm có thể phụ thuộc → CI có thể hẹp hơn thực tế |
| QCVN 41:2019 đã được thay bằng 41:2024 | Cần rà lại mã hiệu và ý nghĩa |

### 11.2. Hướng phát triển (theo Kết luận)

1. **Dữ liệu:** tập test ngoài phân phối (tuyến đường mới); nhãn chữ để đo CER; định nghĩa lại lớp "Biển chỉ dẫn hướng đi"; thêm ảnh nền khó để học lại bộ xác minh.
2. **Biển nhỏ:** huấn luyện trên ô cắt hoặc độ phân giải cao hơn; thêm đầu phát hiện độ phân giải cao (như các cải tiến trên TT100K).
3. **Ảnh xấu:** chọn lại ngưỡng trên val; chỉ báo nhiễu tốt hơn Laplacian; kiểm chứng ảnh đêm thật.
4. **Video:** đo độ ổn định nhãn có/không theo vết trên video thật; đo webcam GPU.
5. **Mô hình:** nhiều seed; thử YOLO11 cỡ khác; xuất ONNX để chạy nhanh hơn trên CPU (phải kiểm độ đúng sau chuyển đổi).

**Ứng dụng:** kiểm kê biển báo từ video tuyến đường, tra cứu biển trong ảnh. Trước khi dùng cảnh báo người lái cần đánh giá video thật nhiều điều kiện và cập nhật QCVN 41:2024.

---

## 12. Những điểm phải thống nhất trước khi nói

Khi đọc đối chiếu toàn bộ thư mục, có các chỗ chưa khớp. **Không tự sửa báo cáo trong file này**; nhóm cần thống nhất cách nói (và quyết định có sửa báo cáo không).

| # | Điểm | Nguồn | Cách nói an toàn | Mức chắc chắn |
|---|---|---|---|---|
| 1 | Báo cáo viết "tập kiểm thử không tham gia bất kỳ lựa chọn nào", nhưng chọn 1280 px (T3) và tắt bộ xác minh (T1) dựa trên kết quả đo trên test | `chuong2.tex` §Dữ liệu, `chuong3.tex` Bảng `tab:env`; T3/T1 đo trên test | "Trọng số và tham số mô hình chọn trên val; hai quyết định vận hành (1280 px, tắt xác minh) dựa trên phép đo test, nên E1 không hoàn toàn độc lập — đây là giới hạn" | Chắc chắn có mâu thuẫn câu chữ |
| 2 | Nhãn "[CV + DL]" cho bộ xác minh LightGBM | `chuong2.tex` (kiến trúc, E2), phụ lục; `pipeline.yaml` ghi `[CV+ML]` | Nói "CV + ML, có ngữ cảnh YOLO" | Chắc chắn |
| 3 | Hình kiến trúc đặt xác minh **trước** theo vết; mã chạy video theo vết trước, xác minh/OCR chạy nền theo vết | `fig:system_pipeline` vs `pipeline.py` | Giải thích hình là sơ đồ chức năng; tách luồng ảnh tĩnh / video như §6.1 | Chắc chắn |
| 4 | README ghi đọc số "km/h, m, T" | `README.md` vs `chuong2.tex` §Phạm vi | Chỉ km/h và m; T thuộc lớp gộp, không trong phạm vi | Chắc chắn |
| 5 | 9.450 biển train vs 9.449 vùng huấn luyện E8 | `tab:split` vs §E8 | Chưa xác nhận nguyên nhân chênh 1 mẫu; không tự giải thích | Chưa rõ |
| 6 | Test 826 ảnh nhưng nhóm tương đồng cộng lại 779 ảnh (243 + 271 + 265); số biển 667 + 746 + 604 = 2.017 đủ | `fig:similarity`, `similarity.csv` | Khả năng 47 ảnh còn lại là ảnh nền không có biển (53 ảnh nền ở toàn bộ dữ liệu) — **chưa xác minh**; nói "phân tích trên toàn bộ 2.017 biển" | Chưa rõ |
| 7 | Chênh lệch biển lớn E8: báo cáo −10,4 điểm, bàn giao 12/11 ghi −10,5 | `chuong3.tex` vs `docs/handover/2026-11-12` | Dùng số trong báo cáo (−10,4) | Làm tròn khác nhau |
| 8 | Recall nhóm tương đồng "trung bình" (0,875) chỉ có ở bàn giao, báo cáo chỉ nêu hai đầu | handover §4.5 | Chỉ nói hai đầu 0,978 → 0,805 trừ khi đã mở hình | — |
| 9 | Phân công ghi "gán nhãn OCR" nhưng báo cáo nói không có nhãn chữ | `phancong.tex` vs `chuong2.tex` | Phân biệt nhiệm vụ kế hoạch với sản phẩm thực tế; không nói đã có tập nhãn OCR | Chắc chắn |
| 10 | Phụ lục ghi tải dữ liệu vào `dataset/raw`; cấu hình dùng `dataset/merged_dataset_traffic_signs` | `phuluc.tex` vs `configs/data.yaml` | Khi hướng dẫn chạy, theo `configs/data.yaml` | Chắc chắn |
| 11 | 22,5 ms bị gọi là "hệ thống đầy đủ" | `tab:e1` chú thích | Chỉ gồm chất lượng + tăng cường + phát hiện; không gồm OCR, mạng, hiển thị | Chắc chắn |
| 12 | Sprint plan còn ghi "Chương 7 Kết luận", báo cáo Word/LaTeX TBD | `docs/03_SPRINT_PLAN.md` | Báo cáo thực tế là LaTeX 3 chương + Kết luận; sprint plan là kế hoạch cũ | Chắc chắn |
| 13 | Danh mục theo QCVN 41:2019 | `classes.yaml`, báo cáo | Nói "danh mục nhãn của dữ liệu đối chiếu QCVN 41:2019; quy chuẩn đã thay bằng 41:2024, cần rà lại" | Chắc chắn |
| 14 | Mẫu hình thức DA/KLTN ICTU (`reportICTU.cls`) khác lớp `ictureport.cls` đang dùng (lề, giãn dòng) | `guide.md` §15.2 | Hỏi giảng viên mẫu nào áp dụng cho môn; chưa tự đổi | Chắc chắn có khác biệt |
| 15 | Lời cảm ơn còn để trống "ngày …… tháng ……"; bảng phân công có cột chữ ký | `frontmatter/loicamon.tex`, `phancong.tex` | Điền ngày và ký trên bản in trước khi nộp | Chắc chắn |
| 16 | Hình CNN (Hình 1.3) lấy từ web (nguồn InterData) | `chuong1_nentang.tex` | Nếu bị hỏi: hình minh họa có ghi nguồn, không phải hình nhóm vẽ | Chắc chắn |

**Ai chốt:** Hoàn (TV1) chốt cách nói cho #1, #2, #3; Quý (TV4) quyết định có sửa báo cáo cho #4, #9, #12, #14, #15; Dưỡng (TV5) kiểm #5, #6; Minh (TV3) kiểm #10 và README.

---

## 13. Trình bày: bài kiểm tra thường xuyên

Bài kiểm tra thường xuyên chấm theo 10 tiêu chí; bảng dưới chỉ phần nào trong file này dùng cho tiêu chí nào
(`guide.md` có bản chi tiết hơn nhưng không bắt buộc đọc):

| Tiêu chí | Nội dung dùng | Minh họa |
|---|---|---|
| 1. Phương pháp lựa chọn | Bài toán, mục tiêu, kiến trúc hai nhánh | Sơ đồ hệ thống |
| 2–5. Phương pháp (tiếp) | Chất lượng + Gamma/CLAHE · YOLO11s, fine-tune, 960/1280 · HSV–hình dạng–HOG–SVM · theo vết, OCR, xác minh | Ảnh tối trước/sau, T3, mask/contour, crop "40" |
| 6. Độ đo | IoU, TP/FP/FN, P/R/F1, mAP, CI, tốc độ | Ví dụ 10 biển |
| 7–8. Dữ liệu | Nguồn, nhãn, gộp lớp, audit, pHash, chia cụm, EDA | Một nhãn YOLO, bảng chia |
| 9. Hình thức | Bố cục ba chương, hình/bảng/trích dẫn | PDF đã kiểm |
| 10. Trình bày, hỏi đáp | Luồng lập luận, demo có mục đích | §15 |

**Nếu bài kiểm tra tiếp theo tập trung vào kết quả** (Chương 3): dùng §8 làm trục, mỗi thí nghiệm nói theo mẫu
"**câu hỏi → thiết kế → số chính kèm điều kiện → kết luận được phép → giới hạn**". Chọn tối đa 3–4 thí nghiệm (khuyên: T3, T4, E8, T1) thay vì đọc hết.

---

## 14. Trình bày: bảo vệ cuối kỳ — slide, phân vai, kịch bản, demo

> Thời lượng chính thức chưa được xác nhận. Phương án dưới đây: **≈ 15 phút thuyết trình + ≈ 5 phút demo + hỏi đáp**.
> Nếu giảng viên giao ít hơn, cắt theo §14.6. Sprint plan yêu cầu thêm video demo 3–5 phút làm dự phòng.

### 14.1. Nguyên tắc phân vai

- Mỗi người **dẫn** phần gần với việc mình làm, nhưng **ai cũng phải trả lời được mọi phần** (§15). Khi luyện, đổi vai ngẫu nhiên ít nhất một lần.
- Một người **điều phối hỏi đáp** (Hoàn) — nghe câu hỏi, chỉ định người trả lời, bổ sung nếu thiếu; không tranh lời.
- Một người **điều khiển máy demo** (Minh), một người **giữ slide và đồng hồ** (Quý).

### 14.2. Dàn ý 18 slide và phân vai

| # | Slide | Người dẫn | Phút | Thông điệp / điều phải chỉ |
|---|---|---|---|---|
| 1 | Bìa: tên đề tài, nhóm 7, thành viên, GVHD | Quý | 0:20 | — |
| 2 | Bối cảnh và bài toán | Quý | 0:50 | Ảnh đường phố → khung, lớp, số; 3 nhiệm vụ + theo vết |
| 3 | Mục tiêu M1–M4 và phạm vi | Quý | 0:50 | 27 lớp; đọc km/h và m; không đèn/vạch/điều khiển xe |
| 4 | Dữ liệu: nguồn, nhãn, 32 → 27 | Dưỡng | 0:50 | Roboflow CC BY 4.0; nhóm không tự thu; một dòng nhãn YOLO |
| 5 | Chuẩn bị dữ liệu: audit, pHash, chia cụm | Dưỡng | 1:00 | 67 ảnh loại; 3.889 cụm; bảng 3.707/853/826 |
| 6 | EDA: biển nhỏ, mất cân bằng | Dưỡng | 0:50 | 53,7 % < 32 px; chênh 22 lần → dẫn sang thiết kế |
| 7 | Kiến trúc hai hệ thống | Hoàn | 1:00 | Đi một vòng theo mũi tên; CV/ML/DL từng khâu; nhánh đối chứng để so sánh |
| 8 | Đánh giá chất lượng + tăng cường thích nghi | Thịnh | 1:00 | 3 chỉ báo, quy tắc chọn phép; Gamma, CLAHE; ảnh tối trước/sau |
| 9 | YOLO11s: fine-tune, train 960 / suy luận 1280 | Minh | 1:00 | Cấu hình huấn luyện; tắt lật ngang; vì sao 1280 |
| 10 | Pipeline CV truyền thống | Thịnh | 1:15 | HSV → mask → contour → HOG + màu 388 chiều → SVM 27 + nền |
| 11 | Theo vết + đọc số/chữ (+ xác minh tùy chọn) | Minh | 1:00 | Kalman/Hungarian/bỏ phiếu; cắt vùng → VietOCR → regex; "không đoán" |
| 12 | Giao thức đánh giá và độ đo | Hoàn | 1:00 | Ngưỡng 0,25, IoU 0,5; theo kích thước/lớp/tương đồng; CI; ví dụ P/R |
| 13 | S1 + T3: baseline và biển nhỏ | Minh | 0:50 | mAP ≈ 0,89–0,91; lỗi chính là bỏ sót biển < 16 px; 0,634 → 0,737 |
| 14 | T4: ảnh xấu | Thịnh | 0:50 | 0,686 → 0,822; "luôn CLAHE" hại ảnh nhiễu → cần đánh giá chất lượng |
| 15 | E8: thủ công vs học sâu | Hoàn | 1:00 | Nói điều kiện trước: truyền thống được cho vị trí; 91,0 vs 92,4; nút thắt là định vị |
| 16 | T1 + E1: bộ xác minh và hệ thống mặc định | Hoàn | 0:50 | Kết quả âm trung thực; P 0,862 / R 0,917 / F1 0,889 |
| 17 | Hạn chế và hướng phát triển | Dưỡng | 0:50 | OCR định tính, chưa có video thật, một seed, dữ liệu cùng nguồn, QCVN 2024 |
| 18 | Kết luận + chuyển sang demo | Quý | 0:40 | 4 bài học; mời xem demo |
| — | **Demo trực tiếp** | Minh (thao tác), Thịnh (thuyết minh phần CV) | 5:00 | §14.4 |

Tổng thuyết trình ≈ 15 phút. Mỗi người nói 2,5–3,5 phút, cân bằng giữa các thành viên.
**Slide dự phòng** (sau slide cuối, chỉ mở khi bị hỏi): bảng cấu hình huấn luyện; bảng T1 đầy đủ; bảng E8 theo kích thước; bảng tốc độ; recall theo lớp; tương đồng; bảng 27 lớp; HOG 324 chiều; công thức mAP.

### 14.3. Lời nói mẫu (giữ ý và điều kiện, không cần đọc nguyên văn)

- **Quý — mở đầu:** "Biển báo cho biết quy định, cảnh báo và hướng đi. Bài toán của nhóm là từ ảnh hoặc video, tìm vị trí từng biển, cho biết đó là biển gì và đọc số, chữ khi đủ rõ. Khó ở chỗ biển ở xa rất nhỏ, ánh sáng thay đổi và nền đường phố có nhiều vật cùng màu với biển."
- **Dưỡng — sang dữ liệu:** "Trước khi chọn mô hình, nhóm phân tích dữ liệu. Nhóm dùng bộ dữ liệu có sẵn trên Roboflow, việc của nhóm là kiểm tra, lọc, gom ảnh gần trùng và chia lại. Hơn một nửa số biển có cạnh dưới 32 pixel — đặc điểm này quyết định nhiều lựa chọn phía sau."
- **Hoàn — kiến trúc:** "Nhóm tổ chức hai hệ thống. Hệ thống chính lấy YOLO11s làm lõi; các khâu CV truyền thống đứng trước và sau nó, mỗi khâu có công tắc để đo đóng góp riêng. Hệ thống thứ hai chỉ dùng màu, hình dạng, HOG và SVM, để so sánh trực tiếp hai hướng tiếp cận."
- **Thịnh — tăng cường:** "Hệ thống không tăng cường mọi ảnh. Nó đo độ sáng, tương phản, độ nét trước; chỉ ảnh tối mới được Gamma và CLAHE. Lý do nằm ở thí nghiệm T4: áp CLAHE cho mọi ảnh làm recall ảnh nhiễu giảm từ 0,799 xuống 0,706."
- **Minh — YOLO:** "YOLO11s được fine-tune từ trọng số COCO trên tập huấn luyện ở 960 pixel. Khi suy luận nhóm dùng 1280 pixel với cùng trọng số; thí nghiệm T3 cho thấy recall biển dưới 16 pixel tăng từ 0,634 lên 0,737 mà precision không đổi."
- **Hoàn — E8:** "Điều kiện quan trọng: phương pháp truyền thống được cho sẵn vị trí biển, còn YOLO phải tự tìm. Trong điều kiện đó HOG + màu + SVM đạt 91,0 %, YOLO 92,4 %. Nghĩa là đặc trưng thủ công phân loại được; cái nó thiếu là khả năng tìm biển."
- **Hoàn — bộ xác minh:** "Nhóm thử thêm một bộ xác minh bằng đặc trưng thủ công. Ở cùng recall, cải thiện precision chỉ +0,005 và khoảng tin cậy chứa 0, nên nhóm tắt nó mặc định và báo cáo như một kết quả âm."
- **Quý — kết thúc:** "Tóm lại, trong phạm vi dữ liệu đã chọn, tăng cường thích nghi giúp ảnh tối, tăng độ phân giải suy luận giúp biển nhỏ; OCR và theo vết chạy được nhưng chưa đo định lượng. Bài học lớn nhất của nhóm: đo trước khi thêm khâu, và mọi con số phải đi kèm điều kiện đo."

### 14.4. Kịch bản demo 5 phút (ảnh mẫu trong `configs/samples.yaml`)

| Bước | Trang | Ảnh mẫu | Thao tác | Câu nói (một ý) |
|---|---|---|---|---|
| 1 | `/pipeline` | `co_so1` | Chạy một ảnh | "Đây là chỉ số chất lượng, ảnh này đủ sáng nên đi thẳng; YOLO tìm biển, OCR đọc 40 km/h" |
| 2 | `/demo/dl` | `bien_nho1` | Đổi 960 ↔ 1280, xem bảng lịch sử | "Cùng trọng số, 1280 tìm thêm biển nhỏ — đây là T3" |
| 3 | `/demo/dl` | ảnh bất kỳ + "Tối" γ 3,5 | Bật/tắt tăng cường, kéo thanh trước/sau | "Ảnh tối là giả lập; bật tăng cường thì tìm lại được biển — T4" |
| 4 | `/demo/traditional` | `da_dang2` | Xem mask, ứng viên, HOG, SIFT | "Mask màu, ứng viên hình dạng, rồi SVM; biển nhỏ gần như không có điểm SIFT" |
| 5 | `/compare` | `nhieu_bien1` | Chạy hai hệ thống | "YOLO 22 phát hiện, CV 8; khi cho cùng vị trí thì phân loại khớp phần lớn — nút thắt là định vị" |
| 6 (nếu còn giờ) | `/demo/video` | video demo | Chạy job video | "Theo vết gắn mã cho từng biển; đây là minh họa chức năng, chưa đo độ ổn định" |

Quy tắc demo: thay đổi **một** công tắc mỗi lần; giữ cùng ảnh, cùng ngưỡng; nếu OCR không đọc được thì giải thích là thiết kế "để trống thay vì đoán", không ngụy biện.

### 14.5. Chuẩn bị máy demo và phương án dự phòng

**Trước buổi bảo vệ (D−1 và sáng hôm đó):**
- [ ] Máy demo có đủ `models/current/yolo11.pt`, `hog_svm.joblib`, `verifier.joblib`, `models/vietocr/*`, `dataset/processed/v1/test/images`.
- [ ] `make up` (hoặc `make up-gpu`) chạy được, mở http://localhost:18080; `/health` báo 4/4 mô hình.
- [ ] Chạy thử đủ 6 bước demo **trên đúng máy sẽ dùng**, bấm giờ.
- [ ] Docker chạy offline (không phụ thuộc wifi phòng học).
- [ ] Mở sẵn: PDF báo cáo, slide, trang web đã chạy một lần (để nạp mô hình — khởi động mất ≈ 11 s).
- [ ] Không huấn luyện, không cập nhật thư viện, không `git pull` trong ngày bảo vệ.

**Dự phòng (theo thứ tự):** (1) chạy `make dev` thay Docker; (2) video demo 3–5 phút đã quay sẵn; (3) ảnh chụp từng bước demo trong slide dự phòng.
Nói rõ "đây là video quay từ hệ thống" — không trình bày video như chạy trực tiếp.

### 14.6. Nếu bị rút thời gian

- **10 phút:** bỏ slide 1 (gộp vào 2), gộp 5 + 6, gộp 13 + 14, bỏ 11 (nói 1 câu ở slide 7), demo còn bước 1–3–5.
- **5 phút:** giữ bài toán, dữ liệu (1 slide), kiến trúc, T3 + T4, E8, kết luận; demo một bước (`/compare`).
- Không bao giờ cắt **điều kiện đo** khi nói số, cũng không cắt **hạn chế**.

---

## 15. Bảo vệ: nguyên tắc trả lời và bộ câu hỏi

### 15.1. Nguyên tắc

1. **Trả lời theo khung:** kết luận một câu → lý do/bằng chứng (thí nghiệm nào, số nào, điều kiện nào) → giới hạn.
2. **Không chắc thì nói đúng mức:** "phần đã biết là… / số này đo trong điều kiện… / phần này nhóm chưa đo". Không đoán số, không mượn số của thí nghiệm khác.
3. **Không phủ nhận kết quả âm:** bộ xác minh không cải thiện là phát hiện có giá trị, không phải điều cần che.
4. **Không nhận công quá mức:** dữ liệu là của Roboflow; VietOCR pretrained; YOLO là của Ultralytics. Đóng góp của nhóm là tích hợp, kiểm chứng, so sánh, giao thức đánh giá.
5. **Người được hỏi trả lời trước**, người điều phối (Hoàn) chỉ bổ sung khi cần, tối đa một người bổ sung.

### 15.2. Bộ câu hỏi có đáp án

**A. Đề tài và lựa chọn phương pháp**

1. **Đề tài giải quyết những nhiệm vụ nào?** Phát hiện, phân loại biển; đọc số/chữ khi đủ rõ; theo vết với video. Lớp và giá trị số là hai thông tin khác nhau.
2. **Đóng góp chính của nhóm là gì, khi YOLO, VietOCR, dữ liệu đều có sẵn?** Một hệ thống kết hợp chạy đầu–cuối; so sánh có kiểm soát CV truyền thống vs học sâu trên cùng tập test theo kích thước, có CI; đo đóng góp từng khâu kể cả khâu không có ích; hai cách cải thiện biển nhỏ và ảnh tối không cần thêm dữ liệu; giao thức chia cụm chống rò rỉ.
3. **Vì sao không chỉ dùng CV truyền thống?** E8 và so sánh định tính: định vị bằng màu–hình dạng báo nhầm (áo đỏ), gộp biển sát nhau, bỏ biển nhỏ và biển nhiều màu.
4. **Vì sao không chỉ dùng YOLO?** YOLO không đọc số, không liên kết thời gian, kém trên ảnh tối; các khâu thêm vào được đo đóng góp (T4) — khâu không có ích (xác minh) thì tắt.
5. **Vì sao YOLO11s, không Faster R-CNN hay YOLO lớn hơn?** Một giai đoạn, nhanh cho video, có pretrained, vừa GPU nhóm có. Nhóm chưa benchmark đồng điều kiện các detector → không gọi là tối ưu; thử cỡ khác là hướng phát triển.
6. **Fine-tune khác dùng pretrained trực tiếp?** COCO không có 27 lớp biển; fine-tune cập nhật toàn mạng trên dữ liệu của nhóm.
7. **Vì sao tắt lật ngang?** Biển trái/phải (Cấm rẽ trái/phải) đổi nghĩa khi lật; giữ nhãn cũ sẽ sai nhãn.
8. **Vì sao tắt mosaic 15 epoch cuối?** Để mô hình học trên ảnh thật, gần phân phối suy luận ở cuối quá trình; bước tụt loss quanh epoch 66 là do việc này.
9. **Train 960 suy luận 1280 có hợp lệ?** Có; cùng trọng số, kiểm chứng bằng T3; nội suy không tạo chi tiết, biển lớn giảm nhẹ nên không phóng mãi.
10. **CLAHE có luôn tốt?** Không; khuếch đại nhiễu — T4 "luôn áp" làm recall ảnh nhiễu 0,799 → 0,706.
11. **Vì sao chế độ thích nghi lại kém "luôn áp" trên ảnh tối?** Ngưỡng μV < 0,30 bỏ sót 20–32 % ảnh tối; đổi lại không hại ảnh nhiễu/mờ/tốt. Chọn lại ngưỡng trên val là hướng phát triển.
12. **Lọc song phương có tác dụng không?** Chưa có bằng chứng: Laplacian không phân biệt nhiễu với tán lá, nên trong T4 nó không được kích hoạt.
13. **Vì sao HSV mà không RGB?** HSV tách sắc độ khỏi độ sáng, đặt miền màu dễ hơn; vẫn nhạy ánh sáng. Đỏ có hai dải H vì nằm ở hai đầu vòng màu.
14. **Vì sao dùng độ tròn của bao lồi?** Viền đỏ biển cấm là vòng rỗng; đường bao thô có độ tròn thấp; bao lồi khắc phục.
15. **HOG 324 chiều từ đâu?** Ảnh 32×32, ô 8×8 → 4×4 ô; khối 2×2 trượt 1 ô → 3×3 khối; mỗi khối 4 ô × 9 hướng = 36 → 324. Thêm HSV 16×4 = 64 → 388.
16. **SVM có tìm được biển không?** Không; SVM phân loại vùng đã cắt. Vị trí do bước màu + contour tạo ra.
17. **Có lớp nền thì nhận 28 loại biển?** Không; 28 lớp nội bộ = 27 biển + 1 nền để loại ứng viên giả.
18. **Vì sao SIFT kém?** Biển phẳng, ít kết cấu; biển < 16 px có trung vị 1 điểm SIFT. Chỉ kết luận trong thử nghiệm của nhóm.
19. **LightGBM có phải học sâu?** Không; là cây tăng cường (ML).
20. **Precision tăng 0,085 khi bật xác minh, sao không dùng?** Recall giảm 0,052 (biển nhỏ −0,108); ở cùng recall chỉ +0,005, CI chứa 0 → chỉ là dịch điểm vận hành.
21. **Isotonic làm gì?** Hiệu chỉnh điểm thành xác suất phù hợp hơn (ánh xạ không giảm); không tạo đặc trưng, không tự tăng accuracy.
22. **Kalman có phân loại biển?** Không; ước lượng chuyển động khung trên ảnh. Nhãn ổn định nhờ bỏ phiếu trong cửa sổ 10 quan sát.
23. **Theo vết đã giảm nhảy nhãn bao nhiêu?** Chưa đo; thiếu video đường phố thật. Công cụ đo đã có.
24. **OCR có đọc cả ảnh đường phố?** Không; CV cắt vùng → VietOCR đọc → regex/từ điển kiểm.
25. **Độ chính xác OCR là bao nhiêu?** Chưa đo định lượng (không có nhãn chữ). Chỉ có ví dụ định tính 40/60 km/h, 2,0 m.
26. **Vì sao không fine-tune VietOCR?** Không có nhãn chữ (dữ liệu đóng băng); backlog chỉ làm khi đo được độ khớp < 80 %.
27. **Từ điển có làm chữ luôn đúng?** Không; có thể sửa sai tên riêng. Vì vậy lưu cả chuỗi gốc, ngưỡng tương đồng 80/100.

**B. Dữ liệu và đánh giá**

28. **Vì sao 32 lớp gốc mà mô hình 27 lớp?** 26 giữ + 6 gộp thành 1 = 27; tiêu chí < 60 cụm cảnh (ADR-009).
29. **Lớp "Biển báo khác" nhận được biển lạ không?** Không; là lớp gộp 6 loại cụ thể có dữ liệu huấn luyện.
30. **Nhóm tự thu dữ liệu?** Không; dùng nguồn công bố, nhóm làm kiểm tra, lọc, gom cụm, ánh xạ, chia, đóng gói.
31. **pHash là gì, vì sao ngưỡng 6?** Băm cảm nhận 64 bit; Hamming đếm bit khác; ≤ 6 coi là gần trùng; cụm nối bắc cầu. Không bảo đảm bắt mọi quan hệ cùng tuyến đường → có phân tích theo mức tương đồng.
32. **Val khác test?** Val để chọn trong phát triển; test để đánh giá cuối. (Lưu ý §12 #1 về T3/T1.)
33. **mAP khác accuracy?** mAP tóm tắt đường P–R theo lớp khi ghép khung với IoU; accuracy chỉ có nghĩa khi tập đơn vị mẫu xác định (vùng cắt E8). Detection không có số "nền đúng" hữu hạn để tính accuracy.
34. **Vì sao thư viện 0,905 mà nhóm tính 0,892?** Khác cách đệm ảnh khi suy luận; báo cáo nêu cả hai, khoảng 0,89–0,91.
35. **Vì sao precision 0,920 và 0,860?** 0,920 ở ngưỡng tối ưu F1 của thư viện; 0,860 ở ngưỡng hiển thị 0,25 mà người dùng thấy.
36. **CI chứa 0 nghĩa là hai phương pháp bằng nhau?** Không; chỉ là chưa đủ bằng chứng khác biệt.
37. **Bootstrap theo ảnh có hạn chế gì?** Ảnh cùng cụm có thể phụ thuộc → CI có thể hẹp; CI không phản ánh biến động giữa các lần huấn luyện (chỉ một seed).
38. **Kết quả có tổng quát cho đường phố khác?** Chưa chứng minh; nhóm "khác train" recall 0,805, precision 0,749 — ước lượng gần hơn cho đường mới; cần tập ngoài phân phối.
39. **Có quá khớp không?** Loss val không tăng lại, val ≈ test → chưa thấy dấu hiệu qua đường cong; không khẳng định loại trừ hoàn toàn.
40. **Vì sao số lượng mẫu ít mà lớp hiếm vẫn tốt?** Tương quan số cụm và recall yếu (Spearman 0,16–0,32); nhưng CI lớp hiếm rộng vì chỉ 23–31 biển.

**C. Hệ thống, triển khai, quy trình**

41. **Hệ thống chạy thời gian thực chưa?** Khâu phát hiện 22,5 ms/ảnh trên RTX 4060 (≈ 44 FPS lý thuyết cho riêng khâu này); webcam đầu cuối trên CPU 3,5–9,3 FPS; webcam GPU qua web **chưa đo**.
42. **Vì sao ảnh qua API mất 0,9–1,6 s?** Docker CPU, có OCR (VietOCR chạy CPU); khác cấu hình với số GPU.
43. **Vì sao cần Docker?** Môi trường nhất quán CPU/GPU, chạy offline, ai cũng khởi động bằng một lệnh.
44. **Video và webcam khác ảnh tĩnh thế nào trong pipeline?** Phát hiện + theo vết mỗi khung; xác minh/OCR chạy nền theo vết khi vết mới hoặc sau 10 khung.
45. **Làm sao bảo đảm số liệu không chép tay?** Mọi lần chạy ghi `experiments/registry.csv`; biểu đồ sinh bằng script từ cùng tệp kết quả; Phụ lục có bảng lệnh tái lập từng bảng/hình.
46. **Nhóm làm việc thế nào?** Scrum 6 sprint × 1 tuần, Trello, Git flow (nhánh feature → PR vào `develop`), CI, ADR ghi quyết định, SRS cập nhật liên tục.
47. **Giấy phép Ultralytics ảnh hưởng gì?** AGPL-3.0: đồ án học thuật ghi nguồn; nếu thương mại hóa phải tuân AGPL hoặc mua giấy phép.
48. **Nhóm có dùng công cụ AI hỗ trợ không?** Trả lời trung thực theo thực tế của nhóm (hồ sơ bàn giao ghi được lập với trợ giúp của Claude Code). Nhấn mạnh: số liệu đến từ các lần chạy có ghi nhận, nhóm kiểm và hiểu từng bước — chính là lý do có tài liệu này.
49. **Danh mục biển còn đúng quy chuẩn hiện hành?** Theo QCVN 41:2019; đã được thay bằng 41:2024 từ 01/01/2025 → cần rà lại; đã ghi trong Hạn chế.
50. **Nếu có thêm 1 tháng, làm gì trước?** Nhãn chữ để đo OCR; video thật để đo theo vết; tập ngoài phân phối; nhiều seed. Ưu tiên đo được trước khi thêm mô hình.

**D. Lý thuyết nền (Chương 1) — giảng viên hay hỏi để kiểm tra hiểu bài**

51. **AI, ML, DL quan hệ thế nào?** DL ⊂ ML ⊂ AI. ML học quy luật từ dữ liệu; DL dùng mạng nhiều lớp học luôn cách biểu diễn. Trong đề tài: luật màu/hình = quy tắc; HOG + SVM = ML; YOLO = DL.
52. **Đề tài thuộc hình thức học nào?** Có giám sát (ảnh + nhãn lớp/khung). Gom cụm pHash để kiểm tra dữ liệu mang tính không giám sát.
53. **Phân loại, phát hiện, phân đoạn, theo dõi khác nhau?** Phân loại: loại gì; phát hiện: loại gì + ở đâu (khung); phân đoạn: điểm ảnh nào thuộc vùng; theo dõi: liên kết qua thời gian. Mặt nạ HSV là phân đoạn; YOLO là phát hiện; SVM trên vùng cắt là phân loại; Kalman là theo dõi.
54. **Lấy mẫu khác lượng tử hóa?** Lấy mẫu = chia lưới vị trí (số điểm ảnh); lượng tử hóa = số mức cường độ (số bit). Tăng sáng không khôi phục được vùng đã bão hòa hoặc tối mất chi tiết.
55. **Tích chập trong CNN làm gì?** Bộ lọc nhỏ k×k trượt trên ảnh, nhân–cộng với vùng lân cận, cộng bias, qua hàm kích hoạt (ReLU = max(0, z)). Dùng chung trọng số ở mọi vị trí → nhận cùng một mẫu ở nhiều chỗ, ít tham số.
56. **Pooling / giảm độ phân giải ảnh hưởng biển nhỏ ra sao?** Giảm tính toán nhưng có thể làm mất nét của vật nhỏ → lý do suy luận 1280 px giúp biển nhỏ.
57. **Vùng tiếp nhận là gì?** Phần ảnh đầu vào ảnh hưởng tới một giá trị đặc trưng; lớp sâu có vùng rộng hơn, nhưng không giữ được chi tiết đã mất khi giảm độ phân giải.
58. **Mạng học thế nào?** Hàm mất mát đo sai khác; lan truyền ngược tính gradient; cập nhật θ ← θ − η∇L trên từng lô. 1 epoch = 1 lượt qua tập train. η quá lớn dao động, quá nhỏ học chậm (nhóm dùng AdamW, lr 0,001, cosine, warm-up).
59. **Học chuyển giao và fine-tune?** Dùng biểu diễn học từ dữ liệu nguồn (COCO) cho nhiệm vụ mới; fine-tune = tiếp tục cập nhật một phần hoặc toàn mạng (nhóm cập nhật toàn mạng).
60. **Quá khớp là gì, phòng thế nào?** Học thuộc chi tiết riêng của train, kém trên mẫu mới; dấu hiệu: loss train giảm, val không cải thiện/tăng. Phòng: tăng cường dữ liệu giữ nhãn, giới hạn độ phức tạp, dừng sớm/chọn epoch theo val.
61. **Hai giai đoạn và một giai đoạn khác nhau?** Faster R-CNN: mạng đề xuất vùng (RPN) rồi phân loại + hiệu chỉnh khung; YOLO: dự đoán khung và lớp trực tiếp trong một lần truyền → nhanh, hợp video.
62. **RGB, HSV, Lab dùng vào đâu?** RGB lưu ảnh (OpenCV đọc thứ tự **BGR**); HSV tách sắc màu để lấy ngưỡng đỏ/xanh/vàng; Lab tách độ sáng L khỏi màu a*, b* → CLAHE trên L ít làm lệch màu.
63. **Nội suy và letterbox?** Đổi kích thước phải ước lượng giá trị mới (láng giềng gần nhất, song tuyến tính…). Ép ảnh chữ nhật thành vuông làm tròn thành elip; giữ tỉ lệ + đệm thì phải nhớ tỉ lệ và độ lệch để đổi tọa độ khung về ảnh gốc. Mặt nạ nhãn không nên nội suy tạo giá trị trung gian.
64. **Histogram cho biết gì, không cho biết gì?** Số điểm ảnh ở mỗi mức cường độ; hẹp → tương phản thấp. Không cho biết điểm sáng/tối nằm ở đâu.
65. **Cân bằng histogram toàn ảnh khác CLAHE?** Toàn ảnh dùng một phép chung; CLAHE theo vùng cục bộ, cắt histogram trước khi cân bằng, nội suy giữa các vùng để tránh ranh giới giả.
66. **Lọc trung bình, Gaussian, trung vị, song phương?** Trung bình: làm mờ cả biên; Gaussian: trọng số lớn ở tâm; trung vị: tốt với nhiễu xung (muối tiêu); song phương: xét cả khoảng cách và chênh cường độ → giữ biên tốt hơn, tốn thời gian hơn.
67. **Gradient, Sobel, Laplacian?** Gx, Gy là đạo hàm theo hai hướng; độ lớn m = √(Gx² + Gy²), hướng α = atan2(Gy, Gx). Sobel ước lượng đạo hàm bậc 1; Laplacian dùng đạo hàm bậc 2. Nhiễu và vân nền cũng tạo đáp ứng lớn → vì vậy phương sai Laplacian không phải thước đo nhiễu đáng tin.
68. **Co, giãn, mở, đóng?** Co thu hẹp vùng trắng, giãn mở rộng; mở = co rồi giãn (xóa đốm nhỏ); đóng = giãn rồi co (lấp lỗ, nối khe). Phần tử cấu trúc phải hợp với chi tiết cần giữ.
69. **Moment và Hu?** m_pq = Σ xᵖ yᵠ M(x, y); m₀₀ = diện tích; tâm = (m₁₀/m₀₀, m₀₁/m₀₀). 7 moment Hu bất biến tịnh tiến, tỉ lệ, quay trong mô hình lý tưởng; trên ảnh thật vẫn thay đổi do nhiễu, che khuất; Hu thứ 7 đổi dấu khi phản chiếu.
70. **Miền tần số liên quan gì tới đề tài?** Nền đều = tần số thấp; biên, nét mảnh, nhiễu = tần số cao. Làm trơn giảm nhiễu nhưng yếu biên. **pHash** dùng DCT, lấy hệ số tần số thấp so với trung vị để tạo bit → so bố cục ảnh gần trùng.
71. **PCA làm gì?** Trừ trung bình, tính ma trận hiệp phương sai, lấy r vector riêng có trị riêng lớn nhất, chiếu z = U_rᵀ(x − μ). Không dùng nhãn → phương sai lớn không đồng nghĩa phân loại tốt. Phải fit trên train, không fit trên test. Bộ xác minh giữ 16 thành phần HOG.
72. **SVM, cây quyết định, Random Forest, LightGBM khác nhau?** SVM: ranh giới biên lớn, kernel RBF cho ranh giới phi tuyến, cần chuẩn hóa đặc trưng. Cây: câu hỏi theo ngưỡng đặc trưng, sâu dễ theo nhiễu. RF: nhiều cây độc lập có ngẫu nhiên. LightGBM: tăng cường — cây mới sửa sai số còn lại của mô hình hiện tại; chia giá trị thành khoảng để nhanh.
73. **Điểm 0,8 có phải xác suất 80 %?** Chưa chắc; cần hiệu chỉnh (ví dụ isotonic) trên dữ liệu thích hợp. Hiệu chỉnh khác với chọn ngưỡng.
74. **Vì sao đặc trưng cục bộ (SIFT) kém trên biển nhỏ, còn HOG ổn?** SIFT cần điểm nổi bật ổn định; vùng nhỏ, phẳng không có đủ điểm. HOG mô tả toàn vùng bằng hướng nét theo ô, không cần điểm khóa.

### 15.3. Câu hỏi về đóng góp cá nhân (mỗi người chuẩn bị 1 phút)

| Thành viên | Phải nói được |
|---|---|
| Hoàn | Thiết kế giao thức đánh giá, T0/T1, E8, vì sao tắt bộ xác minh; vai trò review |
| Thịnh | Tăng cường thích nghi, pipeline CV đối chứng, tracking, cắt vùng OCR; các trang React |
| Minh | Notebook fine-tune, cấu hình huấn luyện, T3, tích hợp VietOCR, FastAPI/WebSocket, Docker |
| Quý | Cấu trúc báo cáo, nội dung biển/QCVN, slide, video; phần cùng kiểm thử, đánh giá |
| Dưỡng | Audit, pHash, chia cụm, đóng gói, EDA; benchmark, kiểm thử chấp nhận |

Sau đó mỗi người nói thêm **một câu nối phần mình với phần của người khác** (ví dụ Dưỡng: "chia theo cụm là lý do nhóm có thể tin con số E1 của Hoàn").

---

## 16. Lịch luyện tập và phiếu tự kiểm tra

### 16.1. Lịch đề xuất (hôm nay 20/11; bảo vệ dự kiến tuần 27/11–04/12)

| Ngày | Việc | Ai |
|---|---|---|
| 20–21/11 | Mỗi người đọc file này; ghi câu chưa hiểu vào nhóm chat | Cả nhóm |
| 22/11 | **Buổi 1:** mỗi người tự vẽ pipeline, nói 2 phút; chốt 14 điểm ở §12 | Cả nhóm, Hoàn chủ trì |
| 23–24/11 | Quý làm slide theo §14.2; mỗi người viết ghi chú nói cho slide mình | Quý + từng người |
| 25/11 | **Buổi 2:** tính tay ví dụ P/R/F1, IoU, HOG 324; đọc 4 bảng (T3, T4, E8, T1) có điều kiện | Cả nhóm |
| 26/11 | Minh + Dưỡng kiểm máy demo (§14.5); Thịnh + Minh quay video demo dự phòng | Minh, Dưỡng, Thịnh |
| 28/11 | **Diễn tập 1:** bấm giờ toàn bài, chưa demo | Cả nhóm |
| 01/12 | **Diễn tập 2:** demo trực tiếp + hỏi đáp ngẫu nhiên 15 câu §15 (người hỏi chỉ định người trả lời) | Cả nhóm |
| 02–03/12 | Sửa slide theo diễn tập; luyện câu mỗi người còn yếu | Cả nhóm |
| Ngày bảo vệ | Kiểm máy sớm 30 phút; không thay đổi mã | Minh, Dưỡng |

### 16.2. Phiếu tự kiểm tra (mỗi người tự đánh dấu, không ai được bỏ mục nào)

- [ ] Nói được đề tài trong 30 giây và trong 2 phút (§2.2–2.3).
- [ ] Giải thích được 32 lớp gốc, 27 lớp mô hình, 28 lớp nội bộ SVM.
- [ ] Nói đúng phạm vi đọc số: km/h và m, không có T.
- [ ] Nói đúng đóng góp dữ liệu của nhóm; giải thích được vì sao chia theo cụm pHash.
- [ ] Tự vẽ được pipeline chính và pipeline đối chứng; biết khâu nào CV, ML, DL.
- [ ] Phân biệt luồng ảnh tĩnh và luồng video (tác vụ nền theo vết).
- [ ] Giải thích được quy tắc tăng cường thích nghi và vì sao "chỉ khi cần".
- [ ] Giải thích được train 960 / suy luận 1280; tắt lật ngang.
- [ ] Tính được HOG 324 + HSV 64 = 388.
- [ ] Tự tính được IoU, TP/FP/FN, P/R/F1 từ ví dụ.
- [ ] Không gọi mAP là accuracy; không coi confidence là độ chính xác.
- [ ] Thuộc 10 con số §2.4 **kèm điều kiện đo**.
- [ ] Nói được điều kiện của E8 trước khi nói 91,0 / 92,4.
- [ ] Nói được vì sao bộ xác minh tắt (T1, cùng recall, CI chứa 0).
- [ ] Không khẳng định đã đo OCR, theo vết, webcam GPU.
- [ ] Nêu được ít nhất 4 hạn chế và 3 hướng phát triển.
- [ ] Biết cách nói an toàn cho các điểm ở §12.
- [ ] Chạy được demo bước 1–5 hoặc thuyết minh được khi người khác thao tác.
- [ ] Trả lời được ít nhất 60/74 câu ở §15 (gồm nhóm D lý thuyết) không nhìn tài liệu.
- [ ] Khi giảng viên chỉ một số hình/bảng bất kỳ (ví dụ "Hình 3.8"), nói được hình đó trình bày gì và kết luận gì (§20).

---

## 17. Bảng tra nguồn nhanh

| Cần tra | Mở |
|---|---|
| Báo cáo (nguồn chính thức của mọi số) | `BaoCao/Nhom07/chapters/{modau,chuong2,chuong3,ketluan,phuluc}.tex`; PDF `BaoCao/Nhom07/build/main.pdf` |
| Guide bài kiểm tra 2 (công thức, 10 tiêu chí) | `BaoCao/Nhom07/guide.md` |
| Phân công, bìa | `BaoCao/Nhom07/frontmatter/phancong.tex`, `metadata.tex` |
| Cấu hình chạy, 27 lớp | `configs/pipeline.yaml`, `configs/classes.yaml`, `configs/ocr.yaml`, `configs/data.yaml` |
| Luồng ảnh/video thực tế | `src/utci_vision/pipeline.py` |
| S1 | `docs/danh_gia/S1_baseline_yolo11s_960.md` + thư mục CSV cùng tên |
| T0/T1 | `docs/danh_gia/S3_T0_T1_kha_thi_bo_xac_minh.md` |
| E8/T4 | `docs/danh_gia/S3_E8_T4_phuong_phap_truyen_thong.md` |
| E1/E2/E4/T3 | `docs/danh_gia/S3_danh_gia_he_thong.md`, `docs/danh_gia/S3_he_thong/*.csv` |
| Dữ liệu | `docs/data/DATA_CARD.md`, `docs/data/review/` |
| Quyết định kiến trúc | `docs/adr/ADR-001…009` |
| Yêu cầu, kế hoạch | `docs/02_SRS.md`, `docs/03_SPRINT_PLAN.md`, `docs/00_PHUONG_AN.md`, `docs/04_BAO_CAO_DE_XUAT.md` |
| Lịch sử, kịch bản demo gốc | `docs/handover/2026-11-12_ban_giao.md` (§7 demo), `2026-11-13_bao_cao.md` |
| Tài liệu tham khảo đã xác thực | `docs/research/README.md`, `docs/research/tai_lieu_bao_cao.md` |
| Sổ đăng ký thí nghiệm | `experiments/registry.csv` |
| Chạy trên Windows | `docs/HUONG_DAN_CHAY_WINDOWS.md` |

Khi báo cáo hoặc cấu hình thay đổi, kiểm lại con số ở đây trước khi dùng để nói. Không thay một số trong kịch bản bằng số đẹp hơn từ thí nghiệm khác mà bỏ mất điều kiện đo.

---

## 18. Lý thuyết nền — tóm tắt Chương 1

Chương 1 (`chuong1_nentang.tex`) không trình bày cái mới của nhóm, nhưng là nơi giảng viên hỏi để kiểm tra **hiểu bài**. Mỗi mục dưới đây có dòng "**Trong đề tài:**" để nối lý thuyết với hệ thống — luôn nói kèm dòng đó.

### 18.1. AI, ML, DL và thị giác máy tính

- **AI** xây hệ thống nhận biết, suy luận, học từ dữ liệu, ra quyết định trong phạm vi nhiệm vụ. **ML** ⊂ AI: mô hình học quy luật từ dữ liệu. **DL** ⊂ ML: mạng nơ-ron nhiều lớp học luôn cách biểu diễn (Hình 1.1).
- Ba cách nhận diện một vùng biển: (1) quy tắc "vùng đỏ gần tròn"; (2) tính đặc trưng màu/hình rồi học bộ phân loại; (3) mạng sâu học đặc trưng trực tiếp từ ảnh.
- **Xử lý ảnh** tạo ra ảnh mới (giảm nhiễu, tăng tương phản); **thị giác máy tính** dùng thông tin đó để mô tả đối tượng và cảnh.
- Bốn bài toán cơ bản: **phân loại** (loại gì), **phát hiện** (loại gì + ở đâu), **phân đoạn** (điểm ảnh nào thuộc vùng), **theo dõi** (liên kết qua khung hình). OCR thêm bước chuyển chữ/số thành văn bản.
- **Trong đề tài:** quy tắc = lọc hình dạng; ML = HOG + SVM, LightGBM; DL = YOLO11s, VietOCR.

### 18.2. Thu nhận ảnh

- **Lấy mẫu** chia mặt phẳng ảnh thành lưới vị trí; **lượng tử hóa** biểu diễn mức sáng bằng số mức hữu hạn (số bit). Hai bước khác nhau.
- Diện mạo phụ thuộc bề mặt, nguồn sáng, cách ghi hình. Vùng đã bão hòa trắng hoặc mất chi tiết trong tối thì **tăng sáng không tạo lại nét**.
- Chuyển động khi phơi sáng → mờ; lấy nét sai → biên loang; nén → khối. **Độ phân giải không phải tiêu chí duy nhất**: ảnh lớn mà mờ có thể ít thông tin hơn vùng nhỏ nét.
- **Trong đề tài:** giải thích vì sao ảnh tối giả lập khác ảnh đêm thật, và vì sao phóng ảnh không tạo chi tiết.

### 18.3. Học máy

- **Bốn hình thức học** (Bảng 1.1, Hình 1.2): có giám sát (có nhãn) · không giám sát (tìm cấu trúc, ví dụ phân cụm) · bán giám sát (kết hợp; ví dụ nhãn giả) · tăng cường (học hành động qua phần thưởng).
  **Trong đề tài:** phân loại/phát hiện biển = có giám sát; gom cụm pHash để kiểm tra dữ liệu = không giám sát.
- **Quy trình:** xác định đầu vào/nhãn → kiểm tra dữ liệu → chọn biểu diễn → huấn luyện → đánh giá trên mẫu độc lập. Chất lượng nhãn và cách chia ảnh hưởng trực tiếp độ tin cậy.
- **Các mô hình:**
  - **SVM:** ranh giới biên lớn; mẫu gần biên (vector hỗ trợ) quyết định; kernel → ranh giới phi tuyến; chấp nhận sai một số mẫu khó (tham số C); **cần chuẩn hóa** vì đặc trưng có thang lớn sẽ chi phối khoảng cách.
  - **Cây quyết định:** chuỗi câu hỏi theo ngưỡng đặc trưng; cây sâu dễ theo nhiễu. **Random Forest:** nhiều cây học với ngẫu nhiên mẫu/đặc trưng, lấy tổng hợp.
  - **LightGBM (tăng cường cây):** cây mới được xây để giảm sai số còn lại của mô hình hiện tại (khác RF: cây không độc lập); chia giá trị thành khoảng rời rạc để nhanh, ít bộ nhớ. Thêm cây/lá không tự bảo đảm tốt hơn.
  - **Điểm dự đoán ≠ xác suất:** nhóm mẫu có điểm 0,8 có thể chỉ đúng ít hơn 80 %; **hiệu chỉnh** kiểm tra và điều chỉnh quan hệ đó (khác với chọn ngưỡng).
- **Chia dữ liệu:** train học tham số; val chọn mô hình, siêu tham số, ngưỡng; test đánh giá sau khi đã chốt. Chuẩn hóa/PCA chỉ fit trên train.
- **Quá khớp:** train giảm mà val không cải thiện; giảm bằng giới hạn độ phức tạp, tăng cường dữ liệu, dừng sớm. Cả hai tập đều kém → xem lại biểu diễn/dữ liệu.
- Ảnh cùng đoạn video gần trùng → chia theo video/phiên/cụm. Dữ liệu dùng huấn luyện **bất kỳ thành phần nào** phải tách khỏi test của toàn hệ thống.
- **Bảng 1.2 (ML truyền thống vs DL):** ML truyền thống dùng đặc trưng do người thiết kế, cần ít dữ liệu, nhanh, dễ giải thích; DL tự học biểu diễn, cần nhiều dữ liệu và GPU, mạnh trên cảnh phức tạp.

### 18.4. Mạng nơ-ron và CNN

- **Nơ-ron:** y = φ(wᵀx + b); φ tạo phi tuyến, ví dụ **ReLU φ(z) = max(0, z)**.
- **Tích chập (một kênh, bước 1):** Y(i, j) = φ(b + Σᵤ Σᵥ K(u, v)·X(i+u, j+v)). Bộ lọc k×k **dùng chung trọng số** ở mọi vị trí → nhận cùng một mẫu ở nhiều chỗ. Thư viện gọi là tích chập nhưng thực chất là tương quan chéo.
- Lớp đầu học mẫu cục bộ (nét ngang/dọc), lớp sau kết hợp thành hình rộng hơn. Bước trượt, phần đệm điều chỉnh kích thước bản đồ đặc trưng; **gộp (pooling)** giảm độ phân giải → giảm tính toán nhưng **có thể mất chi tiết vật nhỏ**.
- **Vùng tiếp nhận:** phần ảnh ảnh hưởng tới một giá trị đặc trưng; mở rộng qua các lớp, nhưng không cứu được chi tiết đã mất.
- Dùng chung bộ lọc ≠ bất biến với mọi biến đổi: đổi tỉ lệ, xoay mạnh, ánh sáng, che khuất vẫn làm dự đoán thay đổi.
- Đầu ra phân loại tổng hợp cả vùng; đầu ra phát hiện phải giữ thông tin vị trí → hai kiểu tổ chức phần dự đoán khác nhau (Hình 1.3: CNN phân loại điển hình gồm phần trích đặc trưng + phần ra lớp).
- **Trong đề tài:** giải thích vì sao biển < 16 px khó và vì sao suy luận 1280 px giúp.

### 18.5. Nguyên lý học

- **Hàm mất mát** đo sai khác dự đoán – nhãn; **lan truyền ngược** tính gradient; cập nhật trên lô: **θₜ₊₁ = θₜ − η∇L(θₜ)**. 1 **epoch** = 1 lượt qua toàn tập train. η lớn → dao động; nhỏ → chậm.
- Mất mát phân loại liên quan lớp; mất mát định vị liên quan khung. **Mất mát giảm không có nghĩa mọi nhóm lỗi giảm như nhau** (ví dụ biển nhỏ).
- **Tăng cường dữ liệu** phải giữ nhãn: lật ngang biển có hướng tạo lớp khác → nhóm tắt lật ngang.
- **Học chuyển giao / fine-tune:** dùng biểu diễn học từ dữ liệu nguồn; có thể đóng băng bộ trích đặc trưng hoặc cập nhật toàn bộ. Trọng số pretrained không thay được ví dụ biển nhỏ, ảnh mờ, ban đêm.
- **Trong đề tài:** fine-tune toàn mạng YOLO11s từ COCO, AdamW, lr 0,001, cosine, 3 epoch warm-up, chọn epoch theo val.

### 18.6. Phát hiện đối tượng

- **Hai giai đoạn — Faster R-CNN:** mạng đề xuất vùng (RPN) chia sẻ đặc trưng với mạng phát hiện; vùng đề xuất được phân loại và hiệu chỉnh khung.
- **Một giai đoạn — YOLO:** dự đoán khung và lớp trực tiếp từ đặc trưng ảnh, hợp xử lý liên tiếp nhiều khung. Cấu trúc lưới của YOLOv1 không mô tả chung cho mọi phiên bản sau. (Bài 9 của học phần.)
- Kết quả phụ thuộc dữ liệu, kích thước đầu vào, biến thể, phần cứng → phải xét cùng lúc định vị, phân loại, thời gian.

### 18.7. Xử lý ảnh số

**Không gian màu (Bảng 1.3, Hình 1.4):**

| Không gian | Thành phần | Dùng trong đề tài |
|---|---|---|
| RGB (OpenCV đọc **BGR**) | Đỏ, lục, lam; 8 bit 0–255 | Ảnh đầu vào; phải thống nhất thứ tự kênh trước khi hiển thị/đưa vào mô hình |
| HSV | Sắc màu H (tuần hoàn — đỏ ở hai đầu), bão hòa S, độ sáng V | Ngưỡng màu đỏ/xanh/vàng; μV để đo ảnh tối; histogram HSV 16×4 |
| Lab | Độ sáng L*, trục a* (lục–đỏ), b* (lam–vàng) | CLAHE trên L; σL để đo tương phản |

Trong Hình 1.4, các kênh hiển thị bằng thang xám: sáng = giá trị kênh cao. Đó là cách xem từng kênh, **không phải ảnh bị mất màu**; với kênh H, giá trị cao không có nghĩa màu sáng hơn.

**Đổi kích thước và cắt vùng:**
- Nội suy láng giềng gần nhất / song tuyến tính / theo diện tích khi thu nhỏ. Thu nhỏ làm nét mảnh trộn vào nền; phóng to không thêm chi tiết.
- Ép chữ nhật thành vuông làm tròn thành elip → giữ tỉ lệ + đệm (letterbox), lưu tỉ lệ và độ lệch để đổi tọa độ về ảnh gốc.
- Vùng cắt quá hẹp mất viền/ký tự; quá rộng đưa nền vào. Mặt nạ nhãn không nên dùng nội suy tạo giá trị trung gian.

**Chất lượng và độ sáng:**
- Độ sáng TB, độ phân tán cường độ (tương phản), phương sai Laplacian (dấu hiệu độ nét — nhưng nhiễu và nền nhiều chi tiết cũng làm nó tăng).
- **Histogram** đếm điểm ảnh theo mức; hẹp → tương phản thấp; **không cho biết vị trí** sáng/tối.
- **Gamma:** s = r^(1/γ), r ∈ [0, 1]; γ > 1 sáng lên, 0 < γ < 1 tối đi; 0 và 1 giữ nguyên. Phải nêu quy ước vì có tài liệu viết số mũ trực tiếp là γ (chiều tác động đảo lại). Ví dụ r = 0,25, γ = 2 → s = 0,5.
- **Cân bằng histogram toàn ảnh** dùng một phép chung; **CLAHE** chia vùng, cắt histogram trước khi cân bằng, ghép kết quả để tránh ranh giới giả, hạn chế khuếch đại nhiễu.

**Lọc và biên (Bảng 1.4):**

| Phép lọc | Cách xử lý | Lưu ý |
|---|---|---|
| Trung bình | Trung bình lân cận | Giảm dao động nhưng mờ biên |
| Gaussian | Trọng số theo khoảng cách tới tâm | Cửa sổ/σ lớn → mất cấu trúc nhỏ |
| Trung vị | Lấy giá trị giữa trong cửa sổ | Tốt với nhiễu xung; cửa sổ lớn xóa nét mảnh |
| Song phương | Xét cả khoảng cách và chênh cường độ | Giữ biên tốt hơn; phụ thuộc tham số, tốn thời gian |

- **Gradient:** Gx, Gy; độ lớn **m = √(Gx² + Gy²)**; hướng **α = atan2(Gy, Gx)** (hướng tăng cường độ mạnh nhất, không phải hướng đường biên). Sobel ước lượng đạo hàm bậc 1; **Laplacian** dùng đạo hàm bậc 2.
- Biên thật, nhiễu, vân nền đều cho đáp ứng lớn; đáp ứng có dấu phải lưu đúng kiểu số (không ép ngay về số nguyên không dấu). Ảnh biên chưa phải kết luận về lớp.

**Phân vùng và hình dạng (Hình 1.5):**
- Phân vùng tách vùng có ý nghĩa (mặt nạ đỏ, vùng sáng chứa chữ); ngưỡng màu đơn giản nhưng nhạy ánh sáng, bóng đổ. Ảnh biên có thể rời rạc, chưa thành đường bao kín.
- **Hình thái học** (phần tử cấu trúc): co thu hẹp vùng trắng, giãn mở rộng; **mở = co → giãn** (xóa đốm); **đóng = giãn → co** (lấp lỗ, nối khe). Hình 1.5 hàng trên: 4 phép trên một ảnh nhị phân kernel 3×3; hàng dưới: đường bao (đỏ), khung bao (xanh đứt), tâm (chấm đen) của các hình mẫu — hàng dưới **không phải** kết quả của hàng trên.
- Từ đường bao: diện tích, chu vi, tâm, số đỉnh sau xấp xỉ đa giác. **Độ tròn C = 4πA/P²** (tròn lý tưởng = 1). Tỉ lệ rộng/cao, **độ đặc** (diện tích / diện tích bao lồi). Mức sai lệch khi xấp xỉ đa giác ảnh hưởng số đỉnh đếm được. Góc nghiêng làm tròn thành elip → kết hợp nhiều đặc trưng, không dùng một ngưỡng cứng.
- **Moment:** m_pq = Σ Σ xᵖ yᵠ M(x, y); m₀₀ = diện tích; tâm (m₁₀/m₀₀, m₀₁/m₀₀); trừ tâm → bất biến tịnh tiến; chuẩn hóa → giảm ảnh hưởng tỉ lệ. **7 moment Hu** bất biến tịnh tiến, tỉ lệ, quay (lý tưởng); trên ảnh thật vẫn đổi do nội suy, nhiễu, che khuất; Hu thứ 7 đổi dấu khi phản chiếu.

**Miền tần số (Bài 2):**
- Nền đồng đều ↔ tần số thấp; biên, nét mảnh, một phần nhiễu ↔ tần số cao.
- **Fourier (DFT)** dùng sin/cos; biên độ = mức đóng góp, pha = sắp xếp trong không gian (chỉ biên độ thì không tái tạo được vị trí).
- **DCT** biểu diễn bằng tổng cosin; năng lượng tập trung ở hệ số thấp → biểu diễn gọn; bỏ hệ số cao có thể mất nét nhỏ.
- Không phải mọi tần số cao là nhiễu. **Trong đề tài:** pHash dùng hệ số DCT thấp để so bố cục ảnh gần trùng.

### 18.8. Đặc trưng ảnh và giảm chiều

- **Đặc trưng** chuyển vùng ảnh thành tập giá trị cùng quy ước: màu (phân bố màu), hình dạng (đường bao/vùng), kết cấu (biến thiên cường độ lân cận). Tỉ lệ màu ít phụ thuộc kích thước nhưng không biết màu ở viền hay giữa → cần thêm hình dạng/cấu trúc nét.
- **Cục bộ** (quanh điểm nổi bật, như SIFT — Bài 4) vs **toàn vùng** (như HOG): vùng rất nhỏ không có đủ điểm nổi bật; vector toàn vùng nhạy với nền bị cắt vào.
- Ghép đặc trưng phải giữ đúng thứ tự, cách tính ở cả lúc học và lúc dùng; giá trị **thiếu** khác giá trị **0**.
- **HOG:** vùng kích thước thống nhất → gradient từng điểm → histogram hướng theo ô (trọng số theo độ lớn; không phân biệt dấu thì gộp hai hướng chênh 180°) → ghép ô thành khối, chuẩn hóa (giảm ảnh hưởng thay đổi độ sáng) → nối các khối. Ví dụ 4×4 ô, 9 hướng, khối 2×2 trượt 1 ô → 3×3 khối × 36 = **324**. Ô nhỏ chi tiết nhưng nhạy nhiễu; ô lớn gọn nhưng trộn nét. HOG không tự bất biến với quay hay phối cảnh.
- **PCA:** μ = trung bình; S = ma trận hiệp phương sai; vector riêng = hướng mới, trị riêng = phương sai theo hướng; giữ r hướng đầu → **z = U_rᵀ(x − μ)** (tổ hợp đặc trưng cũ, không phải xóa bớt vị trí). **Không dùng nhãn** → phương sai lớn ≠ phân loại tốt. Chuẩn hóa thang đo trước PCA là lựa chọn riêng. Fit trên train rồi giữ cố định cho val/test/ảnh mới.
- **Độ tương đồng & gần trùng (Bài 6):** khoảng cách nhỏ chỉ có nghĩa trong quy ước đặc trưng đã chọn. Phân biệt **trùng tệp**, **gần trùng nội dung**, **cùng lớp đối tượng**.
  **pHash:** xám → kích thước thống nhất → DCT → lấy hệ số tần số thấp → so trung vị → chuỗi bit. **Hamming** d_H = số bit khác. Ngưỡng rộng gộp nhầm cảnh khác; chặt bỏ sót bản gần trùng. Không phải mã hóa bảo mật. Trong cụm nối bắc cầu, hai ảnh ở hai đầu có thể khác nhau đáng kể.

---

## 19. Nghiên cứu liên quan — tóm tắt §1.6

Báo cáo chia bốn nhóm công trình; mỗi công trình đều có **vai trò cụ thể trong đề tài** — đó là điều phải nói được.

| Nhóm | Công trình | Nội dung chính | Vai trò trong đề tài |
|---|---|---|---|
| Dữ liệu & đánh giá | **GTSRB** (2012) | Phân loại vùng đã cắt, 43 lớp; tổ hợp CNN vượt người thử nghiệm | Tách đánh giá phân loại → thiết kế E8 |
| | **GTSDB** (2013) | Phát hiện trên ảnh đường phố, 900 ảnh (600 train / 300 test), chấm theo nhóm cấm/nguy hiểm/hiệu lệnh; HOG + phân loại tuyến tính là baseline | Phân loại tốt trên vùng cắt không thay được chỉ số phát hiện |
| | **TT100K** (2016) | 100 nghìn ảnh toàn cảnh, ≈ 30 nghìn biển, phần lớn rất nhỏ; detector cho vật lớn làm kém | Phân tích theo kích thước biển |
| | **Mapillary** (2020) | Phạm vi toàn cầu, lớp *other-sign*, báo cáo theo kích thước | Tiền lệ cho lớp "Biển báo khác" |
| | **Zalo AI Challenge 2020** | Ảnh 1622×626, nhiều biển rất nhỏ; nhiều đội dùng cắt ô | Ảnh độ phân giải này chiếm 41 % dữ liệu của nhóm |
| | **Pham và cs.; Cu và cs.** (2024) | YOLOv5 cho biển Việt Nam (Jetson; bộ biển nguy hiểm theo QCVN 41:2019) | Bối cảnh trong nước; dùng dữ liệu riêng, **chưa so với phương pháp truyền thống** trên cùng tập test |
| CV truyền thống | **De la Escalera và cs.** (1997) | Định vị theo màu + hình dạng, nhận dạng bằng mạng nơ-ron | Nền của pipeline đối chứng |
| | **Maldonado-Bascón và cs.** (2007) | Phân đoạn màu → SVM tuyến tính phân loại hình dạng → SVM Gauss nhận dạng nội dung | Nền cho SVM sau ứng viên màu |
| | **Dalal & Triggs** (2005) | HOG: histogram hướng gradient theo ô, chuẩn hóa theo khối | Đặc trưng thủ công chính |
| | **Vieira** (2025) | Tiền xử lý cho HOG-SVM trên GTSRB: 89,65 % → 91,25 % khi dùng YUV; ghép nhiều bước không luôn tốt hơn | Mốc tham chiếu (không so trực tiếp vì khác dữ liệu) |
| | **SIFT + túi từ thị giác** | Hiệu quả với vật giàu kết cấu | Đối chứng âm trong E8 |
| Học sâu & biển nhỏ | **Faster R-CNN**; **YOLO**; tổng quan **Sapkota và cs.** (YOLOv1 → v12) | Hai giai đoạn vs một giai đoạn | Lý do chọn một giai đoạn cho video |
| | **YOLO11** (Ultralytics) | Khối C3k2, C2PSA; cỡ nano → extra-large; khởi tạo từ COCO | Detector lõi (biến thể s) |
| | **SAHI** (2022) | Cắt ô chồng lấn: chỉ suy luận cắt ô +5,1–6,8 AP (VisDrone, xView); tinh chỉnh thêm trên ô +12,7–14,5 AP | Thí nghiệm T3 (nhóm chỉ thử phần suy luận vì không huấn luyện lại) |
| Theo vết & xác minh | **SORT** (2016) | Kalman + Hungarian theo IoU; ≈ 260 FPS; chất lượng phụ thuộc detector | Mô-đun theo vết |
| | **Šegvić và cs.** (2014) | Chuỗi phát hiện nhất quán theo thời gian, lọc bằng mô hình phân biệt riêng | Ý tưởng bộ xác minh |

**Ba khoảng trống đề tài nhắm tới:** (1) so sánh trực tiếp truyền thống vs học sâu trên cùng tập test biển Việt Nam, theo kích thước, có CI; (2) đo đóng góp từng khâu CV trong hệ thống học sâu, kể cả khâu không có ích; (3) cải thiện biển nhỏ và ảnh tối khi không thể thêm dữ liệu.

Báo cáo có **68 tài liệu tham khảo**, đã đối chiếu DOI/nơi đăng; 4 mục trích arXiv đã đổi sang bản xuất bản; riêng bài ETASR (Pham và cs., 2024) chưa xác minh được DOI nên chỉ ghi URL.
Nếu bị hỏi "số liệu của bài X có so được với nhóm không?" → **không so trực tiếp**, vì khác dữ liệu, cách chia và chỉ số.

---

## 20. Bản đồ hình và bảng trong báo cáo

Giảng viên thường lật PDF và hỏi "Hình 3.x / Bảng 3.x nói gì?". Trả lời theo mẫu: **hình/bảng trình bày gì → điểm cần nhìn → kết luận**. Số thứ tự lấy từ bản biên dịch `build/main.pdf`.

### 20.1. Hình

| Số | Nội dung | Điểm cần nhìn / kết luận | Xem lại |
|---|---|---|---|
| 1.1 | Quan hệ AI ⊃ ML ⊃ mạng nơ-ron ⊃ DL | DL nằm trong ML | §18.1 |
| 1.2 | Bốn hình thức học máy | Đề tài là có giám sát | §18.3 |
| 1.3 | CNN điển hình (nguồn InterData) | Phần trích đặc trưng + phần ra lớp | §18.4 |
| 1.4 | Các kênh RGB, HSV, Lab (thang xám) | Không phải ảnh mất màu; kênh H tuần hoàn | §18.7 |
| 1.5 | Co, giãn, mở, đóng; đường bao, khung, tâm | Hàng dưới độc lập với hàng trên | §18.7 |
| 2.1 | Minh họa bài toán nhận diện | Khung + lớp + giá trị đọc được | §4.1 |
| 2.2 | (a) 5 bước chuẩn bị dữ liệu, (b) vai trò từng tập | Thanh tỉ lệ số ảnh; C ∈ {1, 10} chọn trên val | §5.3–5.4 |
| 2.3 | Phân bố kích thước, độ phân giải, số biển/ảnh | Cột đỏ < 16 px, cam 16–32 px → biển rất nhỏ | §5.5 |
| 2.4 | Số biển 27 lớp theo nhóm; trong ngoặc cạnh trung vị | Mất cân bằng 22 lần | §5.5 |
| 2.5 | **Kiến trúc hệ thống** (CV xanh lá / DL xanh dương; liền = dữ liệu, đứt = tùy chọn) | Ảnh nhỏ là kết quả trung gian thật trên ảnh test; xác minh vẽ trước theo vết là sơ đồ chức năng | §6.1, §12 #3 |
| 2.6 | Kiến trúc OCR cơ bản | Tìm vùng chữ → nhận dạng | §6.7 |
| 2.7 | **Pipeline CV đối chứng** | HSV → ứng viên hình dạng → HOG + HSV → SVM có lớp nền | §6.8 |
| 2.8 | Các bước CV truyền thống trên ảnh test | Vùng (d) đầu tiên: **áo đỏ bị nhận nhầm "Cấm đỗ xe", xác suất 0,50** — báo động giả điển hình | §6.8 |
| 3.1 | (a) loss, (b) chỉ số val theo epoch | Giảm đều tới 80; tụt quanh epoch 66 do tắt mosaic; gần bão hòa | §8.2 |
| 3.2 | Recall 27 lớp + CI Wilson | 24/27 ≥ 0,81; 3 lớp yếu có nguyên nhân | §8.2 |
| 3.3 | Kết quả theo mức tương đồng với train | R 0,978 → 0,805; P 0,942 → 0,749 | §8.2 |
| 3.4 | Recall theo kích thước, 3 cách suy luận (T3) | 1280 giúp < 16 px; cắt ô cao nhất nhưng đánh đổi | §8.3 |
| 3.5 | Recall trên ảnh xấu, 3 chế độ (T4) | Thích nghi giúp ảnh tối, không hại ảnh nhiễu | §8.4 |
| 3.6 | Ảnh làm tối γ 3,5 trước/sau tăng cường | μV = 0,14 → chọn Gamma + CLAHE; tìm thêm biển ở mép phải | §8.4 |
| 3.7 | Accuracy phân loại theo kích thước, 4 phương pháp (E8) | Truyền thống được cho vị trí; YOLO bị tính sai cả khi bỏ sót | §8.6 |
| 3.8 | Chênh lệch ghép cặp HOG + màu − YOLO trên biển YOLO tìm thấy (bootstrap 2.000) | Đỏ = CI không chứa 0; xám = không khác biệt; < 16 px ngang nhau, ≥ 64 px thua rõ | §8.6 |
| 3.9 | YOLO (trái) vs CV truyền thống (phải) trên 3 ảnh test | 22 vs 8 phát hiện; gộp biển sát nhau; nhầm áo đỏ | §8.6 |
| 3.10 | Trang Pipeline hệ thống | Độ sáng 0,48, tương phản 0,23 → không tăng cường; đọc "40 km/h" | §9.3 |
| 3.11 | Trang Demo học sâu | Đổi kích thước, bật/tắt khâu, mô phỏng ảnh xấu → T3/T4/E2 trực tiếp | §9.3 |
| 3.12 | Trang Demo CV truyền thống | Ảnh vào → mask HSV → ứng viên → kết quả, thời gian từng bước | §9.3 |
| 3.13 | Trang So sánh CV – DL | Hai hệ thống cùng ảnh + bảng so khớp từng biển | §9.3 |
| Phụ lục | Trang Mô tả dữ liệu, trang Kết quả thực nghiệm | Số liệu xuất từ cùng tệp kết quả với Chương 3 | §9.3 |

### 20.2. Bảng

| Số | Nội dung | Xem lại |
|---|---|---|
| 1.1 | Các hình thức học máy | §18.3 |
| 1.2 | ML truyền thống vs học sâu | §18.3 |
| 1.3 | Đặc điểm các không gian màu | §18.7 |
| 1.4 | Đặc điểm một số phép lọc | §18.7 |
| 1.5 | Tóm tắt nghiên cứu liên quan | §19 |
| 2.1 | Thống kê chia tập theo cụm | §5.4 |
| 2.2 | Cấu hình huấn luyện và suy luận YOLO11s | §6.4 |
| 2.3 | Danh sách thí nghiệm | §8.1 |
| 3.1 | Môi trường thực nghiệm | §8 (đầu mục) |
| 3.2 | Kết quả YOLO11s 960 px trên test (S1) | §8.2 |
| 3.3 | Kết quả theo kích thước biển | §8.2 |
| 3.4 | T3 — cách suy luận và biển nhỏ | §8.3 |
| 3.5 | T4 — recall khi ảnh bị làm xấu | §8.4 |
| 3.6 | E8 — phân loại thủ công vs YOLO | §8.6 |
| 3.7 | T1 — ablation đặc trưng bộ xác minh | §8.5 |
| 3.8 | E1 — hệ thống mặc định | §8.7 |
| 3.9 | E2 — ablation từng khâu (960 px) | §8.7 |
| 3.10 | Tốc độ hệ thống | §8.9 |
| 3.11 | Các trang của ứng dụng web | §9.3 |
| Phụ lục | Cấu trúc mã nguồn · Lệnh tái lập kết quả · Thay đổi so với dữ liệu gốc | §9.1, §10, §5.3 |

**Phụ lục còn có 2 đoạn mã lõi** (rút gọn): `needed_ops` + `auto_gamma` trong `enhance.py` (quy tắc §6.3) và đoạn lọc hình dạng trong `traditional.py` (quy tắc §6.8). Nếu bị hỏi, đọc theo thứ tự điều kiện như hai bảng quy tắc đó.

---

## 21. Bảng viết tắt

| Viết tắt | Đầy đủ — nghĩa |
|---|---|
| API | Application Programming Interface — giao diện lập trình ứng dụng |
| AP / mAP | Average Precision / Mean AP — độ chính xác trung bình của một lớp / trung bình các lớp |
| AUC | Area Under the ROC Curve — diện tích dưới đường ROC (0,5 = ngẫu nhiên, 1 = hoàn hảo) |
| BoVW | Bag of Visual Words — túi từ thị giác |
| CER | Character Error Rate — tỉ lệ lỗi ký tự |
| CI | Confidence Interval — khoảng tin cậy |
| CLAHE | Contrast Limited Adaptive Histogram Equalization — cân bằng histogram thích nghi có giới hạn tương phản |
| CNN | Convolutional Neural Network — mạng nơ-ron tích chập |
| CPU / GPU | Bộ xử lý trung tâm / đồ họa |
| CV | Computer Vision — trong báo cáo: xử lý ảnh và đặc trưng thủ công |
| DL / ML | Deep Learning / Machine Learning — học sâu / học máy |
| EDA | Exploratory Data Analysis — phân tích khám phá dữ liệu |
| TP / FP / FN | Phát hiện đúng / phát hiện sai / bỏ sót |
| FPS | Frames Per Second — số khung hình mỗi giây |
| HOG | Histogram of Oriented Gradients — histogram hướng gradient |
| HSV | Hue, Saturation, Value — sắc màu, bão hòa, độ sáng |
| IoU | Intersection over Union — tỉ lệ giao trên hợp |
| NMS | Non-Maximum Suppression — loại khung không cực đại |
| OCR | Optical Character Recognition — nhận dạng ký tự quang học |
| pHash | Perceptual Hash — băm cảm nhận |
| QCVN | Quy chuẩn kỹ thuật quốc gia (41:2019/BGTVT về báo hiệu đường bộ) |
| RBF | Radial Basis Function — nhân Gauss của SVM |
| SAHI | Slicing Aided Hyper Inference — suy luận hỗ trợ bằng cắt ô |
| SIFT | Scale-Invariant Feature Transform — biến đổi đặc trưng bất biến tỉ lệ |
| SVM | Support Vector Machine — máy vector hỗ trợ |
| YOLO | You Only Look Once — mô hình phát hiện một giai đoạn |
| Thêm (không có trong danh mục báo cáo nhưng hay dùng) | PCA — phân tích thành phần chính · SORT — Simple Online and Realtime Tracking · RPN — mạng đề xuất vùng · ADR — Architecture Decision Record · SRS — đặc tả yêu cầu phần mềm |
