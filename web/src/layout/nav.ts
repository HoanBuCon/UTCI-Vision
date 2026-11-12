export interface NavItem {
  to: string;
  label: string;
  icon: string;
  tag?: "CV" | "DL";
}
export interface NavGroup {
  title: string;
  items: NavItem[];
}

/** Điều hướng chính (sidebar) — nhóm theo luồng trình bày đồ án: dữ liệu -> pipeline -> demo -> so sánh -> kết quả. */
export const NAV: NavGroup[] = [
  { title: "Tổng quan", items: [{ to: "/", label: "Bảng điều khiển", icon: "home" }] },
  {
    title: "Dữ liệu",
    items: [
      { to: "/data", label: "Mô tả dữ liệu (EDA)", icon: "data" },
      { to: "/library", label: "Thư viện biển báo", icon: "book" },
    ],
  },
  { title: "Hệ thống", items: [{ to: "/pipeline", label: "Pipeline hệ thống", icon: "flow" }] },
  {
    title: "Demo",
    items: [
      { to: "/demo/dl", label: "Học sâu (YOLO11)", icon: "brain", tag: "DL" },
      { to: "/demo/traditional", label: "CV truyền thống", icon: "scan", tag: "CV" },
      { to: "/demo/video", label: "Video", icon: "video" },
      { to: "/demo/webcam", label: "Webcam", icon: "camera" },
    ],
  },
  {
    title: "Đánh giá",
    items: [
      { to: "/compare", label: "So sánh CV ↔ DL", icon: "compare" },
      { to: "/results", label: "Kết quả thực nghiệm", icon: "chart" },
    ],
  },
  { title: "Dự án", items: [{ to: "/about", label: "Giới thiệu", icon: "info" }] },
];

export function findNav(pathname: string): { group: string; item: NavItem } | null {
  for (const g of NAV) for (const i of g.items) if (i.to === pathname) return { group: g.title, item: i };
  return null;
}
