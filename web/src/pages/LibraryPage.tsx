import { useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import type { ClassInfo } from "../api/types";

const ORDER = ["prohibitory", "warning", "mandatory", "info", "other"];

/** Thư viện biển báo (FR-WEB-04): 27 lớp nhóm theo siêu lớp, tìm kiếm theo tên / mã QCVN. */
export default function LibraryPage() {
  const [classes, setClasses] = useState<ClassInfo[]>([]);
  const [query, setQuery] = useState("");
  useEffect(() => {
    api.classes().then(setClasses).catch(() => setClasses([]));
  }, []);

  const groups = useMemo(() => {
    const q = query.trim().toLowerCase();
    const hit = classes.filter((c) => !q || `${c.name_vi} ${c.qcvn} ${c.meaning}`.toLowerCase().includes(q));
    return ORDER.map((s) => ({ key: s, label: hit.find((c) => c.superclass === s)?.superclass_vi, items: hit.filter((c) => c.superclass === s) })).filter(
      (g) => g.items.length,
    );
  }, [classes, query]);

  return (
    <section>
      <h1>Thư viện biển báo ({classes.length} lớp)</h1>
      <input className="search" placeholder="Tìm theo tên hoặc mã QCVN…" value={query} onChange={(e) => setQuery(e.target.value)} />
      {groups.map((g) => (
        <div key={g.key}>
          <h2 className={`tag-${g.key}`}>
            {g.label} ({g.items.length})
          </h2>
          <ul className="library">
            {g.items.map((c) => (
              <li key={c.id}>
                <strong>{c.name_vi}</strong>
                {c.qcvn && <span className="muted small"> · {c.qcvn}</span>}
                {c.meaning ? <p className="small">{c.meaning}</p> : null}
                <p className="small muted">
                  {[c.has_value && `đọc giá trị (${c.value_unit})`, c.has_text && "có chữ"].filter(Boolean).join(" · ")}
                </p>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </section>
  );
}
