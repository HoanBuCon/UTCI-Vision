import { Fragment, useState } from "react";
import { api } from "../api/client";
import type { DetectResponse } from "../api/types";
import BeforeAfter from "../components/BeforeAfter";
import DetectionList from "../components/DetectionList";
import Icon from "../components/Icon";
import InputPicker, { type PickedInput } from "../components/InputPicker";
import Latency from "../components/Latency";
import { Busy, Card, PageHead } from "../components/ui";

interface Stage {
  id: string;
  name: string;
  kind: "CV" | "DL" | "CV+DL";
  short: string;
  detail: string;
  file: string;
  off?: boolean;
}

const DL_PIPE: Stage[] = [
  { id: "quality", name: "Đánh giá chất lượng", kind: "CV", short: "độ sáng, tương phản, độ nét", file: "enhance.py", detail: "Thu nhỏ ảnh, đo độ sáng trung bình kênh V (HSV), độ lệch chuẩn kênh L (Lab) và phương sai Laplacian. So với ngưỡng trong configs/pipeline.yaml để quyết định có cần tăng cường không — ảnh bình thường đi thẳng qua (không tốn thời gian, không làm hỏng ảnh tốt)." },
  { id: "enhance", name: "Tăng cường thích nghi", kind: "CV", short: "gamma / CLAHE / lọc song phương", file: "enhance.py", detail: "Gamma tự động đưa độ sáng về mức mục tiêu; CLAHE trên kênh L tăng tương phản cục bộ; lọc song phương giảm nhiễu nhưng giữ biên. T4: ảnh rất tối recall 0,686 → 0,822." },
  { id: "yolo", name: "YOLO11s", kind: "DL", short: "phát hiện + phân loại 27 lớp", file: "detector.py", detail: "YOLO11s (Ultralytics) fine-tune từ COCO trên processed/v1 ở 960 px, suy luận ở 1280 px (T3: tăng recall biển nhỏ). FP16 trên GPU. Tuỳ chọn cắt ô 640 px chồng lấn cho ảnh độ phân giải cao." },
  { id: "verify", name: "Bộ xác minh", kind: "CV+DL", short: "LightGBM, tắt mặc định", file: "verifier.py", off: true, detail: "LightGBM trên đặc trưng ngữ cảnh YOLO + màu HSV + hình học + Hu moments + HOG để loại báo động giả. AUC 0,945 nhưng giảm recall biển nhỏ (E2) nên tắt mặc định; bật lại trên trang Demo học sâu." },
  { id: "track", name: "Theo vết", kind: "CV", short: "Kalman + Hungarian (video)", file: "tracking.py", detail: "Video / webcam: bộ lọc Kalman dự đoán vị trí, ghép bằng thuật toán Hungarian theo IoU, bỏ phiếu nhãn theo vết → giảm nhấp nháy và nhãn nhảy giữa các khung hình." },
  { id: "ocr", name: "Đọc số / chữ", kind: "CV+DL", short: "cắt vùng [CV] → VietOCR [DL]", file: "ocr.py", detail: "Với biển có giá trị (tốc độ, tải trọng, chiều cao) và biển phụ: cắt vùng chữ bằng chiếu histogram + ngưỡng [CV], đọc bằng VietOCR (VGG + Transformer) [DL], chuẩn hoá bằng regex + từ điển; bỏ kết quả độ tin cậy < 0,75." },
  { id: "out", name: "Kết quả", kind: "CV", short: "tên tiếng Việt, QCVN, ý nghĩa", file: "pipeline.py", detail: "Ghép lớp với thông tin QCVN 41:2019 (configs/classes.yaml): tên, nhóm biển, mã hiệu, ý nghĩa, giá trị đọc được → API JSON + ảnh vẽ khung." },
];

const CV_PIPE: Stage[] = [
  { id: "c-enh", name: "Tăng cường", kind: "CV", short: "dùng chung với hệ DL", file: "enhance.py", detail: "Cùng khâu đánh giá chất lượng + tăng cường thích nghi như hệ thống học sâu." },
  { id: "c-hsv", name: "Phân đoạn màu HSV", kind: "CV", short: "đỏ (2 dải H) / xanh / vàng", file: "traditional.py", detail: "Ngưỡng HSV theo màu quy chuẩn QCVN: viền đỏ (biển cấm), nền xanh (hiệu lệnh, chỉ dẫn), nền vàng (nguy hiểm). Mở / đóng hình thái học để bỏ nhiễu và nối viền." },
  { id: "c-shape", name: "Contour + hình dạng", kind: "CV", short: "tròn / tam giác / chữ nhật", file: "traditional.py", detail: "Contour ngoài → độ tròn của bao lồi (viền đỏ là vòng rỗng), số đỉnh xấp xỉ đa giác, solidity, tỉ lệ khung → vùng ứng viên; NMS và loại mảnh màu nằm trong biển lớn." },
  { id: "c-feat", name: "HOG + histogram HSV", kind: "CV", short: "đặc trưng thủ công", file: "traditional.py", detail: "Crop ứng viên (nới 10%) đưa về 32×32 xám, HOG (9 hướng, ô 8×8, khối 2×2) mô tả hình dạng ký hiệu + histogram HSV 16×4 mô tả màu." },
  { id: "c-svm", name: "SVM (RBF)", kind: "CV", short: "27 lớp + lớp nền", file: "train_hog_svm.py", detail: "SVM RBF có lớp “nền” huấn luyện từ ứng viên không trùng biển thật → loại vùng màu giả. Val: accuracy biển 0,880, nhận đúng nền 0,971. Khi cho đúng vùng biển (E8): HOG + màu + SVM 0,910 so với YOLO 0,924." },
];

function Flow({ stages, sel, onSel }: { stages: Stage[]; sel: string; onSel: (id: string) => void }) {
  return (
    <div className="flow">
      {stages.map((s, i) => (
        <Fragment key={s.id}>
          {i > 0 && (
            <span className="arrow">
              <Icon name="arrow" size={16} />
            </span>
          )}
          <button className={`stage ${sel === s.id ? "on" : ""} ${s.off ? "off" : ""}`} onClick={() => onSel(s.id)}>
            <span className={`pill ${s.kind === "DL" ? "pill-dl" : "pill-cv"}`}>{s.kind}</span>
            <b>{s.name}</b>
            <span className="small muted">{s.short}</span>
          </button>
        </Fragment>
      ))}
    </div>
  );
}

interface Debug {
  quality?: { mean_v: number; std_l: number; laplacian_var: number };
  ops?: string[];
  images?: Record<string, string>;
}

/** Giải thích pipeline: sơ đồ tương tác hai hệ thống + chạy một ảnh để xem kết quả trung gian từng khâu (FR-WEB-05). */
export default function PipelinePage() {
  const [sel, setSel] = useState("yolo");
  const stage = [...DL_PIPE, ...CV_PIPE].find((s) => s.id === sel)!;
  const [picked, setPicked] = useState<PickedInput | null>(null);
  const [res, setRes] = useState<DetectResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run(p: PickedInput) {
    setPicked(p);
    setRes(null);
    setError(null);
    setBusy(true);
    try {
      setRes(await api.detect(p.input, { annotate: true, debug: true, returnInput: true }));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const dbg = (res?.debug ?? {}) as Debug;
  const crops = Object.entries(dbg.images ?? {}).filter(([k]) => k !== "enhanced");

  return (
    <>
      <PageHead title="Pipeline hệ thống" desc="Hệ thống kết hợp CV truyền thống [CV] và học sâu [DL]. Bấm vào từng khâu để xem nó làm gì; chạy một ảnh bên dưới để xem kết quả trung gian thật." />
      <Card title="Sơ đồ">
        <div className="lanes">
          <div className="lane">
            <div className="lane-title">
              <span className="pill pill-dl">Hệ thống chính</span> Học sâu + tiền / hậu xử lý truyền thống (dùng trong API, video, webcam)
            </div>
            <Flow stages={DL_PIPE} sel={sel} onSel={setSel} />
          </div>
          <div className="lane">
            <div className="lane-title">
              <span className="pill pill-cv">Hệ thống đối chứng</span> CV truyền thống hoàn toàn (trang Demo CV, So sánh)
            </div>
            <Flow stages={CV_PIPE} sel={sel} onSel={setSel} />
          </div>
        </div>
        <div className="callout" style={{ marginBottom: 0 }}>
          <b>
            {stage.name} <span className={`pill ${stage.kind === "DL" ? "pill-dl" : "pill-cv"}`}>{stage.kind}</span>
          </b>
          <p style={{ margin: "6px 0 0" }}>{stage.detail}</p>
          <p className="small muted" style={{ margin: "6px 0 0" }}>
            Mã nguồn: <code>{stage.file}</code>
          </p>
        </div>
      </Card>

      <Card title="Chạy thử từng khâu trên một ảnh">
        <InputPicker value={picked} disabled={busy} onChange={run} />
      </Card>
      {busy && <Busy />}
      {error && <p className="error">Lỗi: {error}</p>}
      {res && (
        <ol className="stages" style={{ marginTop: 16 }}>
          <li>
            <h2>1. Đánh giá chất lượng ảnh [CV]</h2>
            {dbg.quality && (
              <p>
                Độ sáng V = <b>{dbg.quality.mean_v.toFixed(2)}</b> · tương phản (độ lệch chuẩn L) = <b>{dbg.quality.std_l.toFixed(2)}</b> · phương sai Laplacian ={" "}
                <b>{dbg.quality.laplacian_var.toFixed(0)}</b>
              </p>
            )}
            <p>{dbg.ops?.length ? `Ảnh cần tăng cường → áp dụng: ${dbg.ops.join(", ")}.` : "Ảnh đủ sáng, đủ tương phản → giữ nguyên (không tăng cường)."}</p>
          </li>
          {dbg.images?.enhanced && res.input_image && (
            <li>
              <h2>2. Tăng cường thích nghi [CV]</h2>
              <BeforeAfter before={res.input_image} after={dbg.images.enhanced} beforeLabel="Gốc" afterLabel="Sau tăng cường" />
            </li>
          )}
          <li>
            <h2>3. YOLO11s phát hiện + phân loại [DL]</h2>
            {res.annotated_image && <img className="preview" src={res.annotated_image} alt="kết quả" />}
            <Latency ms={res.latency_ms} />
          </li>
          <li>
            <h2>4. Cắt vùng số / chữ / biển phụ [CV] → VietOCR [DL]</h2>
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
    </>
  );
}
