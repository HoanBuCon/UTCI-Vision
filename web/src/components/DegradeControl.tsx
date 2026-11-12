import type { Degrade } from "../api/client";
import { Seg } from "./ui";

export interface DegradeValue {
  kind: Degrade;
  level: number;
}

const RANGE: Record<Exclude<Degrade, null>, { min: number; max: number; step: number; def: number; label: (v: number) => string }> = {
  dark: { min: 1.5, max: 4, step: 0.5, def: 2.5, label: (v) => `gamma ${v}` },
  noise: { min: 5, max: 40, step: 5, def: 15, label: (v) => `σ = ${v}` },
  blur: { min: 3, max: 21, step: 2, def: 9, label: (v) => `nhân ${v} px` },
};

export const NO_DEGRADE: DegradeValue = { kind: null, level: 0 };

/** Mô phỏng điều kiện xấu trên máy chủ (giống thí nghiệm T4): tối, nhiễu, mờ chuyển động. */
export default function DegradeControl({ value, onChange }: { value: DegradeValue; onChange: (v: DegradeValue) => void }) {
  const r = value.kind ? RANGE[value.kind] : null;
  return (
    <div className="control">
      <span>Mô phỏng điều kiện xấu</span>
      <div className="row-flex">
        <Seg<string>
          value={value.kind ?? "none"}
          options={[
            { value: "none", label: "Gốc" },
            { value: "dark", label: "Tối" },
            { value: "noise", label: "Nhiễu" },
            { value: "blur", label: "Mờ" },
          ]}
          onChange={(k) => onChange(k === "none" ? NO_DEGRADE : { kind: k as Degrade, level: RANGE[k as Exclude<Degrade, null>].def })}
        />
        {r && (
          <label className="row-flex small">
            <input type="range" min={r.min} max={r.max} step={r.step} value={value.level} onChange={(e) => onChange({ ...value, level: Number(e.target.value) })} />
            <span className="num">{r.label(value.level)}</span>
          </label>
        )}
      </div>
    </div>
  );
}

export function degradeLabel(d: DegradeValue): string {
  return d.kind ? `${{ dark: "tối", noise: "nhiễu", blur: "mờ" }[d.kind]} (${RANGE[d.kind].label(d.level)})` : "gốc";
}
