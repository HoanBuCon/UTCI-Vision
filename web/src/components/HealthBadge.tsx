import { useHealth } from "../api/useHealth";

const NAMES: Record<string, string> = { detector: "YOLO11", verifier: "Bộ xác minh", ocr: "VietOCR", classic: "HOG + SVM" };

/** Trạng thái backend + mô hình đã nạp (FR-API-01). */
export default function HealthBadge() {
  const { health, error } = useHealth();
  if (error && !health)
    return (
      <span className="badge badge-err" title={error}>
        <i className="dot" />
        <span className="health-text">API chưa sẵn sàng</span>
      </span>
    );
  if (!health)
    return (
      <span className="badge">
        <i className="dot" />
        <span className="health-text">Đang kết nối…</span>
      </span>
    );
  const loaded = Object.values(health.models).filter((m) => m.loaded).length;
  const detail = Object.entries(health.models)
    .map(([k, m]) => `${NAMES[k] ?? k}: ${m.loaded ? "đã nạp" : m.detail}`)
    .join("\n");
  return (
    <span className={`badge ${error ? "badge-err" : health.status === "ok" ? "badge-ok" : "badge-warn"}`} title={detail}>
      <i className="dot" />
      <span className="health-text">
        API {health.version} · {health.device.toUpperCase()} · {loaded}/{Object.keys(health.models).length} mô hình
      </span>
    </span>
  );
}
