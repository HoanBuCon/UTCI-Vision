import type { Detection, SignText } from "../api/types";
import { useClasses } from "../api/useClasses";

function parsedText(t: SignText): string {
  const p = t.parsed as { time_ranges?: string[][]; distance_m?: number; except_vehicles?: string[] };
  const parts: string[] = [];
  if (p.time_ranges) parts.push(`khung giờ ${p.time_ranges.map((r) => r.join("–")).join(", ")}`);
  if (p.distance_m !== undefined) parts.push(`cách ${p.distance_m} m`);
  if (p.except_vehicles) parts.push(`trừ ${p.except_vehicles.join(", ")}`);
  return parts.length ? ` (${parts.join("; ")})` : "";
}

interface Props {
  detections: Detection[];
  selected?: number | null;
  onSelect?: (index: number) => void;
}

/** Danh sách biển: tên, siêu lớp, QCVN, ý nghĩa, độ tin cậy, giá trị số, chữ, biển phụ. */
export default function DetectionList({ detections, selected, onSelect }: Props) {
  const classes = useClasses();
  if (!detections.length) return <p className="muted">Không phát hiện biển báo nào.</p>;
  return (
    <ol className="detections">
      {detections.map((d, i) => {
        const info = classes[d.class_id];
        return (
          <li key={i} className={selected === i ? "selected" : ""} onClick={() => onSelect?.(i)}>
            <div className="row">
              <strong>
                {i + 1}. {d.class_name}
              </strong>
              <span className={`tag tag-${d.superclass}`}>{info?.superclass_vi ?? d.superclass}</span>
              {info?.qcvn && <span className="muted small">{info.qcvn}</span>}
              <span className="score">{(d.score * 100).toFixed(0)}%</span>
            </div>
            {info?.meaning && <p className="small">{info.meaning}</p>}
            {d.value && (
              <p className="value">
                Giá trị: <b>{d.value.number} {d.value.unit}</b>
              </p>
            )}
            {d.text && (
              <p className="small">
                Chữ trên biển: <b>{d.text.text}</b>
                {parsedText(d.text)}
              </p>
            )}
            {d.sub_sign && (
              <p className="small">
                Biển phụ: <b>{d.sub_sign.text}</b>
                {parsedText(d.sub_sign)}
              </p>
            )}
            {d.verified === false && <p className="small warn">Bộ xác minh đánh giá có thể là nhận nhầm</p>}
          </li>
        );
      })}
    </ol>
  );
}
