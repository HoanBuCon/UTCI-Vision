import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { ClassInfo } from "../api/types";

/**
 * Thư viện biển báo (FR-WEB-04). Phụ trách: TV2 — S3 (nội dung ý nghĩa: TV4).
 * Đã chạy được với /api/v1/classes. TODO: nhóm theo siêu lớp, ảnh minh hoạ, tìm kiếm.
 */
export default function LibraryPage() {
  const [classes, setClasses] = useState<ClassInfo[]>([]);
  useEffect(() => {
    api.classes().then(setClasses).catch(() => setClasses([]));
  }, []);

  return (
    <section>
      <h1>Thư viện biển báo ({classes.length})</h1>
      <ul className="library">
        {classes.map((c) => (
          <li key={c.id}>
            <strong>{c.name_vi}</strong> <span className={`tag tag-${c.superclass}`}>{c.superclass_vi}</span>
            {c.meaning && <p>{c.meaning}</p>}
          </li>
        ))}
      </ul>
    </section>
  );
}
