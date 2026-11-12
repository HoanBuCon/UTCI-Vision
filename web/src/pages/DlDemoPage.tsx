import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import type { DetectResponse } from "../api/types";
import { useLoaded } from "../api/useHealth";
import BeforeAfter from "../components/BeforeAfter";
import BoxOverlay from "../components/BoxOverlay";
import DegradeControl, { degradeLabel, NO_DEGRADE, type DegradeValue } from "../components/DegradeControl";
import DetectionList from "../components/DetectionList";
import Icon from "../components/Icon";
import InputPicker, { type PickedInput } from "../components/InputPicker";
import Latency from "../components/Latency";
import { Busy, Card, download, PageHead, Seg, Switch } from "../components/ui";

interface Opts {
  enhance: boolean;
  verifier: boolean;
  imgsz: number;
  tiled: boolean;
  degrade: DegradeValue;
}
const DEFAULT: Opts = { enhance: true, verifier: false, imgsz: 1280, tiled: false, degrade: NO_DEGRADE };

interface HistoryRow {
  input: string;
  opts: Opts;
  n: number;
  small: number;
  ms: number;
}

function optsLabel(o: Opts): string {
  return [`${o.imgsz}px`, o.tiled && "cắt ô", o.enhance ? "tăng cường" : "không tăng cường", o.verifier && "xác minh", degradeLabel(o.degrade)].filter(Boolean).join(" · ");
}

/** Demo hệ thống học sâu: ảnh mẫu / upload, bật tắt từng khâu (ablation trực tiếp), mô phỏng điều kiện xấu, lịch sử chạy. */
export default function DlDemoPage() {
  const [picked, setPicked] = useState<PickedInput | null>(null);
  const [opts, setOpts] = useState<Opts>(DEFAULT);
  const [res, setRes] = useState<DetectResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [history, setHistory] = useState<HistoryRow[]>([]);
  const verifierLoaded = useLoaded("verifier");
  const seq = useRef(0);

  async function run(p: PickedInput | null = picked, o: Opts = opts) {
    if (!p) return;
    const id = ++seq.current;
    setBusy(true);
    setError(null);
    try {
      const r = await api.detect(p.input, {
        annotate: true,
        debug: true,
        returnInput: true,
        enhance: o.enhance,
        verifier: o.verifier,
        imgsz: o.imgsz,
        tiled: o.tiled,
        degrade: o.degrade.kind,
        level: o.degrade.kind ? o.degrade.level : null,
      });
      if (id !== seq.current) return;
      setRes(r);
      setSelected(null);
      const small = r.detections.filter((d) => Math.sqrt((d.bbox[2] - d.bbox[0]) * (d.bbox[3] - d.bbox[1])) < 16).length;
      setHistory((h) => [{ input: p.label, opts: o, n: r.detections.length, small, ms: r.latency_ms.total ?? 0 }, ...h].slice(0, 12));
    } catch (e) {
      if (id === seq.current) setError((e as Error).message);
    } finally {
      if (id === seq.current) setBusy(false);
    }
  }

  // chạy lại khi đổi tuỳ chọn (đã có ảnh)
  const first = useRef(true);
  useEffect(() => {
    if (first.current) {
      first.current = false;
      return;
    }
    const t = window.setTimeout(() => run(), 250);
    return () => window.clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [opts]);

  const set = (patch: Partial<Opts>) => setOpts((o) => ({ ...o, ...patch }));
  const dbg = (res?.debug ?? {}) as { ops?: string[]; images?: Record<string, string> };
  const enhanced = dbg.images?.enhanced;

  return (
    <>
      <PageHead
        title="Demo học sâu — YOLO11s"
        desc="Pipeline đầy đủ: đánh giá chất lượng → tăng cường thích nghi [CV] → YOLO11s phát hiện + phân loại 27 lớp [DL] → (bộ xác minh) → đọc số / chữ bằng VietOCR. Bật tắt từng khâu để thấy ảnh hưởng ngay trên ảnh."
      />
      <Card title="1. Chọn ảnh">
        <InputPicker
          value={picked}
          disabled={busy}
          onChange={(p) => {
            setPicked(p);
            setRes(null);
            run(p);
          }}
        />
      </Card>
      <Card title="2. Cấu hình pipeline" note="Mặc định = cấu hình đã chọn sau thí nghiệm: 1280 px, tăng cường thích nghi bật, bộ xác minh tắt (E2: tăng precision nhưng giảm recall biển nhỏ).">
        <div className="controls">
          <div className="control">
            <span>Kích thước suy luận</span>
            <Seg value={opts.imgsz} onChange={(v) => set({ imgsz: v })} options={[{ value: 960, label: "960" }, { value: 1280, label: "1280" }, { value: 1600, label: "1600" }]} />
          </div>
          <div className="control">
            <span>Khâu</span>
            <div className="row-flex">
              <Switch label="Tăng cường thích nghi" checked={opts.enhance} onChange={(v) => set({ enhance: v })} />
              <Switch
                label="Bộ xác minh"
                checked={opts.verifier}
                disabled={verifierLoaded === false}
                title={verifierLoaded === false ? "Chưa có trọng số bộ xác minh" : "LightGBM trên đặc trưng ngữ cảnh YOLO + màu + hình học"}
                onChange={(v) => set({ verifier: v })}
              />
              <Switch label="Cắt ô (tiling)" checked={opts.tiled} title="Chạy YOLO trên các ô 640 px chồng lấn — tăng recall biển nhỏ, giảm precision, chậm hơn (T3)" onChange={(v) => set({ tiled: v })} />
            </div>
          </div>
          <DegradeControl value={opts.degrade} onChange={(d) => set({ degrade: d })} />
          <div className="row-flex">
            <button className="btn-primary" disabled={!picked || busy} onClick={() => run()}>
              <Icon name="play" size={16} /> Chạy lại
            </button>
            <button onClick={() => setOpts(DEFAULT)} disabled={busy}>
              Mặc định
            </button>
          </div>
        </div>
      </Card>

      {error && <p className="error">Lỗi: {error}</p>}
      {!picked && <div className="empty card">Chọn một ảnh mẫu hoặc tải ảnh lên để bắt đầu.</div>}
      {picked && (
        <Card
          title={`3. Kết quả${res ? ` — ${res.detections.length} biển` : ""}`}
          extra={
            <div className="row-flex">
              {busy && <Busy />}
              {res && (
                <>
                  <button onClick={() => download("ket_qua.json", JSON.stringify({ input: picked.label, config: opts, ...res, annotated_image: undefined, input_image: undefined, debug: undefined }, null, 2))}>
                    <Icon name="download" size={16} /> JSON
                  </button>
                  {res.annotated_image && (
                    <button onClick={() => download("ket_qua.jpg", res.annotated_image!)}>
                      <Icon name="download" size={16} /> Ảnh
                    </button>
                  )}
                </>
              )}
            </div>
          }
        >
          <div className="split">
            <div>
              {res?.input_image ? (
                <BoxOverlay src={res.input_image} size={res.image_size} detections={res.detections} selected={selected} onSelect={setSelected} />
              ) : (
                <img className="preview" src={picked.preview} alt="ảnh đã chọn" />
              )}
              {res && <Latency ms={res.latency_ms} />}
              {res && enhanced && res.input_image && (
                <div style={{ marginTop: 14 }}>
                  <h3>Tăng cường thích nghi: {dbg.ops?.join(", ")}</h3>
                  <BeforeAfter before={res.input_image} after={enhanced} beforeLabel="Đầu vào" afterLabel="Sau tăng cường" />
                </div>
              )}
              {res && !enhanced && opts.enhance && <p className="small muted">Ảnh đủ sáng / đủ tương phản → bộ đánh giá chất lượng giữ nguyên ảnh.</p>}
            </div>
            <div>{res ? <DetectionList detections={res.detections} selected={selected} onSelect={setSelected} /> : busy ? <Busy /> : null}</div>
          </div>
        </Card>
      )}

      {history.length > 0 && (
        <Card title="Lịch sử chạy (phiên này)" note="So sánh nhanh các cấu hình trên cùng ảnh — ví dụ 960 vs 1280 với biển nhỏ, hoặc bật / tắt tăng cường với ảnh tối.">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Ảnh</th>
                  <th>Cấu hình</th>
                  <th className="num">Số biển</th>
                  <th className="num">Biển &lt; 16 px</th>
                  <th className="num">Thời gian (ms)</th>
                </tr>
              </thead>
              <tbody>
                {history.map((h, i) => (
                  <tr key={i} className={i === 0 ? "hl" : ""}>
                    <td>{h.input}</td>
                    <td>{optsLabel(h.opts)}</td>
                    <td className="num">{h.n}</td>
                    <td className="num">{h.small}</td>
                    <td className="num">{h.ms.toFixed(0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </>
  );
}
