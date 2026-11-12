// Kiểu dữ liệu tĩnh do scripts/export_web_data.py sinh ra (web/public/data/*.json).

export interface Eda {
  totals: {
    images: number;
    boxes: number;
    classes: number;
    raw_classes: number;
    background_images: number;
    clusters: number;
    median_side_px: number;
    pct_lt16: number;
    pct_lt32: number;
    imbalance: number;
    excluded_images: number;
  };
  splits: Record<"train" | "val" | "test", { images: number; boxes: number }>;
  per_class: {
    id: number;
    name: string;
    superclass: string;
    qcvn: string;
    train: number;
    val: number;
    test: number;
    total: number;
    clusters: number;
    median_px: number;
    pct_lt16: number;
    raw_ids: number[];
  }[];
  superclasses: { key: string; name: string; boxes: number }[];
  size_hist: { bin: string; boxes: number }[];
  resolutions: { res: string; images: number }[];
  signs_per_image: { n: number; images: number }[];
  position_heatmap: number[][];
  merged: { into: string; raw_ids: number[]; raw_names: string[] };
  audit: Record<string, number>;
}

type Row = Record<string, number | string | null>;

export interface Results {
  model: {
    run_id: string;
    author: string;
    dataset_version: string;
    started_at: string;
    duration_s: number;
    config: Record<string, unknown>;
    environment: Record<string, string | boolean>;
    metrics: Record<string, number>;
  };
  training: { epoch: number; train_box: number; train_cls: number; val_box: number; val_cls: number; precision: number; recall: number; map50: number; map50_95: number }[];
  bootstrap: { metric: string; value: number; ci95_low: number; ci95_high: number }[];
  per_class: { id: number; ten: string; n: number; recall: number; recall_ci95: string; precision: number; recall_ge16px: number; ti_le_bien_nho: number }[];
  per_class_ap: { id: number; ten: string; test_P: number; test_R: number; test_AP50: number; test_AP: number }[];
  similarity: { group: string; anh: number; bien: number; dung: number; ti_le_bien_nho: number; recall: number; recall_ge16px: number; precision: number }[];
  e1: Row[];
  e2: Row[];
  e4_ablation: Row[];
  t3: Row[];
  e8: { phuong_phap: string; kich_thuoc: string; n: number; accuracy: number; ci95: string; macro_F1: number; n_yolo_tim_thay: number; accuracy_tren_bien_yolo_tim_thay: number }[];
  e8_paired: { kich_thuoc: string; n: number; delta_acc: number; ci95_low: number; ci95_high: number }[];
  t4: { dieu_kien: string; che_do: string; ti_le_anh_tang_cuong: number; P: number; R: number; dP: number | null; dP_ci95: string | null; dR: number | null; dR_ci95: string | null }[];
  t1: Row[];
  sift_keypoints: { size: string; median: number; pct_lt5: number }[];
  benchmarks: { gpu_detector_ms_1280: number; docker_cpu_image_s: [number, number]; ws_cpu_fps: number; ws_docker_cpu_fps: number };
  registry: { run_id: string; exp: string; date: string; author: string; platform: string; gpu: string; dataset_version: string; notes: string }[];
}
