import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { HealthResponse } from "../api/types";

/** Hiển thị trạng thái backend + mô hình đã nạp (FR-API-01). Đã chạy được với khung API hiện tại. */
export default function HealthBadge() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.health().then(setHealth).catch((e: Error) => setError(e.message));
  }, []);

  if (error) return <span className="badge badge-err">API lỗi</span>;
  if (!health) return <span className="badge">Đang kết nối…</span>;
  const loaded = Object.values(health.models).filter((m) => m.loaded).length;
  return (
    <span className={`badge ${health.status === "ok" ? "badge-ok" : "badge-warn"}`}>
      API {health.version} · {health.device} · mô hình {loaded}/{Object.keys(health.models).length}
    </span>
  );
}
