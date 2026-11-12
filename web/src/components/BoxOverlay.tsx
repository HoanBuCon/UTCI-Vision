import type { Detection } from "../api/types";
import { SUPERCLASS_COLOR } from "../api/useClasses";

interface Props {
  src: string;
  size: [number, number]; // (width, height) của ảnh gốc
  detections: Detection[];
  selected?: number | null;
  onSelect?: (index: number) => void;
}

/** Ảnh + lớp SVG vẽ box theo toạ độ ảnh gốc (co giãn theo khung hiển thị). */
export default function BoxOverlay({ src, size, detections, selected, onSelect }: Props) {
  const [w, h] = size;
  const stroke = Math.max(2, w / 400);
  const font = Math.max(12, w / 60);
  return (
    <div className="overlay">
      <img src={src} alt="ảnh đầu vào" />
      <svg viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
        {detections.map((d, i) => {
          const [x1, y1, x2, y2] = d.bbox;
          const color = SUPERCLASS_COLOR[d.superclass] ?? "#22c55e";
          const label = `${i + 1}. ${d.class_name}${d.value ? ` · ${d.value.number} ${d.value.unit}` : ""}`;
          return (
            <g key={i} onClick={() => onSelect?.(i)} className="box">
              <rect
                x={x1}
                y={y1}
                width={x2 - x1}
                height={y2 - y1}
                fill={selected === i ? `${color}33` : "transparent"}
                stroke={color}
                strokeWidth={selected === i ? stroke * 2 : stroke}
              />
              <text x={x1} y={Math.max(font, y1 - 4)} fontSize={font} fill={color} stroke="#fff" strokeWidth={font / 6} paintOrder="stroke">
                {label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
