import { useState } from "react";
import { api } from "../api/client";
import type { TraditionalResponse } from "../api/types";
import { useLoaded } from "../api/useHealth";
import BeforeAfter from "../components/BeforeAfter";
import DegradeControl, { NO_DEGRADE, type DegradeValue } from "../components/DegradeControl";
import DetectionList from "../components/DetectionList";
import InputPicker, { type PickedInput } from "../components/InputPicker";
import { Busy, Card, PageHead, Seg, Switch } from "../components/ui";

const STEPS = [
  { key: "input", label: "Đầu vào", note: "Ảnh gốc (đã áp dụng mô phỏng điều kiện xấu nếu chọn)." },
  { key: "enhanced", label: "Tăng cường", note: "Gamma tự động / CLAHE kênh L / lọc song phương — chỉ áp dụng khi bộ đánh giá chất lượng thấy cần." },
  { key: "masks", label: "Phân đoạn màu HSV", note: "Ngưỡng HSV cho đỏ (hai dải H), xanh, vàng → mở / đóng hình thái học. Màu tô: đỏ / xanh / vàng." },
  { key: "candidates", label: "Vùng ứng viên", note: "Contour → lọc theo độ tròn của bao lồi, số đỉnh (tam giác / chữ nhật), solidity, tỉ lệ khung → NMS + loại mảnh nằm trong biển lớn." },
  { key: "annotated", label: "Kết quả", note: "Ứng viên được SVM xếp vào 27 lớp biển hoặc lớp “nền” (loại bỏ); giữ những ứng viên có xác suất ≥ 0,30." },
];

const COLOR_VI: Record<string, string> = { red: "đỏ", blue: "xanh", yellow: "vàng" };

/** Demo CV truyền thống: từng bước màu + hình dạng → HOG + màu → SVM, có ảnh HOG và điểm SIFT cho từng ứng viên. */
export default function TraditionalPage() {
  const [picked, setPicked] = useState<PickedInput | null>(null);
  const [enhance, setEnhance] = useState(true);
  const [degrade, setDegrade] = useState<DegradeValue>(NO_DEGRADE);
  const [res, setRes] = useState<TraditionalResponse | null>(null);
  const [step, setStep] = useState("annotated");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const classicLoaded = useLoaded("classic");

  async function run(p = picked, e = enhance, d = degrade) {
    if (!p) return;
    setBusy(true);
    setError(null);
    try {
      setRes(await api.traditional(p.input, { enhance: e, degrade: d.kind, level: d.kind ? d.level : null }));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const steps = STEPS.filter((s) => res?.images[s.key]);
  const cur = STEPS.find((s) => s.key === step && res?.images[s.key]) ?? steps[steps.length - 1];
  const signs = res?.candidates.filter((c) => c.class_id !== null) ?? [];

  return (
    <>
      <PageHead
        title="Demo CV truyền thống"
        desc="Không dùng mạng nơ-ron: phân đoạn màu HSV + hình thái học + lọc hình dạng tìm vùng ứng viên, rồi đặc trưng thủ công HOG + histogram màu HSV và SVM (RBF) phân loại 27 lớp + lớp nền."
      />
      {classicLoaded === false && <p className="callout warn">Máy chủ chưa có bộ phân loại HOG + SVM — chạy <code>python scripts/train_hog_svm.py</code>.</p>}
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
      <Card title="2. Tuỳ chọn">
        <div className="controls">
          <Switch
            label="Tăng cường thích nghi"
            checked={enhance}
            onChange={(v) => {
              setEnhance(v);
              run(picked, v, degrade);
            }}
          />
          <DegradeControl
            value={degrade}
            onChange={(d) => {
              setDegrade(d);
              run(picked, enhance, d);
            }}
          />
          {busy && <Busy />}
        </div>
      </Card>
      {error && <p className="error">Lỗi: {error}</p>}
      {res && cur && (
        <>
          <Card
            title="3. Từng bước xử lý"
            extra={<Seg value={cur.key} onChange={setStep} options={steps.map((s) => ({ value: s.key, label: s.label }))} />}
            note={
              <>
                Thời gian: tăng cường {res.latency_ms.enhance?.toFixed(0)} ms · phân đoạn + contour {res.latency_ms.segment?.toFixed(0)} ms · HOG + SVM {res.latency_ms.classify?.toFixed(0)} ms (CPU). Chất lượng ảnh: độ sáng V ={" "}
                {res.quality.mean_v?.toFixed(2)}, tương phản {res.quality.std_l?.toFixed(2)}, độ nét (Laplacian) {res.quality.laplacian_var?.toFixed(0)}
                {res.ops.length ? ` → áp dụng ${res.ops.join(", ")}` : " → giữ nguyên"}.
              </>
            }
          >
            <p className="small muted" style={{ marginTop: 0 }}>
              {cur.note}
            </p>
            {cur.key === "enhanced" ? (
              <BeforeAfter before={res.images.input} after={res.images.enhanced} beforeLabel="Đầu vào" afterLabel="Sau tăng cường" />
            ) : (
              <img className="preview" src={res.images[cur.key]} alt={cur.label} />
            )}
          </Card>
          <div className="grid g2">
            <Card title={`Kết quả cuối: ${res.detections.length} biển`}>
              <DetectionList detections={res.detections} />
            </Card>
            <Card title="Thống kê ứng viên">
              <p>
                <b>{res.candidates.length}</b> vùng ứng viên từ màu + hình dạng → SVM giữ <b>{signs.length}</b> là biển, loại <b>{res.candidates.length - signs.length}</b> là nền.
              </p>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Màu</th>
                      <th>Hình</th>
                      <th className="num">Ứng viên</th>
                      <th className="num">Là biển</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(
                      res.candidates.reduce<Record<string, { n: number; s: number }>>((acc, c) => {
                        const k = `${c.color}|${c.shape}`;
                        acc[k] ??= { n: 0, s: 0 };
                        acc[k].n++;
                        if (c.class_id !== null) acc[k].s++;
                        return acc;
                      }, {}),
                    ).map(([k, v]) => (
                      <tr key={k}>
                        <td>{COLOR_VI[k.split("|")[0]]}</td>
                        <td>{k.split("|")[1]}</td>
                        <td className="num">{v.n}</td>
                        <td className="num">{v.s}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="card-note">
                Hạn chế đã biết: biển cùng màu đứng sát nhau bị gộp thành một contour; biển chỉ dẫn nhiều màu / chữ trắng và biển rất nhỏ thường không thành ứng viên. Đây là lý do pipeline
                truyền thống có recall thấp hơn YOLO dù bộ phân loại HOG + màu + SVM gần ngang YOLO khi được cho đúng vùng biển (E8).
              </p>
            </Card>
          </div>
          <Card title="4. Đặc trưng của từng ứng viên (tối đa 8 — vùng được nhận là biển trước)" note="HOG mô tả hướng gradient theo từng ô (ổn định với ánh sáng); SIFT cần nhiều chi tiết nên gần như không có điểm đặc trưng trên biển nhỏ — vì vậy SIFT-BoVW chỉ đạt 0,711 accuracy (E8).">
            <div className="cands">
              {res.candidates
                .filter((c) => c.crop)
                .sort((a, b) => Number(a.class_id === null) - Number(b.class_id === null))
                .map((c, i) => (
                  <div key={i} className={`cand ${c.class_id === null ? "bg" : ""}`}>
                    <div className="imgs">
                      <figure>
                        <img src={c.crop!} alt="vùng ứng viên" />
                        <figcaption>Vùng</figcaption>
                      </figure>
                      <figure>
                        <img src={c.hog_image!} alt="HOG" />
                        <figcaption>HOG</figcaption>
                      </figure>
                      <figure>
                        <img src={c.sift_image!} alt="SIFT" />
                        <figcaption>SIFT: {c.sift_keypoints} điểm</figcaption>
                      </figure>
                    </div>
                    <div className="meta">
                      <div>
                        {c.class_name ? <b>{c.class_name}</b> : <b className="muted">Nền (loại bỏ)</b>} <span className="num muted">· {((c.score ?? 0) * 100).toFixed(0)}%</span>
                      </div>
                      <div className="small muted">
                        màu {COLOR_VI[c.color]} · {c.shape} · {(c.bbox[2] - c.bbox[0]).toFixed(0)}×{(c.bbox[3] - c.bbox[1]).toFixed(0)} px
                      </div>
                    </div>
                  </div>
                ))}
            </div>
            {!res.candidates.length && <p className="muted">Không tìm thấy vùng ứng viên nào.</p>}
          </Card>
        </>
      )}
      {!picked && <div className="empty card">Chọn một ảnh mẫu hoặc tải ảnh lên để bắt đầu.</div>}
    </>
  );
}
