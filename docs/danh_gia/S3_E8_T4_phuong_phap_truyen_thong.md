# Phương pháp truyền thống: E8 (đặc trưng thủ công vs học sâu) và T4 (tăng cường ảnh)

- **Ngày:** 11/11/2026 · **Trọng số YOLO:** `20261029-1030_yolo11s_960` (baseline S1) · **Dữ liệu:** `processed/v1` (không chỉnh sửa)
- **Tái lập:** `python scripts/compare_traditional_dl.py <yolo11.pt>` (E8) · `python scripts/enhance_robustness.py <yolo11.pt>` (T4)
- **Bối cảnh:** hướng B sau thử nghiệm [T0/T1](S3_T0_T1_kha_thi_bo_xac_minh.md) — đặt phương pháp truyền thống vào vai trò đo được rõ ràng.

## Tóm tắt

| | Kết quả chính |
|---|---|
| **E8** | Đặc trưng thủ công tốt nhất (**HOG + màu HSV + SVM**) phân loại đúng **91,0%** biển test (YOLO11: 92,4%). Trên cùng tập biển YOLO tìm thấy, YOLO hơn 3,3 điểm [CI95 1,9–4,6]; với biển < 16 px **hai phương pháp ngang nhau** (Δ +2,0 điểm, CI95 −2,6…+6,6). SIFT-BoVW kém nhất (71,1%). |
| **T4** | Tăng cường thích nghi (gamma + CLAHE khi ảnh tối) **khôi phục 53–66% recall bị mất** khi ảnh tối: γ 2,5: 0,810 → 0,853; γ 3,5: 0,686 → **0,822** (+0,136, CI95 +0,116…+0,155). Không làm hại ảnh tốt (chỉ kích hoạt ở 2,8% ảnh gốc). Bước đánh giá chất lượng **ngăn được** CLAHE làm hại ảnh nhiễu (áp mù: recall −0,093). |

## E8 — Phân loại biển: đặc trưng truyền thống + SVM vs YOLO11

**Thiết kế.** Cùng 2 017 biển test. Phương pháp truyền thống fit trên 9 449 crop train, chọn `C` trên 2 009 crop val (SVM RBF,
chuẩn hoá chuẩn), được **cho sẵn vị trí biển** (crop GT, nới 10%). YOLO phải tự tìm biển: lấy lớp của dự đoán điểm cao nhất có
IoU ≥ 0,5 (conf ≥ 0,001); không có thì tính bỏ sót. Vì vậy so sánh công bằng là cột "trên biển YOLO tìm thấy" (1 956 biển, cùng
mẫu cho mọi phương pháp).

| Phương pháp | Đặc trưng | Accuracy (CI95) | Macro-F1 | Accuracy trên biển YOLO tìm thấy | ms / crop |
|---|---|---|---|---|---|
| HOG + SVM | HOG 32×32 (324 chiều) | 0,888 (0,874–0,901) | 0,852 | 0,901 | 1,6 |
| **HOG + màu + SVM** | + histogram HSV 16×4 | **0,910** (0,897–0,922) | 0,872 | 0,920 | 2,0 |
| SIFT-BoVW + SVM | SIFT trên crop 64×64, từ điển 256 | 0,711 (0,691–0,730) | 0,662 | 0,724 | 2,7 |
| **YOLO11s** (học sâu) | CNN học đầu-cuối | **0,924** (0,912–0,935) | **0,917** | **0,953** | 22 ms / ảnh (gồm tìm biển) |

**Theo kích thước biển** (accuracy trên mọi biển / trên biển YOLO tìm thấy):

| Cạnh biển | n | HOG + SVM | HOG + màu + SVM | SIFT-BoVW + SVM | YOLO11s | YOLO tìm thấy |
|---|---|---|---|---|---|---|
| < 16 px | 361 | 0,756 / 0,807 | **0,812 / 0,856** | 0,526 / 0,567 | 0,706 / 0,836 | 84,5% |
| 16–32 px | 751 | 0,903 / 0,905 | 0,929 / 0,930 | 0,738 / 0,740 | **0,957 / 0,963** | 99,5% |
| 32–64 px | 617 | 0,940 / 0,940 | 0,953 / 0,953 | 0,767 / 0,767 | **0,979 / 0,979** | 100% |
| ≥ 64 px | 288 | 0,906 / 0,906 | 0,892 / 0,892 | 0,753 / 0,756 | **0,993 / 0,997** | 99,7% |

**Δaccuracy ghép cặp (HOG + màu + SVM − YOLO11) trên biển YOLO tìm thấy**, bootstrap 2 000 lần:

| Cạnh biển | n | Δ | CI95 |
|---|---|---|---|
| Tất cả | 1 956 | −0,033 | −0,046 … −0,019 |
| < 16 px | 305 | +0,020 | −0,026 … +0,066 (không khác biệt) |
| 16–32 px | 747 | −0,032 | −0,052 … −0,013 |
| 32–64 px | 617 | −0,026 | −0,044 … −0,008 |
| ≥ 64 px | 287 | −0,105 | −0,143 … −0,073 |

**Nhận xét**
1. **Đặc trưng thủ công cạnh tranh được ở phân loại:** HOG + màu kém YOLO chỉ 1,4 điểm accuracy tổng; thêm màu HSV vào HOG tăng
   2,2 điểm — màu là thông tin QCVN mà HOG trên ảnh xám bỏ qua.
2. **Với biển nhỏ, điểm yếu của YOLO là *tìm* biển, không phải *phân loại*:** YOLO bỏ sót 15,5% biển < 16 px; trên các biển nhỏ YOLO
   tìm thấy, HOG + màu phân loại ngang YOLO. Khi được cho vị trí, phương pháp truyền thống đúng 81,2% biển < 16 px so với 70,6%
   của YOLO (gồm bỏ sót).
3. **Biển lớn là nơi đặc trưng thủ công thua rõ nhất** (−10,5 điểm): crop bị thu về 32×32 làm mất chi tiết của biển chỉ dẫn /
   biển có chữ (vd. "Biển gộp làn đường theo phương tiện"), trong khi CNN học được đặc trưng ở nhiều tỉ lệ.
4. **SIFT không hợp với biển báo**, đúng như dự đoán: kém HOG 17,7 điểm; dù phóng crop lên 64×64 (chỉ 0,7% crop test không có
   điểm SIFT), điểm khoá chủ yếu là điểm nội suy và viền tròn chung của nhiều lớp.
5. Đặc trưng thủ công rẻ (1,6–2,7 ms / crop trên CPU) nhưng cần một bước định vị riêng — chính là việc YOLO làm.

## T4 — Tăng cường ảnh thích nghi khi ảnh xấu

**Thiết kế.** 826 ảnh test bị làm xấu nhân tạo; YOLO @0,25 trên ảnh (a) không xử lý, (b) **tăng cường thích nghi** của pipeline
(đánh giá chất lượng → chỉ áp gamma tự động + CLAHE kênh L / lọc song phương khi cần; ngưỡng trong `configs/pipeline.yaml`,
chọn từ thống kê dữ liệu ở S1, không tinh chỉnh trên test), (c) **luôn áp gamma + CLAHE** (đối chứng). Δ so với (a), CI95 bootstrap
ghép cặp theo ảnh (1 000 lần).

| Điều kiện | Không xử lý P / R | Thích nghi: % ảnh xử lý · P / R · ΔR (CI95) | Luôn gamma + CLAHE: P / R · ΔR (CI95) |
|---|---|---|---|
| Ảnh gốc | 0,864 / 0,893 | 2,8% · 0,862 / 0,892 · −0,001 (−0,003…+0,000) | 0,866 / 0,890 · −0,003 (−0,010…+0,004) |
| Tối (γ 2,5) | 0,908 / 0,810 | 68,2% · 0,885 / **0,853** · **+0,044** (+0,032…+0,056) | 0,873 / 0,873 · +0,063 (+0,049…+0,077) |
| Rất tối (γ 3,5) | 0,923 / 0,686 | 80,5% · 0,904 / **0,822** · **+0,136** (+0,116…+0,155) | 0,885 / 0,854 · +0,168 (+0,147…+0,188) |
| Nhiễu Gauss (σ 15) | 0,827 / 0,799 | 2,8% · 0,827 / 0,799 · 0,000 (−0,001…+0,001) | 0,870 / 0,706 · **−0,093** (−0,109…−0,077) |
| Mờ chuyển động | 0,843 / 0,748 | 2,8% · 0,841 / 0,748 · 0,000 (−0,001…+0,002) | 0,841 / 0,734 · −0,014 (−0,024…−0,004) |

**Nhận xét**
1. **Tăng cường truyền thống có tác dụng rõ với ảnh tối:** khôi phục 53% (γ 2,5) và 66% (γ 3,5) phần recall bị mất, có ý nghĩa
   thống kê; precision giảm nhẹ (−0,02) vì ảnh sáng hơn làm lộ thêm vật thể giống biển.
2. **Bước đánh giá chất lượng là cần thiết:** áp CLAHE cho mọi ảnh làm hại ảnh nhiễu (recall −0,093) và ảnh mờ; chế độ thích nghi
   không kích hoạt ở đó nên không gây hại, và gần như không chạm vào ảnh tốt.
3. **Hạn chế đã lộ ra:**
   - Ngưỡng tối (`dark_mean_v = 0,30`) bỏ sót 20–32% ảnh đã làm tối, nên thích nghi kém hơn "luôn áp" trên ảnh tối
     (+0,044 so với +0,063). Hạ ngưỡng cần chọn lại trên val, không chọn trên test.
   - Nhiễu Gauss σ 15 **không bị phát hiện** (phương sai Laplacian không tách được nhiễu với chi tiết ảnh như tán lá), nên bước lọc song
     phương chưa bao giờ được dùng trong thử nghiệm này — chưa có bằng chứng về khử nhiễu.
   - Ảnh làm tối nhân tạo khác ảnh đêm thật (đèn xe, đèn đường, nhiễu cảm biến); cần ảnh đêm thật để khẳng định.

## Kết luận cho phần "phương pháp truyền thống" của đề tài

| Vai trò | Bằng chứng | Mức thuyết phục |
|---|---|---|
| Tăng cường ảnh thích nghi (gamma, CLAHE, đánh giá chất lượng) | T4: +0,136 recall ở ảnh rất tối, không hại ảnh tốt / ảnh nhiễu | **Mạnh** — có ý nghĩa thống kê, vai trò thật trong pipeline |
| Trích xuất đặc trưng thủ công HOG + màu (+ SVM) | E8: 91,0% vs 92,4% của YOLO; ngang YOLO trên biển nhỏ đã tìm thấy | **Mạnh cho chương so sánh** — cho thấy đặc trưng thủ công làm được gì và thua ở đâu |
| Bộ xác minh đặc trưng thủ công + LightGBM | T1: không vượt điểm YOLO ở cùng recall | Yếu — giữ như kết quả ablation trung thực |
| SIFT-BoVW | E8: 71,1% | Đối chứng âm — giải thích vì sao chọn HOG |

Gợi ý cho nhóm (cần quyết định): đưa tăng cường thích nghi vào pipeline như khâu truyền thống chính (FR-PIPE-01/02); dùng E8 làm
chương so sánh trong báo cáo; chọn lại ngưỡng `dark_mean_v` trên val; thu một ít ảnh đêm thật để kiểm chứng T4.

## Hạn chế chung
- Một lần chạy, một trọng số YOLO; val đã dùng để chọn epoch YOLO (ảnh hưởng nhỏ); test chưa dùng cho lựa chọn nào.
- E8: phương pháp truyền thống có lợi thế được cho vị trí biển; SVM chỉ dò `C` ∈ {1, 10}.
- T4: suy giảm nhân tạo, không phải ảnh xấu thật.
