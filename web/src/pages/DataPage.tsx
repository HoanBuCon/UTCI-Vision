import { useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Eda } from "../api/staticTypes";
import { SUPERCLASS_COLOR } from "../api/useClasses";
import { Legend, Tip } from "../components/charts";
import { Card, int, Kpi, PageHead, Seg, SortTable, useStatic, type Column } from "../components/ui";
import { useTheme } from "../theme";

const SUPER_VI: Record<string, string> = { prohibitory: "Cấm", warning: "Nguy hiểm", mandatory: "Hiệu lệnh", info: "Chỉ dẫn", other: "Khác" };

function Heatmap({ grid }: { grid: number[][] }) {
  const { colors } = useTheme();
  const max = Math.max(...grid.flat());
  const step = (v: number) => colors.seq[Math.min(colors.seq.length - 1, Math.floor((Math.sqrt(v / max) || 0) * colors.seq.length))];
  return (
    <>
      <div className="heat" role="img" aria-label="Mật độ vị trí tâm biển báo trong khung hình">
        {grid.flatMap((row, y) => row.map((v, x) => <div key={`${y}-${x}`} title={`${v} biển (hàng ${y + 1}, cột ${x + 1})`} style={{ background: v ? step(v) : "var(--surface-2)" }} />))}
      </div>
      <div className="heat-legend">
        ít <i /> nhiều (thang căn bậc hai, tối đa {max} biển / ô)
      </div>
    </>
  );
}

/** Trang Mô tả dữ liệu (EDA) — số liệu từ processed/v1 (đã khoá, C-08). */
export default function DataPage() {
  const { data, error } = useStatic<Eda>("eda");
  const { colors } = useTheme();
  const [order, setOrder] = useState<"total" | "pct_lt16" | "median_px">("total");
  const classes = useMemo(() => [...(data?.per_class ?? [])].sort((a, b) => b[order] - a[order]), [data, order]);

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p className="muted">Đang tải số liệu…</p>;
  const t = data.totals;
  const splitColors = { train: colors.series[0], val: colors.series[1], test: colors.series[2] };
  const axis = { stroke: colors.axis, tick: { fill: colors.text, fontSize: 12 } };

  const columns: Column<Eda["per_class"][number]>[] = [
    { key: "id", label: "#", num: true },
    { key: "name", label: "Lớp" },
    { key: "superclass", label: "Nhóm", render: (r) => <span className={`tag-${r.superclass}`}>{SUPER_VI[r.superclass]}</span> },
    { key: "qcvn", label: "QCVN" },
    { key: "train", label: "Train", num: true },
    { key: "val", label: "Val", num: true },
    { key: "test", label: "Test", num: true },
    { key: "total", label: "Tổng", num: true },
    { key: "clusters", label: "Cụm ảnh gần trùng", num: true },
    { key: "median_px", label: "Cạnh trung vị (px)", num: true, render: (r) => r.median_px.toFixed(0) },
    { key: "pct_lt16", label: "% < 16 px", num: true, render: (r) => `${r.pct_lt16.toFixed(1)}%` },
  ];

  return (
    <>
      <PageHead
        title="Mô tả dữ liệu (EDA)"
        desc={
          <>
            Bộ dữ liệu biển báo giao thông Việt Nam (Roboflow, CC BY 4.0) sau khi gộp nhãn và chia lại theo cụm ảnh gần trùng — phiên bản <code>processed/v1</code>{" "}
            được khoá cho mọi thí nghiệm (C-08). Ảnh không được commit vào git (C-06).
          </>
        }
      />
      <div className="toc">
        {["tong-quan", "lop", "kich-thuoc", "vi-tri", "chat-luong"].map((id, i) => (
          <a key={id} href={`#${id}`}>
            {["Tổng quan", "Phân bố lớp", "Kích thước biển", "Vị trí & độ phân giải", "Kiểm tra chất lượng"][i]}
          </a>
        ))}
      </div>

      <section id="tong-quan" className="grid kpis">
        <Kpi label="Ảnh" value={int(t.images)} sub={`${t.background_images} ảnh nền (không có biển) · loại ${t.excluded_images} ảnh lỗi`} />
        <Kpi label="Biển báo (box)" value={int(t.boxes)} sub={`trung bình ${(t.boxes / t.images).toFixed(1)} biển / ảnh`} />
        <Kpi label="Số lớp" value={t.classes} sub={`gộp từ ${t.raw_classes} lớp gốc`} />
        <Kpi label="Cạnh biển trung vị" value={`${t.median_side_px.toFixed(0)} px`} sub={`${t.pct_lt16.toFixed(1)}% < 16 px · ${t.pct_lt32.toFixed(1)}% < 32 px`} />
        <Kpi label="Mất cân bằng lớp" value={`${t.imbalance.toFixed(1)}×`} sub="lớp nhiều nhất / lớp ít nhất" />
        <Kpi label="Cụm ảnh gần trùng" value={int(t.clusters)} sub="chia train/val/test theo cụm (pHash) để tránh rò rỉ" />
      </section>

      <div className="grid g2">
        <Card title="Chia tập" note="Chia 70/15/15 theo cụm ảnh gần trùng — ảnh cùng cảnh (khung hình liên tiếp) luôn nằm cùng một tập.">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Tập</th>
                  <th className="num">Ảnh</th>
                  <th className="num">Biển</th>
                  <th className="num">% ảnh</th>
                </tr>
              </thead>
              <tbody>
                {(["train", "val", "test"] as const).map((s) => (
                  <tr key={s}>
                    <td>
                      <i style={{ display: "inline-block", width: 10, height: 10, borderRadius: 3, background: splitColors[s], marginRight: 8 }} />
                      {s}
                    </td>
                    <td className="num">{int(data.splits[s].images)}</td>
                    <td className="num">{int(data.splits[s].boxes)}</td>
                    <td className="num">{((data.splits[s].images / t.images) * 100).toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
        <Card title="Theo nhóm biển (siêu lớp)" note="Biển cấm chiếm hơn một nửa số box — nguồn chính của mất cân bằng.">
          <div className="chart short">
            <ResponsiveContainer>
              <BarChart data={data.superclasses} layout="vertical" margin={{ left: 8, right: 24 }}>
                <CartesianGrid horizontal={false} />
                <XAxis type="number" {...axis} />
                <YAxis type="category" dataKey="name" width={110} {...axis} />
                <Tooltip cursor={{ fill: colors.grid }} content={<Tip format={(v) => `${v} biển`} />} />
                <Bar dataKey="boxes" name="Số biển" fill={colors.series[0]} radius={[0, 4, 4, 0]} barSize={18} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <Card
        id="lop"
        title="Phân bố 27 lớp"
        extra={
          <Seg
            value={order}
            onChange={setOrder}
            options={[
              { value: "total", label: "Số biển" },
              { value: "pct_lt16", label: "% biển nhỏ" },
              { value: "median_px", label: "Kích thước" },
            ]}
          />
        }
        note={`Lớp "${data.merged.into}" gộp ${data.merged.raw_ids.length} lớp gốc quá ít mẫu: ${data.merged.raw_names.join(", ") || data.merged.raw_ids.join(", ")}.`}
      >
        <Legend items={[{ label: "train", color: splitColors.train }, { label: "val", color: splitColors.val }, { label: "test", color: splitColors.test }]} />
        <div className="chart tall">
          <ResponsiveContainer>
            <BarChart data={classes} layout="vertical" margin={{ left: 8, right: 24 }} barCategoryGap={3}>
              <CartesianGrid horizontal={false} />
              <XAxis type="number" {...axis} />
              <YAxis type="category" dataKey="name" width={190} interval={0} {...axis} tick={{ fill: colors.text, fontSize: 11 }} />
              <Tooltip
                cursor={{ fill: colors.grid }}
                content={<Tip format={(v) => `${v}`} title={(l, p) => `${l} · ${p?.qcvn} · cạnh trung vị ${Number(p?.median_px).toFixed(0)} px · ${Number(p?.pct_lt16).toFixed(0)}% < 16 px`} />}
              />
              <Bar dataKey="train" stackId="s" name="train" fill={splitColors.train} stroke={colors.surface} strokeWidth={1} />
              <Bar dataKey="val" stackId="s" name="val" fill={splitColors.val} stroke={colors.surface} strokeWidth={1} />
              <Bar dataKey="test" stackId="s" name="test" fill={splitColors.test} stroke={colors.surface} strokeWidth={1} radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
      <Card title="Bảng chi tiết theo lớp">
        <SortTable rows={data.per_class} columns={columns} initial={{ key: "total", desc: true }} />
      </Card>

      <div className="grid g2" id="kich-thuoc">
        <Card title="Phân bố kích thước biển (cạnh √(w·h), px)" note="Hơn một nửa số biển nhỏ hơn 32 px — lý do chọn suy luận ở 1280 px (T3) và là điểm yếu chung của cả hai phương pháp.">
          <div className="chart">
            <ResponsiveContainer>
              <BarChart data={data.size_hist} margin={{ right: 12 }}>
                <CartesianGrid vertical={false} />
                <XAxis dataKey="bin" {...axis} />
                <YAxis {...axis} />
                <Tooltip cursor={{ fill: colors.grid }} content={<Tip format={(v) => `${v} biển`} title={(l) => `${l} px`} />} />
                <ReferenceLine x="16–24" stroke={colors.series[7]} strokeDasharray="4 3" label={{ value: "16 px", fill: colors.text, fontSize: 11, position: "insideTopLeft" }} />
                <Bar dataKey="boxes" name="Số biển" fill={colors.series[0]} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card title="Số biển trên mỗi ảnh" note="Cột 10 gộp các ảnh có ≥ 10 biển.">
          <div className="chart">
            <ResponsiveContainer>
              <BarChart data={data.signs_per_image} margin={{ right: 12 }}>
                <CartesianGrid vertical={false} />
                <XAxis dataKey="n" {...axis} tickFormatter={(v) => (v === 10 ? "≥10" : String(v))} />
                <YAxis {...axis} />
                <Tooltip cursor={{ fill: colors.grid }} content={<Tip format={(v) => `${v} ảnh`} title={(l) => `${l} biển / ảnh`} />} />
                <Bar dataKey="images" name="Số ảnh" fill={colors.series[0]} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <div className="grid g2" id="vi-tri">
        <Card title="Vị trí tâm biển trong khung hình" note="Biển tập trung ở nửa trên và hai bên lề đường — phù hợp camera hành trình.">
          <Heatmap grid={data.position_heatmap} />
        </Card>
        <Card title="Độ phân giải ảnh" note="Ảnh nhiều độ phân giải khác nhau; YOLO đưa về cạnh dài 960 (huấn luyện) / 1280 (suy luận).">
          <div className="chart short">
            <ResponsiveContainer>
              <BarChart data={data.resolutions} layout="vertical" margin={{ left: 8, right: 24 }}>
                <CartesianGrid horizontal={false} />
                <XAxis type="number" {...axis} />
                <YAxis type="category" dataKey="res" width={90} {...axis} />
                <Tooltip cursor={{ fill: colors.grid }} content={<Tip format={(v) => `${v} ảnh`} />} />
                <Bar dataKey="images" name="Số ảnh" fill={colors.series[0]} radius={[0, 4, 4, 0]} barSize={18} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <Card id="chat-luong" title="Kiểm tra chất lượng dữ liệu" note="Kết quả scripts/audit (reports/data/issues.json). Dataset được khoá: không bổ sung ảnh và không gán lại nhãn — các vấn đề được xử lý ở bước tiền xử lý / đánh giá.">
        <div className="grid g4">
          {Object.entries(data.audit).map(([k, v]) => (
            <div key={k} className="kpi">
              <span className="label">{AUDIT_VI[k] ?? k}</span>
              <span className="value" style={{ fontSize: "1.3rem" }}>
                {v}
              </span>
            </div>
          ))}
        </div>
        <div className="callout" style={{ marginTop: 12 }}>
          Màu nhóm biển dùng trong toàn bộ ứng dụng:{" "}
          {Object.entries(SUPER_VI).map(([k, v]) => (
            <span key={k} style={{ marginRight: 12 }}>
              <i style={{ display: "inline-block", width: 10, height: 10, borderRadius: 3, background: SUPERCLASS_COLOR[k], marginRight: 4 }} />
              {v}
            </span>
          ))}
        </div>
      </Card>
    </>
  );
}

const AUDIT_VI: Record<string, string> = {
  corrupt_images: "Ảnh hỏng",
  missing_labels: "Thiếu file nhãn",
  bad_lines: "Dòng nhãn sai định dạng",
  invalid_boxes: "Box không hợp lệ",
  empty_labels: "Ảnh không có nhãn",
  duplicates: "Ảnh trùng",
};
