import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { DetectResponse } from "../api/types";
import BoxOverlay from "../components/BoxOverlay";
import DetectionList from "../components/DetectionList";
import Dropzone from "../components/Dropzone";
import Latency from "../components/Latency";

/** Trang Ảnh (FR-WEB-01): tải ảnh -> box + nhãn tiếng Việt + danh sách biển. */
export default function ImagePage() {
  const [src, setSrc] = useState<string | null>(null);
  const [result, setResult] = useState<DetectResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<number | null>(null);

  useEffect(() => () => void (src && URL.revokeObjectURL(src)), [src]);

  async function run(file: File) {
    setSrc(URL.createObjectURL(file));
    setResult(null);
    setError(null);
    setSelected(null);
    setBusy(true);
    try {
      setResult(await api.detectImage(file, { annotate: false }));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section>
      <h1>Nhận diện từ ảnh</h1>
      <Dropzone accept="image/jpeg,image/png,image/bmp,image/webp" hint="Kéo-thả hoặc bấm để chọn ảnh (JPEG/PNG, ≤ 10 MB)" disabled={busy} onFile={run} />
      {busy && <p className="muted">Đang xử lý…</p>}
      {error && <p className="error">Lỗi: {error}</p>}
      {src && (
        <div className="split">
          <div>
            {result ? (
              <BoxOverlay src={src} size={result.image_size} detections={result.detections} selected={selected} onSelect={setSelected} />
            ) : (
              <img className="preview" src={src} alt="ảnh đã chọn" />
            )}
            {result && <Latency ms={result.latency_ms} />}
          </div>
          {result && (
            <div>
              <h2>Biển báo ({result.detections.length})</h2>
              <DetectionList detections={result.detections} selected={selected} onSelect={setSelected} />
            </div>
          )}
        </div>
      )}
    </section>
  );
}
