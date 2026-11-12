import { Link } from "react-router-dom";
import type { Eda, Results } from "../api/staticTypes";
import { useHealth } from "../api/useHealth";
import Icon from "../components/Icon";
import { Card, fmt, int, Kpi, PageHead, pct, useStatic } from "../components/ui";

const LINKS = [
  { to: "/demo/dl", icon: "brain", title: "Demo học sâu", text: "YOLO11s + OCR trên ảnh mẫu hoặc ảnh của bạn, bật tắt từng khâu." },
  { to: "/demo/traditional", icon: "scan", title: "Demo CV truyền thống", text: "Màu HSV → hình dạng → HOG + SVM, xem từng bước." },
  { to: "/compare", icon: "compare", title: "So sánh CV ↔ DL", text: "Cùng ảnh, hai hệ thống, và số liệu thí nghiệm E8 / T4." },
  { to: "/pipeline", icon: "flow", title: "Pipeline", text: "Sơ đồ tương tác và kết quả trung gian của từng khâu." },
  { to: "/data", icon: "data", title: "Dữ liệu", text: "5 386 ảnh, 27 lớp — phân bố lớp, kích thước, vị trí." },
  { to: "/demo/video", icon: "video", title: "Video & webcam", text: "Theo vết Kalman, xuất video kết quả, nhận diện thời gian thực." },
];

const NAMES: Record<string, string> = { detector: "YOLO11s", verifier: "Bộ xác minh (LightGBM)", ocr: "VietOCR", classic: "HOG + SVM" };

/** Bảng điều khiển: số liệu chính + trạng thái mô hình + lối tắt demo. */
export default function DashboardPage() {
  const { data: eda } = useStatic<Eda>("eda");
  const { data: res } = useStatic<Results>("results");
  const { health, error } = useHealth();
  const boot = Object.fromEntries((res?.bootstrap ?? []).map((b) => [b.metric, b]));
  const e1 = res?.e1[0];
  const e8 = (m: string) => res?.e8.find((r) => r.phuong_phap === m && r.kich_thuoc === "tất cả");

  return (
    <>
      <PageHead
        title="Hệ thống nhận diện biển báo giao thông Việt Nam"
        desc="Phát hiện, phân loại 27 loại biển theo QCVN 41:2019 và đọc giá trị trên biển từ ảnh, video và webcam — kết hợp CV truyền thống (tăng cường ảnh, phân đoạn màu, HOG, theo vết Kalman) với học sâu (YOLO11s, VietOCR)."
      >
        <Link className="btn btn-primary" to="/demo/dl">
          <Icon name="play" size={16} /> Thử ngay
        </Link>
      </PageHead>

      <div className="grid kpis">
        <Kpi label="Dữ liệu" value={eda ? int(eda.totals.images) : "…"} sub={eda ? `ảnh · ${int(eda.totals.boxes)} biển · ${eda.totals.classes} lớp` : undefined} />
        <Kpi label="mAP50 (test)" value={boot.mAP50 ? fmt(boot.mAP50.value) : "…"} sub={boot.mAP50 ? `CI95 ${fmt(boot.mAP50.ci95_low)} – ${fmt(boot.mAP50.ci95_high)}` : undefined} />
        <Kpi label="Hệ thống — F1" value={e1 ? fmt(e1.f1 as number) : "…"} sub={e1 ? `P ${fmt(e1.precision as number)} · R ${fmt(e1.recall as number)}` : undefined} />
        <Kpi label="Recall biển < 16 px" value={e1 ? fmt(e1["recall_<16px"] as number) : "…"} sub="0,634 ở 960 px → 1280 px" />
        <Kpi label="Phân loại: YOLO vs HOG + màu" value={res ? `${pct(e8("YOLO11 (học sâu)")?.accuracy)} / ${pct(e8("HOG + màu + SVM")?.accuracy)}` : "…"} sub="accuracy trên 2 017 biển test (E8)" />
        <Kpi label="Tốc độ" value={res ? `${res.benchmarks.gpu_detector_ms_1280} ms` : "…"} sub={res ? `YOLO 1280 trên GPU · Docker CPU ${res.benchmarks.docker_cpu_image_s.join("–")} s / ảnh` : undefined} />
      </div>

      <div className="grid g3" style={{ marginTop: 16 }}>
        <Card title="Bắt đầu demo" className="span-2">
          <div className="quick">
            {LINKS.map((l) => (
              <Link key={l.to} to={l.to}>
                <Icon name={l.icon} />
                <span>
                  <b>{l.title}</b>
                  <p>{l.text}</p>
                </span>
              </Link>
            ))}
          </div>
        </Card>
        <Card title="Trạng thái máy chủ">
          {error && !health && <p className="error small">API chưa sẵn sàng: {error}</p>}
          {health && (
            <>
              <p className="small muted" style={{ marginTop: 0 }}>
                Phiên bản {health.version} · thiết bị <b>{health.device.toUpperCase()}</b>
              </p>
              <ul className="seen">
                {Object.entries(health.models).map(([k, m]) => (
                  <li key={k} className="row-flex">
                    <span className={`badge ${m.loaded ? "badge-ok" : "badge-warn"}`}>
                      <i className="dot" />
                      {m.loaded ? "đã nạp" : "chưa"}
                    </span>
                    <span>{NAMES[k] ?? k}</span>
                    {!m.loaded && <span className="small muted">{m.detail}</span>}
                  </li>
                ))}
              </ul>
            </>
          )}
          {!health && !error && <p className="muted">Đang kết nối…</p>}
        </Card>
      </div>

      <Card title="Điểm chính" note="Chi tiết: trang Kết quả thực nghiệm và So sánh CV ↔ DL; báo cáo đầy đủ trong docs/danh_gia.">
        <ul style={{ margin: 0, paddingLeft: 20, lineHeight: 1.7 }}>
          <li>
            Suy luận ở <b>1280 px</b> (huấn luyện 960) tăng recall biển nhỏ &lt; 16 px từ 0,634 lên 0,737 mà precision không đổi (T3).
          </li>
          <li>
            <b>Tăng cường thích nghi</b> chỉ kích hoạt khi ảnh tối / kém tương phản: ảnh rất tối recall 0,686 → 0,822, ảnh thường không đổi (T4).
          </li>
          <li>
            Đặc trưng thủ công <b>HOG + màu + SVM</b> phân loại gần bằng YOLO (0,910 vs 0,924) và ngang YOLO ở biển &lt; 16 px; SIFT chỉ 0,711 (E8). Nhưng khâu định vị bằng màu + hình dạng kém xa
            YOLO.
          </li>
          <li>
            <b>Bộ xác minh</b> LightGBM tăng precision 0,861 → 0,946 nhưng giảm recall → tắt mặc định, có thể bật trên trang demo (E2).
          </li>
        </ul>
      </Card>
    </>
  );
}
