import { useState } from "react";
import { Bar, BarChart, CartesianGrid, ErrorBar, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Results } from "../api/staticTypes";
import { Legend, pctTick, Tip } from "../components/charts";
import { Card, fmt, Kpi, PageHead, pct, Seg, SortTable, useStatic, type Column } from "../components/ui";
import { useTheme } from "../theme";

const SIZE_KEYS = ["recall_<16px", "recall_16-32", "recall_32-64", "recall_>=64"];
const SIM_VI: Record<string, string> = { "giong_train(<=10)": "Giống train (pHash ≤ 10)", "trung_binh(11-14)": "Trung bình (11–14)", "khac_train(>=15)": "Khác train (≥ 15)" };
const CFG_VI: Record<string, string> = { yolo_only: "Chỉ YOLO", "+enhance": "+ tăng cường", "+verifier": "+ xác minh", full: "Đầy đủ", mac_dinh: "Mặc định (1280 + tăng cường)" };

type Row = Record<string, number | string | null>;

function ConfigTable({ rows }: { rows: Row[] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Cấu hình</th>
            <th className="num">P</th>
            <th className="num">R</th>
            <th className="num">F1</th>
            <th className="num">R &lt;16px</th>
            <th className="num">R 16–32</th>
            <th className="num">R 32–64</th>
            <th className="num">R ≥64</th>
            <th className="num">ms</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={String(r.cau_hinh)}>
              <td>{CFG_VI[String(r.cau_hinh)] ?? r.cau_hinh}</td>
              {["precision", "recall", "f1", ...SIZE_KEYS].map((k) => (
                <td key={k} className="num">
                  {fmt(r[k] as number)}
                </td>
              ))}
              <td className="num">{fmt((r.ms_tb ?? r.ms_anh) as number, 1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** Kết quả thực nghiệm: huấn luyện, khoảng tin cậy, theo lớp, ablation, biển nhỏ, nhóm tương đồng, sổ đăng ký. */
export default function ResultsPage() {
  const { data, error } = useStatic<Results>("results");
  const { colors } = useTheme();
  const [curve, setCurve] = useState<"metrics" | "loss">("metrics");
  if (error) return <p className="error">{error}</p>;
  if (!data) return <p className="muted">Đang tải số liệu…</p>;
  const axis = { stroke: colors.axis, tick: { fill: colors.text, fontSize: 12 } };
  const m = data.model;
  const e1 = data.e1[0];
  const boot = data.bootstrap.map((b) => ({ ...b, err: [b.value - b.ci95_low, b.ci95_high - b.value] }));
  const t3 = SIZE_KEYS.map((k) => ({ size: k.replace("recall_", ""), ...Object.fromEntries(data.t3.map((r) => [String(r.cau_hinh), r[k]])) }));
  const t3names = data.t3.map((r) => String(r.cau_hinh));
  const ap = Object.fromEntries(data.per_class_ap.map((r) => [r.id, r]));
  const perClass = data.per_class.map((r) => ({ ...r, ap50: ap[r.id]?.test_AP50 ?? null, ap: ap[r.id]?.test_AP ?? null }));
  const series = curve === "metrics"
    ? [{ key: "map50", label: "mAP50" }, { key: "map50_95", label: "mAP50-95" }, { key: "precision", label: "Precision" }, { key: "recall", label: "Recall" }]
    : [{ key: "train_box", label: "box loss (train)" }, { key: "val_box", label: "box loss (val)" }, { key: "train_cls", label: "cls loss (train)" }, { key: "val_cls", label: "cls loss (val)" }];

  const cols: Column<(typeof perClass)[number]>[] = [
    { key: "id", label: "#", num: true },
    { key: "ten", label: "Lớp" },
    { key: "n", label: "Số biển test", num: true },
    { key: "precision", label: "P", num: true, render: (r) => fmt(r.precision) },
    { key: "recall", label: "R", num: true, render: (r) => fmt(r.recall) },
    { key: "recall_ci95", label: "CI95 R (Wilson)", render: (r) => r.recall_ci95 },
    { key: "recall_ge16px", label: "R biển ≥16px", num: true, render: (r) => fmt(r.recall_ge16px) },
    { key: "ti_le_bien_nho", label: "% biển nhỏ", num: true, render: (r) => pct(r.ti_le_bien_nho, 0) },
    { key: "ap50", label: "AP50", num: true, render: (r) => fmt(r.ap50) },
    { key: "ap", label: "AP50-95", num: true, render: (r) => fmt(r.ap) },
  ];

  return (
    <>
      <PageHead title="Kết quả thực nghiệm" desc={`Mô hình ${m.run_id} (${m.author}, ${m.environment?.gpu}, ${(m.duration_s / 3600).toFixed(1)} giờ). Mọi số đo trên tập test processed/v1 (826 ảnh, 2 017 biển) tại ngưỡng vận hành conf 0,25; khoảng tin cậy 95% bằng bootstrap theo ảnh.`} />
      <div className="toc">
        {[
          ["huan-luyen", "Huấn luyện"],
          ["he-thong", "Hệ thống (E1, E2)"],
          ["bien-nho", "Biển nhỏ (T3)"],
          ["theo-lop", "Theo lớp"],
          ["tuong-dong", "Độ tương đồng"],
          ["so-dang-ky", "Sổ đăng ký thí nghiệm"],
        ].map(([id, l]) => (
          <a key={id} href={`#${id}`}>
            {l}
          </a>
        ))}
      </div>
      <div className="grid kpis">
        {data.bootstrap.map((b) => (
          <Kpi key={b.metric} label={`${b.metric} (YOLO)`} value={b.value.toFixed(3)} sub={`CI95 ${b.ci95_low.toFixed(3)} – ${b.ci95_high.toFixed(3)}`} />
        ))}
        {e1 && <Kpi label="Hệ thống mặc định — F1" value={fmt(e1.f1 as number)} sub={`P ${fmt(e1.precision as number)} · R ${fmt(e1.recall as number)} · R<16px ${fmt(e1["recall_<16px"] as number)}`} />}
      </div>

      <Card
        id="huan-luyen"
        title="Đường cong huấn luyện (80 epoch, imgsz 960)"
        extra={<Seg value={curve} onChange={setCurve} options={[{ value: "metrics", label: "Chỉ số val" }, { value: "loss", label: "Hàm mất mát" }]} />}
        note="Fine-tune YOLO11s (COCO) trên Colab Tesla T4; chọn checkpoint tốt nhất theo fitness trên val."
      >
        <Legend items={series.map((s, i) => ({ label: s.label, color: colors.series[i] }))} />
        <div className="chart">
          <ResponsiveContainer>
            <LineChart data={data.training} margin={{ right: 12 }}>
              <CartesianGrid vertical={false} />
              <XAxis dataKey="epoch" {...axis} />
              <YAxis {...axis} domain={curve === "metrics" ? [0, 1] : ["auto", "auto"]} />
              <Tooltip content={<Tip title={(l) => `Epoch ${l}`} />} />
              {series.map((s, i) => (
                <Line key={s.key} dataKey={s.key} name={s.label} stroke={colors.series[i]} strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <div className="grid g2" id="he-thong">
        <Card title="Chỉ số YOLO trên test + CI95" note="Thanh lỗi = khoảng tin cậy 95% (bootstrap theo ảnh).">
          <div className="chart short">
            <ResponsiveContainer>
              <BarChart data={boot} margin={{ right: 12 }}>
                <CartesianGrid vertical={false} />
                <XAxis dataKey="metric" {...axis} />
                <YAxis {...axis} domain={[0, 1]} />
                <Tooltip cursor={{ fill: colors.grid }} content={<Tip format={(v) => (Array.isArray(v) ? "" : Number(v).toFixed(3))} title={(l, p) => `${l} · CI95 ${Number(p?.ci95_low).toFixed(3)} – ${Number(p?.ci95_high).toFixed(3)}`} />} />
                <Bar dataKey="value" name="Giá trị" fill={colors.series[0]} radius={[4, 4, 0, 0]} barSize={36}>
                  <ErrorBar dataKey="err" width={8} stroke={colors.text} strokeWidth={1.5} />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card title="E2 — Ablation từng khâu (960 px)" note="Bộ xác minh tăng precision 0,861 → 0,946 nhưng recall biển nhỏ giảm mạnh → tắt mặc định. Tăng cường không đổi kết quả ảnh thường (chỉ kích hoạt với ảnh tối).">
          <ConfigTable rows={data.e2} />
          {e1 && (
            <>
              <h3 style={{ marginTop: 14 }}>E1 — Cấu hình mặc định cuối cùng</h3>
              <ConfigTable rows={data.e1} />
            </>
          )}
        </Card>
      </div>

      <Card id="bien-nho" title="T3 — Recall theo kích thước biển với các cách suy luận" note="1280 px nâng recall biển < 16 px từ 0,634 lên 0,737 với precision không đổi (+3 ms). Cắt ô cho recall cao nhất nhưng precision chỉ 0,749 và chậm gấp 2,5 lần → chọn 1280 làm mặc định.">
        <Legend items={t3names.map((n, i) => ({ label: n, color: colors.series[i] }))} />
        <div className="chart">
          <ResponsiveContainer>
            <BarChart data={t3} margin={{ right: 12 }} barGap={2}>
              <CartesianGrid vertical={false} />
              <XAxis dataKey="size" {...axis} />
              <YAxis {...axis} domain={[0.5, 1]} tickFormatter={pctTick} />
              <Tooltip cursor={{ fill: colors.grid }} content={<Tip format={(v) => pct(Number(v))} title={(l) => `Biển ${l}`} />} />
              {t3names.map((n, i) => (
                <Bar key={n} dataKey={n} name={n} fill={colors.series[i]} radius={[4, 4, 0, 0]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
        <ConfigTable rows={data.t3} />
      </Card>

      <Card id="theo-lop" title="Theo lớp (test)" note="Bấm tiêu đề cột để sắp xếp. Các lớp yếu nhất chủ yếu do tỉ lệ biển nhỏ cao — recall trên biển ≥ 16 px cao hơn rõ.">
        <SortTable rows={perClass} columns={cols} initial={{ key: "recall", desc: false }} highlight={(r) => r.recall < 0.8} />
      </Card>

      <Card id="tuong-dong" title="Theo độ tương đồng với tập train (khoảng cách pHash)" note="Ảnh test càng khác train, recall càng giảm (0,978 → 0,805) — ước lượng thực tế hơn cho ảnh mới ngoài dataset.">
        <Legend items={[{ label: "Recall", color: colors.series[0] }, { label: "Recall biển ≥ 16 px", color: colors.series[1] }, { label: "Precision", color: colors.series[2] }]} />
        <div className="chart short">
          <ResponsiveContainer>
            <BarChart data={data.similarity.map((s) => ({ ...s, name: SIM_VI[s.group] ?? s.group }))} margin={{ right: 12 }} barGap={2}>
              <CartesianGrid vertical={false} />
              <XAxis dataKey="name" {...axis} />
              <YAxis {...axis} domain={[0.6, 1]} tickFormatter={pctTick} />
              <Tooltip cursor={{ fill: colors.grid }} content={<Tip format={(v) => pct(Number(v))} title={(l, p) => `${l} · ${p?.anh} ảnh, ${p?.bien} biển`} />} />
              <Bar dataKey="recall" name="Recall" fill={colors.series[0]} radius={[4, 4, 0, 0]} />
              <Bar dataKey="recall_ge16px" name="Recall ≥16px" fill={colors.series[1]} radius={[4, 4, 0, 0]} />
              <Bar dataKey="precision" name="Precision" fill={colors.series[2]} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card id="so-dang-ky" title="Sổ đăng ký thí nghiệm (experiments/registry.csv)">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Mã</th>
                <th>Ngày</th>
                <th>Người chạy</th>
                <th>Nền tảng</th>
                <th>GPU</th>
                <th>Ghi chú</th>
              </tr>
            </thead>
            <tbody>
              {data.registry.map((r) => (
                <tr key={r.run_id}>
                  <td>
                    <code>{r.exp}</code>
                  </td>
                  <td>{r.date}</td>
                  <td>{r.author}</td>
                  <td>{r.platform}</td>
                  <td>{r.gpu}</td>
                  <td className="small">{r.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </>
  );
}
