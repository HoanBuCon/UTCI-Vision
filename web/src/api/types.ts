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
  input_image: string | null;
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

export interface Sample {
  id: string;
  title: string;
  group: string;
  signs: number;
  small: number;
  size: string;
}

export interface Candidate {
  bbox: BBox;
  color: string;
  shape: string;
  class_id: number | null;
  class_name: string | null;
  score: number | null;
  crop: string | null;
  hog_image: string | null;
  sift_image: string | null;
  sift_keypoints: number | null;
}

export interface TraditionalResponse {
  image_size: [number, number];
  latency_ms: Record<string, number>;
  quality: Record<string, number>;
  ops: string[];
  images: Record<string, string>;
  candidates: Candidate[];
  detections: Detection[];
}

export interface CompareRow {
  bbox: BBox;
  side_px: number;
  yolo_class_id: number;
  yolo_class_name: string;
  yolo_score: number;
  classic_class_id: number | null;
  classic_class_name: string | null;
  classic_score: number | null;
  agree: boolean;
}

export interface ComparePart {
  detections: Detection[];
  latency_ms: Record<string, number>;
  annotated_image: string | null;
}

export interface CompareResponse {
  image_size: [number, number];
  input_image: string | null;
  deep: ComparePart;
  traditional: ComparePart;
  per_box: CompareRow[];
  classic_ms_per_box: number;
}
