import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { HealthResponse } from "../api/types";

/** Trạng thái backend + mô hình đã nạp (FR-API-01). Hỏi lại mỗi 10 s (API có thể còn đang nạp mô hình). */
export default function HealthBadge() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const check = () =>
      api
        .health()
        .then((h) => {
          setHealth(h);
          setError(null);
        })
        .catch((e: Error) => setError(e.message));
    check();
    const timer = window.setInterval(check, 10_000);
    return () => window.clearInterval(timer);
  }, []);

  if (error) return <span className="badge badge-err" title={error}>API chưa sẵn sàng</span>;
  if (!health) return <span className="badge">Đang kết nối…</span>;
  const active = Object.values(health.models).filter((m) => m.loaded || m.detail?.startsWith("tắt"));
  const loaded = Object.values(health.models).filter((m) => m.loaded).length;
  const detail = Object.entries(health.models)
    .map(([k, m]) => `${k}: ${m.loaded ? "đã nạp" : m.detail}`)
    .join("\n");
  return (
    <span className={`badge ${health.status === "ok" ? "badge-ok" : "badge-warn"}`} title={detail}>
      API {health.version} · {health.device} · mô hình {loaded}/{active.length}
    </span>
  );
}
