import { useEffect, useState } from "react";
import { api } from "./client";
import type { HealthResponse } from "./types";

type State = { health: HealthResponse | null; error: string | null };

let state: State = { health: null, error: null };
const listeners = new Set<(s: State) => void>();
let timer: number | null = null;

function poll() {
  api
    .health()
    .then((h) => (state = { health: h, error: null }))
    .catch((e: Error) => (state = { ...state, error: e.message }))
    .finally(() => listeners.forEach((l) => l(state)));
}

/** Trạng thái API dùng chung (header, footer, trang demo) — hỏi lại mỗi 10 s vì API có thể còn đang nạp mô hình. */
export function useHealth(): State {
  const [s, setS] = useState(state);
  useEffect(() => {
    listeners.add(setS);
    if (timer === null) {
      poll();
      timer = window.setInterval(poll, 10_000);
    }
    return () => {
      listeners.delete(setS);
      if (!listeners.size && timer !== null) {
        window.clearInterval(timer);
        timer = null;
      }
    };
  }, []);
  return s;
}

/** Mô hình / khâu đã nạp chưa (detector, verifier, ocr, classic). */
export function useLoaded(name: string): boolean | null {
  const { health } = useHealth();
  return health ? Boolean(health.models[name]?.loaded) : null;
}
