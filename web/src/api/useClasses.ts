import { useEffect, useState } from "react";
import { api } from "./client";
import type { ClassInfo } from "./types";

let cache: Promise<ClassInfo[]> | null = null;

/** Danh sách 27 lớp (tên, siêu lớp, QCVN, ý nghĩa) — tải một lần, dùng chung giữa các trang. */
export function useClasses(): Record<number, ClassInfo> {
  const [byId, setById] = useState<Record<number, ClassInfo>>({});
  useEffect(() => {
    cache ??= api.classes().catch(() => {
      cache = null;
      return [];
    });
    cache.then((list) => setById(Object.fromEntries(list.map((c) => [c.id, c]))));
  }, []);
  return byId;
}

export const SUPERCLASS_COLOR: Record<string, string> = {
  prohibitory: "#dc2828",
  warning: "#f5b800",
  mandatory: "#0a64d8",
  info: "#0a8fc8",
  other: "#777777",
};
