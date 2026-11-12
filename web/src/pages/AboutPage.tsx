import { Card, PageHead } from "../components/ui";

const STACK: [string, string][] = [
  ["Học sâu", "YOLO11s (Ultralytics 8.4), PyTorch, VietOCR (VGG + Transformer)"],
  ["CV truyền thống", "OpenCV (HSV, CLAHE, hình thái học, contour, Kalman), scikit-image (HOG), scikit-learn (SVM), LightGBM, SciPy (Hungarian)"],
  ["Backend", "FastAPI, WebSocket, Uvicorn"],
  ["Frontend", "React 19, Vite, TypeScript, Recharts"],
  ["Triển khai", "Docker Compose (CPU / GPU), Nginx"],
  ["Thực nghiệm", "Colab (Tesla T4) + máy cá nhân (RTX 4060), sổ đăng ký experiments/registry.csv, bootstrap CI"],
];

const RULES: [string, string][] = [
  ["C-06", "Không commit dataset, trọng số, video — trọng số đặt ở models/current (ghi chép trong docs/models.md)."],
  ["C-08", "Dataset khoá ở processed/v1 (27 lớp, 5 386 ảnh); không bổ sung ảnh, không gán lại nhãn."],
  ["Tái lập", "Mọi số liệu web sinh từ scripts/export_web_data.py và các script đánh giá trong scripts/."],
];

/** Giới thiệu dự án, công nghệ, giấy phép. */
export default function AboutPage() {
  return (
    <>
      <PageHead title="Giới thiệu dự án" desc="UTCI-VISION — đồ án môn Thị giác máy tính (23/10 – 04/12/2026), nhóm 5 thành viên (TV1–TV5), 6 sprint." />
      <div className="grid g2">
        <Card title="Bài toán">
          <p style={{ marginTop: 0 }}>
            Nhận diện biển báo giao thông Việt Nam trong ảnh / video từ camera hành trình: tìm vị trí, xác định loại biển (27 lớp theo QCVN 41:2019), đọc giá trị số và chữ trên biển, và giải thích ý
            nghĩa bằng tiếng Việt.
          </p>
          <p>
            Yêu cầu môn học: dùng cả <span className="pill pill-cv">CV truyền thống / đặc trưng thủ công</span> và <span className="pill pill-dl">học sâu</span>, so sánh hai cách tiếp cận bằng thực nghiệm.
          </p>
        </Card>
        <Card title="Ràng buộc">
          <div className="table-wrap">
            <table>
              <tbody>
                {RULES.map(([k, v]) => (
                  <tr key={k}>
                    <td>
                      <b>{k}</b>
                    </td>
                    <td>{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
      <Card title="Công nghệ">
        <div className="table-wrap">
          <table>
            <tbody>
              {STACK.map(([k, v]) => (
                <tr key={k}>
                  <td style={{ width: 160 }}>
                    <b>{k}</b>
                  </td>
                  <td>{v}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
      <Card title="Nguồn và giấy phép">
        <ul style={{ margin: 0, paddingLeft: 20, lineHeight: 1.8 }}>
          <li>
            Dataset: <i>merge_Real-time Viet Nam Traffic Dtctn 2</i> — Roboflow Universe, CC BY 4.0 (
            <a href="https://universe.roboflow.com/nguyns-workspace-17a6o/merge_real-time-viet-nam-traffic-dtctn-2-a7emf" target="_blank" rel="noreferrer">
              liên kết
            </a>
            ).
          </li>
          <li>Ultralytics YOLO11 — AGPL-3.0. VietOCR — Apache-2.0.</li>
          <li>Mã nguồn dự án: Apache-2.0 — © 2026 LiemDaiHiep.</li>
          <li>
            Mã nguồn:{" "}
            <a href="https://github.com/HoanBuCon/UTCI-Vision" target="_blank" rel="noreferrer">
              github.com/HoanBuCon/UTCI-Vision
            </a>
            ; tài liệu trong <code>docs/</code> (SRS, báo cáo đề xuất, đánh giá).
          </li>
        </ul>
      </Card>
    </>
  );
}
