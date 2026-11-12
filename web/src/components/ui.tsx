import { useEffect, useMemo, useState, type ReactNode } from "react";
import { loadStatic } from "../api/client";

export function Card({ title, note, extra, children, className = "", id }: { title?: ReactNode; note?: ReactNode; extra?: ReactNode; children?: ReactNode; className?: string; id?: string }) {
  return (
    <section className={`card ${className}`} id={id}>
      {(title || extra) && (
        <div className="card-head">
          {title && <h2>{title}</h2>}
          {extra}
        </div>
      )}
      {children}
      {note && <p className="card-note">{note}</p>}
    </section>
  );
}

export function Kpi({ label, value, sub }: { label: ReactNode; value: ReactNode; sub?: ReactNode }) {
  return (
    <div className="card kpi">
      <span className="label">{label}</span>
      <span className="value">{value}</span>
      {sub && <span className="sub">{sub}</span>}
    </div>
  );
}

export function PageHead({ title, desc, children }: { title: string; desc?: ReactNode; children?: ReactNode }) {
  return (
    <div className="page-head">
      <div>
        <h1>{title}</h1>
        {desc && <p>{desc}</p>}
      </div>
      {children}
    </div>
  );
}

export function Switch({ label, checked, onChange, disabled, title }: { label: string; checked: boolean; onChange: (v: boolean) => void; disabled?: boolean; title?: string }) {
  return (
    <label className="switch" title={title}>
      <input type="checkbox" checked={checked} disabled={disabled} onChange={(e) => onChange(e.target.checked)} />
      {label}
    </label>
  );
}

export function Seg<T extends string | number>({ value, options, onChange }: { value: T; options: { value: T; label: string }[]; onChange: (v: T) => void }) {
  return (
    <div className="seg" role="group">
      {options.map((o) => (
        <button key={String(o.value)} className={o.value === value ? "on" : ""} onClick={() => onChange(o.value)} aria-pressed={o.value === value}>
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function Busy({ text = "Đang xử lý…" }: { text?: string }) {
  return (
    <span className="busy">
      <span className="spinner" />
      {text}
    </span>
  );
}

export const pct = (v: number | null | undefined, d = 1) => (v === null || v === undefined ? "—" : `${(v * 100).toFixed(d)}%`);
export const fmt = (v: number | null | undefined, d = 3) => (v === null || v === undefined ? "—" : v.toFixed(d));
export const int = (v: number) => v.toLocaleString("vi-VN");

/** Dữ liệu tĩnh web/public/data/*.json. */
export function useStatic<T>(name: "eda" | "results"): { data: T | null; error: string | null } {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    loadStatic<T>(name).then(setData, (e: Error) => setError(e.message));
  }, [name]);
  return { data, error };
}

export interface Column<R> {
  key: string;
  label: ReactNode;
  num?: boolean;
  render?: (r: R) => ReactNode;
  value?: (r: R) => number | string | null;
}

/** Bảng sắp xếp được (bấm tiêu đề cột). */
export function SortTable<R>({ rows, columns, initial, highlight }: { rows: R[]; columns: Column<R>[]; initial?: { key: string; desc?: boolean }; highlight?: (r: R) => boolean }) {
  const [sort, setSort] = useState(initial ?? null);
  const sorted = useMemo(() => {
    if (!sort) return rows;
    const col = columns.find((c) => c.key === sort.key);
    const get = col?.value ?? ((r: R) => (r as Record<string, unknown>)[sort.key] as number | string | null);
    return [...rows].sort((a, b) => {
      const x = get(a);
      const y = get(b);
      if (x === y) return 0;
      if (x === null || x === undefined) return 1;
      if (y === null || y === undefined) return -1;
      return (x < y ? -1 : 1) * (sort.desc ? -1 : 1);
    });
  }, [rows, columns, sort]);
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((c) => (
              <th
                key={c.key}
                className={`sortable ${c.num ? "num" : ""}`}
                onClick={() => setSort((s) => ({ key: c.key, desc: s?.key === c.key ? !s.desc : Boolean(c.num) }))}
                aria-sort={sort?.key === c.key ? (sort.desc ? "descending" : "ascending") : undefined}
              >
                {c.label}
                {sort?.key === c.key ? (sort.desc ? " ↓" : " ↑") : ""}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((r, i) => (
            <tr key={i} className={highlight?.(r) ? "hl" : ""}>
              {columns.map((c) => (
                <td key={c.key} className={c.num ? "num" : ""}>
                  {c.render ? c.render(r) : String((r as Record<string, unknown>)[c.key] ?? "—")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** Tải xuống một chuỗi / data URL thành file. */
export function download(name: string, content: string, type = "application/json") {
  const url = content.startsWith("data:") ? content : URL.createObjectURL(new Blob([content], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  if (!content.startsWith("data:")) setTimeout(() => URL.revokeObjectURL(url), 1000);
}
