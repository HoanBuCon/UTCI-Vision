import type { ClassInfo, CompareResponse, DetectResponse, HealthResponse, JobStatus, Sample, TraditionalResponse } from "./types";

const BASE = "/api/v1";

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = await res.text();
    try {
      detail = (JSON.parse(detail) as { detail?: string }).detail ?? detail;
    } catch {
      /* giữ nguyên text */
    }
    throw new Error(`${res.status}: ${detail}`);
  }
  return (await res.json()) as T;
}

/** Ảnh đầu vào: file người dùng chọn hoặc id ảnh mẫu trên máy chủ. */
export type ImageInput = { file: File } | { sample: string };

export type Degrade = "dark" | "noise" | "blur" | null;

export interface DetectOptions {
  annotate?: boolean;
  debug?: boolean;
  returnInput?: boolean;
  enhance?: boolean | null;
  verifier?: boolean | null;
  imgsz?: number | null;
  tiled?: boolean;
  degrade?: Degrade;
  level?: number | null;
}

function buildRequest(input: ImageInput, params: Record<string, string | number | boolean | null | undefined>) {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) if (v !== null && v !== undefined && v !== "") q.set(k, String(v));
  const body = new FormData();
  if ("sample" in input) q.set("sample", input.sample);
  else body.append("file", input.file);
  return { query: q.toString(), body };
}

export const api = {
  health: () => fetch(`${BASE}/health`).then((r) => json<HealthResponse>(r)),
  classes: () => fetch(`${BASE}/classes`).then((r) => json<ClassInfo[]>(r)),
  samples: () => fetch(`${BASE}/samples`).then((r) => json<Sample[]>(r)),
  sampleImageUrl: (id: string) => `${BASE}/samples/${id}/image`,

  /** Nhận diện bằng hệ thống học sâu (pipeline đầy đủ), có thể ghi đè cấu hình (ablation trực tiếp). */
  detect: (input: ImageInput, o: DetectOptions = {}) => {
    const { query, body } = buildRequest(input, {
      annotate: o.annotate ?? false,
      debug: o.debug ?? false,
      return_input: o.returnInput ?? false,
      enhance: o.enhance,
      verifier: o.verifier,
      imgsz: o.imgsz,
      tiled: o.tiled,
      degrade: o.degrade,
      level: o.level,
    });
    return fetch(`${BASE}/detect/image?${query}`, { method: "POST", body }).then((r) => json<DetectResponse>(r));
  },
  /** Giữ tương thích trang cũ. */
  detectImage: (file: File, opts: { annotate?: boolean; debug?: boolean } = {}) => api.detect({ file }, opts),

  traditional: (input: ImageInput, o: { enhance?: boolean; degrade?: Degrade; level?: number | null } = {}) => {
    const { query, body } = buildRequest(input, { enhance: o.enhance ?? true, degrade: o.degrade, level: o.level });
    return fetch(`${BASE}/traditional/analyze?${query}`, { method: "POST", body }).then((r) => json<TraditionalResponse>(r));
  },

  compare: (input: ImageInput, o: { enhance?: boolean; imgsz?: number | null; degrade?: Degrade; level?: number | null } = {}) => {
    const { query, body } = buildRequest(input, { enhance: o.enhance ?? true, imgsz: o.imgsz, degrade: o.degrade, level: o.level });
    return fetch(`${BASE}/compare?${query}`, { method: "POST", body }).then((r) => json<CompareResponse>(r));
  },

  createVideoJob: (file: File) => {
    const body = new FormData();
    body.append("file", file);
    return fetch(`${BASE}/jobs/video`, { method: "POST", body }).then((r) => json<{ job_id: string }>(r));
  },
  jobStatus: (jobId: string) => fetch(`${BASE}/jobs/${jobId}`).then((r) => json<JobStatus>(r)),

  /** WebSocket webcam: gửi JPEG (Blob), nhận DetectResponse. Gửi frame tiếp theo chỉ sau khi nhận kết quả (back-pressure). */
  streamUrl: () => `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}${BASE}/stream`,
};

/** Dữ liệu tĩnh (scripts/export_web_data.py -> web/public/data). */
const staticCache: Record<string, Promise<unknown>> = {};
export function loadStatic<T>(name: "eda" | "results"): Promise<T> {
  staticCache[name] ??= fetch(`/data/${name}.json`).then((r) => {
    if (!r.ok) throw new Error(`Thiếu /data/${name}.json — chạy scripts/export_web_data.py`);
    return r.json();
  });
  return staticCache[name] as Promise<T>;
}
