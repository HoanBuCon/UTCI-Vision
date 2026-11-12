const LABELS: Record<string, string> = {
  enhance: "Tăng cường [CV]",
  detector: "YOLO11 [DL]",
  tracking: "Theo vết [CV]",
  tasks: "Xác minh / OCR",
  total: "Tổng",
};

/** Thời gian xử lý từng khâu (ms). */
export default function Latency({ ms }: { ms: Record<string, number> }) {
  return (
    <p className="latency small muted">
      {Object.entries(ms).map(([k, v]) => (
        <span key={k}>
          {LABELS[k] ?? k}: <b>{v.toFixed(0)} ms</b>
        </span>
      ))}
    </p>
  );
}
