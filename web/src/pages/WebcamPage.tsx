import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import type { Detection, DetectResponse } from "../api/types";
import { SUPERCLASS_COLOR } from "../api/useClasses";
import Latency from "../components/Latency";

const MAX_WIDTH = 960;

/** Trang Webcam realtime (FR-WEB-03): camera -> WebSocket (back-pressure) -> vẽ box + FPS + biển vừa gặp. */
export default function WebcamPage() {
  const video = useRef<HTMLVideoElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fps, setFps] = useState(0);
  const [last, setLast] = useState<DetectResponse | null>(null);
  const [seen, setSeen] = useState<Record<number, Detection>>({});
  const stop = useRef<() => void>(() => {});

  useEffect(() => () => stop.current(), []);

  async function start() {
    setError(null);
    setSeen({});
    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: { width: { ideal: 1280 } }, audio: false });
    } catch (e) {
      setError(`Không mở được camera: ${(e as Error).message}`);
      return;
    }
    const v = video.current!;
    v.srcObject = stream;
    await v.play();
    const grab = document.createElement("canvas");
    const ws = new WebSocket(api.streamUrl());
    ws.binaryType = "arraybuffer";
    let alive = true;
    let frames = 0;
    let t0 = performance.now();

    const send = () => {
      if (!alive || ws.readyState !== WebSocket.OPEN) return;
      const scale = Math.min(1, MAX_WIDTH / v.videoWidth);
      grab.width = Math.round(v.videoWidth * scale);
      grab.height = Math.round(v.videoHeight * scale);
      grab.getContext("2d")!.drawImage(v, 0, 0, grab.width, grab.height);
      grab.toBlob((blob) => blob && ws.readyState === WebSocket.OPEN && ws.send(blob), "image/jpeg", 0.7);
    };
    ws.onopen = send;
    ws.onmessage = (msg) => {
      const res = JSON.parse(msg.data as string) as DetectResponse & { error?: string };
      if (res.error) {
        setError(res.error);
        return;
      }
      setLast(res);
      draw(res);
      if (res.detections.length) {
        setSeen((prev) => {
          const next = { ...prev };
          for (const d of res.detections) if (d.track_id !== null) next[d.track_id] = d;
          return next;
        });
      }
      frames += 1;
      const now = performance.now();
      if (now - t0 > 1000) {
        setFps((frames * 1000) / (now - t0));
        frames = 0;
        t0 = now;
      }
      send(); // back-pressure: chỉ gửi frame mới khi đã nhận kết quả
    };
    ws.onerror = () => setError("Mất kết nối WebSocket");
    ws.onclose = () => alive && setError("WebSocket đã đóng");

    const draw = (res: DetectResponse) => {
      const c = canvas.current!;
      c.width = v.videoWidth;
      c.height = v.videoHeight;
      const ctx = c.getContext("2d")!;
      ctx.clearRect(0, 0, c.width, c.height);
      const s = v.videoWidth / res.image_size[0];
      ctx.font = `${Math.max(14, c.width / 50)}px system-ui`;
      for (const d of res.detections) {
        const [x1, y1, x2, y2] = d.bbox.map((n) => n * s);
        const color = SUPERCLASS_COLOR[d.superclass] ?? "#22c55e";
        ctx.strokeStyle = ctx.fillStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
        const label = `#${d.track_id ?? ""} ${d.class_name}${d.value ? ` ${d.value.number} ${d.value.unit}` : ""}`;
        ctx.fillText(label, x1, Math.max(16, y1 - 6));
      }
    };

    stop.current = () => {
      alive = false;
      ws.close();
      stream.getTracks().forEach((t) => t.stop());
      setRunning(false);
    };
    setRunning(true);
  }

  const recent = Object.entries(seen).sort(([a], [b]) => Number(b) - Number(a));
  return (
    <section>
      <h1>Webcam thời gian thực</h1>
      <p>
        {running ? (
          <button onClick={() => stop.current()}>Dừng</button>
        ) : (
          <button onClick={start}>Bật camera</button>
        )}{" "}
        {running && <span className="badge">{fps.toFixed(1)} FPS</span>}
      </p>
      {error && <p className="error">{error}</p>}
      <div className="split">
        <div className="webcam">
          <video ref={video} muted playsInline />
          <canvas ref={canvas} />
          {last && <Latency ms={last.latency_ms} />}
        </div>
        <div>
          <h2>Biển vừa gặp ({recent.length})</h2>
          <ul className="seen">
            {recent.map(([id, d]) => (
              <li key={id}>
                <span className={`tag tag-${d.superclass}`}>#{id}</span> {d.class_name}
                {d.value && <b> · {d.value.number} {d.value.unit}</b>}
                {d.text && <span> · {d.text.text}</span>}
                {d.sub_sign && <span className="small"> · biển phụ: {d.sub_sign.text}</span>}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
