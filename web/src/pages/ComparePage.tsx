import { useState } from "react";
import { Bar, BarChart, CartesianGrid, ErrorBar, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api/client";
import type { Results } from "../api/staticTypes";
import type { CompareResponse } from "../api/types";
import { Legend, pctTick, Tip } from "../components/charts";
import DegradeControl, { NO_DEGRADE, type DegradeValue } from "../components/DegradeControl";
import InputPicker, { type PickedInput } from "../components/InputPicker";
import { Busy, Card, Kpi, PageHead, pct, Seg, Switch, useStatic } from "../components/ui";
import { useTheme } from "../theme";

const METHODS = ["YOLO11 (học sâu)", "HOG + màu + SVM", "HOG + SVM", "SIFT-BoVW + SVM"];
const SIZES = ["tất cả", "<16px", "16-32", "32-64", ">=64"];
const COND_VI: Record<string, string> = { goc: "Gốc", toi_gamma2: "Tối γ2.5", "toi_gamma2.5": "Tối γ2.5", rat_toi_gamma3: "Rất tối γ3.5", "rat_toi_gamma3.5": "Rất tối γ3.5", nhieu_sigma15: "Nhiễu σ15", mo_chuyen_dong: "Mờ chuyển động" };
const MODES = ["không xử lý", "tăng cường thích nghi", "luôn gamma + CLAHE"];

function LiveCompare() {
  const [picked, setPicked] = useState<PickedInput | null>(null);
  const [enhance, setEnhance] = useState(true);
  const [imgsz, setImgsz] = useState(1280);
  const [degrade, setDegrade] = useState<DegradeValue>(NO_DEGRADE);
  const [res, setRes] = useState<CompareResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run(p = picked, e = enhance, s = imgsz, d = degrade) {
    if (!p) return;
    setBusy(true);
    setError(null);
    try {
      setRes(await api.compare(p.input, { enhance: e, imgsz: s, degrade: d.kind, level: d.kind ? d.level : null }));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const agree = res?.per_box.filter((r) => r.agree).length ?? 0;
  const dlMs = res?.deep.latency_ms.total ?? 0;
  const cvMs = res?.traditional.latency_ms.total ?? 0;

  return (
    <>
      <Card title="Chạy cả hai hệ thống trên cùng một ảnh">
        <InputPicker
          value={picked}
          disabled={busy}
          onChange={(p) => {
            setPicked(p);
            setRes(null);
            run(p);
          }}
        />
        <div className="controls" style={{ marginTop: 14 }}>
          <div className="control">
            <span>YOLO imgsz</span>
            <Seg
              value={imgsz}
              onChange={(v) => {
                setImgsz(v);
                run(picked, enhance, v, degrade);
              }}
              options={[
                { value: 960, label: "960" },
                { value: 1280, label: "1280" },
              ]}
            />
          </div>
          <Switch
            label="Tăng cường thích nghi (cả hai)"
            checked={enhance}
            onChange={(v) => {
              setEnhance(v);
              run(picked, v, imgsz, degrade);
            }}
          />
          <DegradeControl
            value={degrade}
            onChange={(d) => {
              setDegrade(d);
              run(picked, enhance, imgsz, d);
            }}
          />
          {busy && <Busy />}
        </div>
      </Card>
      {error && <p className="error">Lỗi: {error}</p>}
      {res && (
        <>
          <div className="grid g2">
            <Card title={<><span className="pill pill-dl">DL</span> YOLO11s — {res.deep.detections.length} biển</>} note={`Tổng ${dlMs.toFixed(0)} ms (gồm tăng cường + YOLO; OCR tắt để so sánh công bằng).`}>
              {res.deep.annotated_image && <img className="preview" src={res.deep.annotated_image} alt="kết quả YOLO" />}
            </Card>
            <Card title={<><span className="pill pill-cv">CV</span> Màu + hình dạng + HOG + SVM — {res.traditional.detections.length} biển</>} note={`Tổng ${cvMs.toFixed(0)} ms trên CPU.`}>
              {res.traditional.annotated_image && <img className="preview" src={res.traditional.annotated_image} alt="kết quả truyền thống" />}
            </Card>
          </div>
          <Card
            title="Phân loại trên từng biển YOLO tìm thấy"
            note={`Cùng một vùng biển (do YOLO định vị), so lớp YOLO dự đoán với lớp HOG + màu + SVM dự đoán — tách riêng khâu phân loại khỏi khâu định vị, giống thí nghiệm E8. HOG + SVM mất ${res.classic_ms_per_box} ms / biển.`}
          >
            {res.per_box.length ? (
              <>
                <p>
                  Đồng ý <b>{agree}</b>/{res.per_box.length} biển ({pct(agree / res.per_box.length, 0)}).
                </p>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th className="num">#</th>
                        <th className="num">Cạnh (px)</th>
                        <th>YOLO11</th>
                        <th>HOG + màu + SVM</th>
                        <th>Khớp</th>
                      </tr>
                    </thead>
                    <tbody>
                      {res.per_box.map((r, i) => (
                        <tr key={i}>
                          <td className="num">{i + 1}</td>
                          <td className="num">
                            {r.side_px.toFixed(0)}
                            {r.side_px < 16 && <span className="warn"> · nhỏ</span>}
                          </td>
                          <td>
                            {r.yolo_class_name} <span className="muted num">{(r.yolo_score * 100).toFixed(0)}%</span>
                          </td>
                          <td>
                            {r.classic_class_name ?? <span className="muted">nền</span>} <span className="muted num">{((r.classic_score ?? 0) * 100).toFixed(0)}%</span>
                          </td>
                          <td className={r.agree ? "good" : "bad"}>{r.agree ? "✓ khớp" : "✗ khác"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            ) : (
              <p className="muted">YOLO không tìm thấy biển nào.</p>
            )}
          </Card>
        </>
      )}
    </>
  );
}

/** So sánh CV truyền thống và học sâu: demo trực tiếp + kết quả thí nghiệm E8 (phân loại), T4 (điều kiện xấu), SIFT. */
export default function ComparePage() {
  const { data } = useStatic<Results>("results");
  const { colors } = useTheme();
  const axis = { stroke: colors.axis, tick: { fill: colors.text, fontSize: 12 } };
  const mColor = Object.fromEntries(METHODS.map((m, i) => [m, colors.series[i]]));

  const e8 = SIZES.map((s) => ({ size: s, ...Object.fromEntries((data?.e8 ?? []).filter((r) => r.kich_thuoc === s).map((r) => [r.phuong_phap, r.accuracy])) }));
  const e8n = Object.fromEntries((data?.e8 ?? []).filter((r) => r.phuong_phap === METHODS[0]).map((r) => [r.kich_thuoc, r.n]));
  const paired = (data?.e8_paired ?? []).map((r) => ({ ...r, err: [r.delta_acc - r.ci95_low, r.ci95_high - r.delta_acc] }));
  const t4conds = [...new Set((data?.t4 ?? []).map((r) => r.dieu_kien))];
  const t4 = t4conds.map((c) => ({ cond: COND_VI[c] ?? c, ...Object.fromEntries((data?.t4 ?? []).filter((r) => r.dieu_kien === c).map((r) => [r.che_do, r.R])) }));
  const get = (m: string, s = "tất cả") => data?.e8.find((r) => r.phuong_phap === m && r.kich_thuoc === s);

  return (
    <>
      <PageHead
        title="So sánh CV truyền thống ↔ học sâu"
        desc="Hai cách tiếp cận cùng một bài toán: đặc trưng thủ công (màu, hình dạng, HOG, SIFT) + SVM so với YOLO11s học đặc trưng end-to-end. So sánh trực tiếp trên ảnh và bằng số liệu thí nghiệm trên 2 017 biển của tập test."
      />
      <LiveCompare />

      {data && (
        <>
          <h2 style={{ marginTop: 28 }}>Kết quả thí nghiệm</h2>
          <div className="grid kpis">
            <Kpi label="YOLO11 — accuracy phân loại" value={pct(get(METHODS[0])?.accuracy)} sub={`CI95 ${get(METHODS[0])?.ci95}`} />
            <Kpi label="HOG + màu + SVM" value={pct(get(METHODS[1])?.accuracy)} sub={`CI95 ${get(METHODS[1])?.ci95}`} />
            <Kpi label="SIFT-BoVW + SVM" value={pct(get(METHODS[3])?.accuracy)} sub={`CI95 ${get(METHODS[3])?.ci95}`} />
            <Kpi label="Biển < 16 px: HOG + màu vs YOLO" value={`${pct(get(METHODS[1], "<16px")?.accuracy_tren_bien_yolo_tim_thay, 0)} / ${pct(get(METHODS[0], "<16px")?.accuracy_tren_bien_yolo_tim_thay, 0)}`} sub="trên biển YOLO tìm thấy — chênh lệch không có ý nghĩa thống kê" />
          </div>

          <Card
            title="E8 — Accuracy phân loại theo kích thước biển"
            note="Cùng crop biển thật (GT) của tập test cho mọi phương pháp. Bộ phân loại truyền thống tốt nhất (HOG + màu + SVM) kém YOLO khoảng 1,4 điểm tổng thể; SIFT kém hẳn vì biển nhỏ có quá ít điểm đặc trưng."
          >
            <Legend items={METHODS.map((m) => ({ label: m, color: mColor[m] }))} />
            <div className="chart">
              <ResponsiveContainer>
                <BarChart data={e8} margin={{ right: 12 }} barGap={2}>
                  <CartesianGrid vertical={false} />
                  <XAxis dataKey="size" {...axis} tickFormatter={(s) => `${s} (n=${e8n[s] ?? "?"})`} />
                  <YAxis {...axis} domain={[0.4, 1]} tickFormatter={pctTick} />
                  <Tooltip cursor={{ fill: colors.grid }} content={<Tip format={(v) => pct(Number(v))} />} />
                  {METHODS.map((m) => (
                    <Bar key={m} dataKey={m} name={m} fill={mColor[m]} radius={[4, 4, 0, 0]} />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <div className="grid g2">
            <Card title="Chênh lệch ghép cặp: HOG + màu − YOLO" note="Bootstrap ghép cặp trên cùng biển (YOLO tìm thấy), thanh = CI95. Khoảng tin cậy chứa 0 ở biển < 16 px: hai phương pháp ngang nhau; với biển lớn YOLO vượt trội.">
              <div className="chart">
                <ResponsiveContainer>
                  <BarChart data={paired} margin={{ right: 12 }}>
                    <CartesianGrid vertical={false} />
                    <XAxis dataKey="kich_thuoc" {...axis} />
                    <YAxis {...axis} domain={[-0.15, 0.1]} ticks={[-0.15, -0.1, -0.05, 0, 0.05, 0.1]} tickFormatter={(v) => `${v > 0 ? "+" : ""}${Math.round(v * 100)} đ%`} width={52} />
                    <ReferenceLine y={0} stroke={colors.text} />
                    <Tooltip cursor={{ fill: colors.grid }} content={<Tip format={(v) => (Array.isArray(v) ? "" : `${(Number(v) * 100).toFixed(1)} điểm %`)} title={(l, p) => `${l} · n=${p?.n} · CI95 ${(Number(p?.ci95_low) * 100).toFixed(1)} … ${(Number(p?.ci95_high) * 100).toFixed(1)}`} />} />
                    <Bar dataKey="delta_acc" name="Δ accuracy" fill={colors.series[1]} radius={[4, 4, 4, 4]} barSize={28}>
                      <ErrorBar dataKey="err" width={8} stroke={colors.text} strokeWidth={1.5} />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>
            <Card title="Vì sao SIFT kém: số điểm SIFT trung vị trên một biển" note="Đo trên 2 017 crop test. 93% biển < 16 px có dưới 5 điểm SIFT — không đủ để tạo túi từ thị giác (BoVW).">
              <div className="chart">
                <ResponsiveContainer>
                  <BarChart data={data.sift_keypoints} margin={{ right: 12 }}>
                    <CartesianGrid vertical={false} />
                    <XAxis dataKey="size" {...axis} />
                    <YAxis {...axis} />
                    <Tooltip cursor={{ fill: colors.grid }} content={<Tip format={(v) => `${v}`} title={(l, p) => `${l} · ${p?.pct_lt5}% biển có < 5 điểm`} />} />
                    <Bar dataKey="median" name="Số điểm trung vị" fill={colors.series[3]} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </div>

          <Card title="T4 — Recall của hệ thống khi ảnh xấu đi" note="Tăng cường thích nghi (CV truyền thống) giúp mô hình học sâu: ảnh rất tối recall 0,686 → 0,822 mà không cần huấn luyện lại. Luôn bật gamma + CLAHE thì hại ảnh nhiễu — vì vậy chỉ tăng cường khi bộ đánh giá chất lượng thấy cần.">
            <Legend items={MODES.map((m, i) => ({ label: m, color: colors.series[i] }))} />
            <div className="chart">
              <ResponsiveContainer>
                <BarChart data={t4} margin={{ right: 12 }} barGap={2}>
                  <CartesianGrid vertical={false} />
                  <XAxis dataKey="cond" {...axis} />
                  <YAxis {...axis} domain={[0.5, 1]} tickFormatter={pctTick} />
                  <Tooltip cursor={{ fill: colors.grid }} content={<Tip format={(v) => pct(Number(v))} />} />
                  {MODES.map((m, i) => (
                    <Bar key={m} dataKey={m} name={m} fill={colors.series[i]} radius={[4, 4, 0, 0]} />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card title="Tổng hợp định tính">
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Tiêu chí</th>
                    <th>
                      <span className="pill pill-cv">CV</span> Màu + hình dạng + HOG + SVM
                    </th>
                    <th>
                      <span className="pill pill-dl">DL</span> YOLO11s
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {QUALI.map(([k, a, b]) => (
                    <tr key={k}>
                      <td>
                        <b>{k}</b>
                      </td>
                      <td>{a}</td>
                      <td>{b}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="callout good">
              Kết luận: học sâu tốt hơn ở khâu <b>định vị</b> (tìm biển trong cảnh phức tạp) và biển lớn; đặc trưng thủ công vẫn cạnh tranh ở <b>phân loại</b> biển nhỏ và rất hữu ích ở <b>tiền xử lý</b>{" "}
              (tăng cường thích nghi) và <b>hậu xử lý</b> (cắt vùng số cho OCR, theo vết Kalman). Hệ thống cuối kết hợp cả hai.
            </p>
          </Card>
        </>
      )}
    </>
  );
}

const QUALI: [string, string, string][] = [
  ["Định vị biển", "Dựa vào màu + hình dạng: nhạy với biển dính nhau, biển nhiều màu, nền đỏ / xanh (mái tôn, biển quảng cáo)", "Học từ dữ liệu, ổn định trong cảnh phức tạp"],
  ["Phân loại (cho đúng vùng)", "HOG + màu: 91,0% — ngang YOLO trên biển < 16 px", "92,4% — vượt trội ở biển ≥ 16 px"],
  ["Dữ liệu huấn luyện", "Ít, huấn luyện vài phút trên CPU", "Cần GPU, ~2,9 giờ trên T4 (80 epoch)"],
  ["Tốc độ", "≈ 40 ms phân đoạn + vài ms / vùng trên CPU", "≈ 22 ms / ảnh 1280 trên GPU; ~1 s trên CPU Docker"],
  ["Giải thích được", "Cao: thấy mask màu, contour, ảnh HOG", "Thấp: cần công cụ riêng (Grad-CAM…)"],
  ["Ảnh tối / nhiễu", "Ngưỡng HSV lệch khi ánh sáng đổi", "Giảm recall, khắc phục bằng tăng cường thích nghi (T4)"],
];
