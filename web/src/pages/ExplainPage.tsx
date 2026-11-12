import { useState } from "react";
import { api } from "../api/client";
import type { DetectResponse } from "../api/types";
import DetectionList from "../components/DetectionList";
import Dropzone from "../components/Dropzone";
import Latency from "../components/Latency";

const OP_LABEL: Record<string, string> = { gamma: "gamma tự động", clahe: "CLAHE kênh L", denoise: "lọc song phương" };

interface Debug {
  quality?: { mean_v: number; std_l: number; laplacian_var: number };
  ops?: string[];
  images?: Record<string, string>;
}

/** Chế độ Giải thích (FR-WEB-05, FR-PIPE-14): kết quả trung gian của từng khâu cho một ảnh. */
export default function ExplainPage() {
  const [res, setRes] = useState<DetectResponse | null>(null);
  const [src, setSrc] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run(file: File) {
    setSrc(URL.createObjectURL(file));
    setRes(null);
    setError(null);
    setBusy(true);
    try {
      setRes(await api.detectImage(file, { annotate: true, debug: true }));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const dbg = (res?.debug ?? {}) as Debug;
  const crops = Object.entries(dbg.images ?? {}).filter(([k]) => k !== "enhanced");
  return (
    <section>
      <h1>Giải thích pipeline</h1>
      <p className="muted">Tải một ảnh để xem từng khâu: phương pháp truyền thống [CV] và học sâu [DL] làm gì với ảnh.</p>
      <Dropzone accept="image/*" hint="Kéo-thả hoặc chọn ảnh" disabled={busy} onFile={run} />
      {busy && <p className="muted">Đang xử lý…</p>}
      {error && <p className="error">Lỗi: {error}</p>}
      {res && (
        <ol className="stages">
          <li>
            <h2>1. Đánh giá chất lượng ảnh [CV]</h2>
            {dbg.quality && (
              <p>
                Độ sáng V = <b>{dbg.quality.mean_v.toFixed(2)}</b> · tương phản (độ lệch chuẩn L) = <b>{dbg.quality.std_l.toFixed(2)}</b> · phương sai
                Laplacian = <b>{dbg.quality.laplacian_var.toFixed(0)}</b>
              </p>
            )}
            <p>
              {dbg.ops?.length
                ? `Ảnh cần tăng cường → áp dụng: ${dbg.ops.map((o) => OP_LABEL[o] ?? o).join(", ")}.`
                : "Ảnh đủ sáng, đủ tương phản → giữ nguyên (không tăng cường)."}
            </p>
          </li>
          <li>
            <h2>2. Tăng cường thích nghi [CV]</h2>
            <div className="pair">
              {src && <figure><img src={src} alt="gốc" /><figcaption>Ảnh gốc</figcaption></figure>}
              {dbg.images?.enhanced && <figure><img src={dbg.images.enhanced} alt="sau tăng cường" /><figcaption>Sau tăng cường</figcaption></figure>}
            </div>
          </li>
          <li>
            <h2>3. Phát hiện + phân loại bằng YOLO11 [DL] → theo vết, xác minh</h2>
            {res.annotated_image && <img className="preview" src={res.annotated_image} alt="kết quả" />}
            <Latency ms={res.latency_ms} />
          </li>
          <li>
            <h2>4. Cắt vùng số / dòng chữ / biển phụ [CV] → VietOCR [DL] → regex, từ điển</h2>
            {crops.length ? (
              <div className="crops">
                {crops.map(([k, v]) => (
                  <figure key={k}>
                    <img src={v} alt={k} />
                    <figcaption className="small">{k}</figcaption>
                  </figure>
                ))}
              </div>
            ) : (
              <p className="muted">Không có biển đủ lớn có số / chữ để đọc.</p>
            )}
          </li>
          <li>
            <h2>5. Kết quả cuối</h2>
            <DetectionList detections={res.detections} />
          </li>
        </ol>
      )}
    </section>
  );
}
