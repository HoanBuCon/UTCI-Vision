import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

export type Theme = "light" | "dark";

/** Bảng màu biểu đồ (phân loại, theo thứ tự cố định — đã kiểm định CVD) cho từng chế độ sáng / tối. */
const PALETTE = {
  light: {
    series: ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"],
    seq: ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#104281", "#0d366b"],
    text: "#52514e",
    grid: "#ecebe8",
    axis: "#e4e3df",
    surface: "#ffffff",
    neutral: "#a3a29d",
  },
  dark: {
    series: ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"],
    seq: ["#18283b", "#184f95", "#256abf", "#3987e5", "#86b6ef", "#cde2fb"],
    text: "#c3c2b7",
    grid: "#2a2a28",
    axis: "#2f2f2c",
    surface: "#1a1a19",
    neutral: "#6b6a66",
  },
};
export type ChartColors = (typeof PALETTE)["light"];

const Ctx = createContext<{ theme: Theme; toggle: () => void; colors: ChartColors }>({
  theme: "light",
  toggle: () => {},
  colors: PALETTE.light,
});

function initial(): Theme {
  try {
    const saved = localStorage.getItem("utci-theme");
    if (saved === "light" || saved === "dark") return saved;
  } catch {
    /* bộ nhớ trình duyệt bị chặn */
  }
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(initial);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem("utci-theme", theme);
    } catch {
      /* bỏ qua */
    }
  }, [theme]);
  return (
    <Ctx.Provider value={{ theme, toggle: () => setTheme((t) => (t === "light" ? "dark" : "light")), colors: PALETTE[theme] }}>
      {children}
    </Ctx.Provider>
  );
}

export const useTheme = () => useContext(Ctx);
