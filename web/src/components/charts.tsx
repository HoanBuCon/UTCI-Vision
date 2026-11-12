import type { ReactNode } from "react";

/** Chú giải dùng chung (≥ 2 chuỗi), đặt trên biểu đồ. */
export function Legend({ items }: { items: { label: string; color: string }[] }) {
  return (
    <div className="legend">
      {items.map((i) => (
        <span key={i.label}>
          <i style={{ background: i.color }} />
          {i.label}
        </span>
      ))}
    </div>
  );
}

interface TipPayload {
  name?: string | number;
  value?: number | string | (number | string)[];
  color?: string;
  dataKey?: string | number;
  payload?: Record<string, unknown>;
}

/** Tooltip Recharts theo token giao diện (sáng/tối). `format` định dạng giá trị. */
export function Tip({
  active,
  payload,
  label,
  format = (v) => (typeof v === "number" ? v.toFixed(3) : String(v)),
  title,
}: {
  active?: boolean;
  payload?: TipPayload[];
  label?: ReactNode;
  format?: (v: number | string, key?: string) => string;
  title?: (label: ReactNode, p?: Record<string, unknown>) => ReactNode;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tip">
      <b>{title ? title(label, payload[0].payload) : label}</b>
      {payload.map((p) => (
        <div key={String(p.dataKey)}>
          <i style={{ background: p.color }} />
          {p.name}
          <span>{Array.isArray(p.value) ? p.value.join(" – ") : p.value !== undefined ? format(p.value, String(p.dataKey)) : "—"}</span>
        </div>
      ))}
    </div>
  );
}

export const pctTick = (v: number) => `${Math.round(v * 100)}%`;
