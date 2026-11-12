import { useEffect, useMemo, useState } from "react";
import { api, type ImageInput } from "../api/client";
import type { Sample } from "../api/types";
import Dropzone from "./Dropzone";

export interface PickedInput {
  input: ImageInput;
  preview: string; // URL hiển thị ảnh gốc
  label: string;
  key: string; // định danh để biết đầu vào đã đổi
}

let samplesCache: Promise<Sample[]> | null = null;
export function useSamples(): { samples: Sample[]; error: string | null } {
  const [samples, setSamples] = useState<Sample[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    samplesCache ??= api.samples().catch((e) => {
      samplesCache = null;
      throw e;
    });
    samplesCache.then(setSamples, (e: Error) => setError(e.message));
  }, []);
  return { samples, error };
}

/** Chọn ảnh đầu vào: thư viện ảnh mẫu (test của processed/v1, nhóm theo tình huống) hoặc tải ảnh lên. */
export default function InputPicker({ value, onChange, disabled }: { value: PickedInput | null; onChange: (p: PickedInput) => void; disabled?: boolean }) {
  const { samples, error } = useSamples();
  const groups = useMemo(() => ["Tất cả", ...new Set(samples.map((s) => s.group))], [samples]);
  const [group, setGroup] = useState("Tất cả");
  const shown = samples.filter((s) => group === "Tất cả" || s.group === group);

  function pickFile(file: File) {
    onChange({ input: { file }, preview: URL.createObjectURL(file), label: file.name, key: `file:${file.name}:${file.size}:${Date.now()}` });
  }

  return (
    <div>
      {samples.length > 0 && (
        <>
          <div className="picker-tabs">
            {groups.map((g) => (
              <button key={g} className={`chip ${g === group ? "on" : ""}`} onClick={() => setGroup(g)}>
                {g}
              </button>
            ))}
          </div>
          <div className="samples">
            {shown.map((s) => (
              <button
                key={s.id}
                className={`sample ${value?.key === `sample:${s.id}` ? "on" : ""}`}
                disabled={disabled}
                title={`${s.title} · ${s.signs} biển (${s.small} biển < 16 px) · ${s.size}`}
                onClick={() => onChange({ input: { sample: s.id }, preview: api.sampleImageUrl(s.id), label: s.title, key: `sample:${s.id}` })}
              >
                <img src={api.sampleImageUrl(s.id)} alt={s.title} loading="lazy" />
                <span className="n">{s.signs} biển</span>
                <span className="cap">{s.title}</span>
              </button>
            ))}
          </div>
        </>
      )}
      {error && <p className="small muted">Không tải được ảnh mẫu ({error}) — hãy tải ảnh của bạn lên.</p>}
      <div style={{ marginTop: 10 }}>
        <Dropzone accept="image/jpeg,image/png,image/bmp,image/webp" hint="Hoặc kéo-thả / bấm để tải ảnh của bạn (JPEG, PNG ≤ 10 MB)" disabled={disabled} onFile={pickFile} />
      </div>
    </div>
  );
}
