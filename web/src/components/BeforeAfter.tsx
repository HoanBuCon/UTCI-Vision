import { useRef, useState } from "react";

/** Thanh trượt so sánh hai ảnh cùng kích thước (trái: before, phải: after). Kéo chuột / chạm hoặc dùng phím ← →. */
export default function BeforeAfter({ before, after, beforeLabel = "Trước", afterLabel = "Sau" }: { before: string; after: string; beforeLabel?: string; afterLabel?: string }) {
  const [pos, setPos] = useState(50);
  const ref = useRef<HTMLDivElement>(null);
  const drag = useRef(false);
  const move = (clientX: number) => {
    const r = ref.current?.getBoundingClientRect();
    if (r) setPos(Math.min(100, Math.max(0, ((clientX - r.left) / r.width) * 100)));
  };
  return (
    <div
      ref={ref}
      className="ba"
      tabIndex={0}
      role="slider"
      aria-label="So sánh trước / sau"
      aria-valuenow={Math.round(pos)}
      aria-valuemin={0}
      aria-valuemax={100}
      onPointerDown={(e) => {
        drag.current = true;
        (e.target as Element).setPointerCapture?.(e.pointerId);
        move(e.clientX);
      }}
      onPointerMove={(e) => drag.current && move(e.clientX)}
      onPointerUp={() => (drag.current = false)}
      onKeyDown={(e) => {
        if (e.key === "ArrowLeft") setPos((p) => Math.max(0, p - 5));
        if (e.key === "ArrowRight") setPos((p) => Math.min(100, p + 5));
      }}
    >
      <img src={before} alt={beforeLabel} draggable={false} />
      <div className="after" style={{ clipPath: `inset(0 0 0 ${pos}%)` }}>
        <img src={after} alt={afterLabel} draggable={false} />
      </div>
      <div className="handle" style={{ left: `${pos}%` }} />
      <span className="tag-l">{beforeLabel}</span>
      <span className="tag-r">{afterLabel}</span>
    </div>
  );
}
