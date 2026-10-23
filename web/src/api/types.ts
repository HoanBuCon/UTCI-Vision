// Đồng bộ thủ công với src/utci_vision/api/schemas.py (hợp đồng API — chốt ở Sprint 1).

export type BBox = [number, number, number, number];

export interface SignValue {
  number: number;
  unit: string;
  confidence: number;
}

export interface SignText {
  text: string;
  raw: string;
  confidence: number;
  parsed: Record<string, unknown>;
}

export interface Detection {
  bbox: BBox;
  class_id: number;
  class_name: string;
  superclass: string;
  score: number;
  verified: boolean | null;
  track_id: number | null;
  value: SignValue | null;
  text: SignText | null;
  sub_sign: SignText | null;
}

export interface DetectResponse {
  frame: number;
  image_size: [number, number];
  latency_ms: Record<string, number>;
  detections: Detection[];
  annotated_image: string | null;
  debug: Record<string, unknown> | null;
}

export interface ModelStatus {
  loaded: boolean;
  path: string | null;
  detail: string | null;
}

export interface HealthResponse {
  status: "ok" | "degraded";
  version: string;
  device: string;
  models: Record<string, ModelStatus>;
}

export interface ClassInfo {
  id: number;
  name_vi: string;
  superclass: string;
  superclass_vi: string;
  qcvn: string;
  meaning: string;
  has_value: boolean;
  value_unit: string | null;
  has_text: boolean;
}

export interface JobStatus {
  job_id: string;
  status: "queued" | "running" | "done" | "failed";
  progress: number;
  result_video_url: string | null;
  summary: Record<string, unknown>[];
  error: string | null;
}
