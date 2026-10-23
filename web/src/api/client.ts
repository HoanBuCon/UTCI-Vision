import type { ClassInfo, DetectResponse, HealthResponse, JobStatus } from "./types";

const BASE = "/api/v1";

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return (await res.json()) as T;
}

export const api = {
  health: () => fetch(`${BASE}/health`).then((r) => json<HealthResponse>(r)),
  classes: () => fetch(`${BASE}/classes`).then((r) => json<ClassInfo[]>(r)),

  detectImage: (file: File, opts: { annotate?: boolean; debug?: boolean } = {}) => {
    const body = new FormData();
    body.append("file", file);
    const q = new URLSearchParams({ annotate: String(opts.annotate ?? true), debug: String(opts.debug ?? false) });
    return fetch(`${BASE}/detect/image?${q}`, { method: "POST", body }).then((r) => json<DetectResponse>(r));
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
