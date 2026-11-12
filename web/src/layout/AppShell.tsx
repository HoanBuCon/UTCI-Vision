import { Suspense, useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useHealth } from "../api/useHealth";
import HealthBadge from "../components/HealthBadge";
import Icon from "../components/Icon";
import { Busy } from "../components/ui";
import { useTheme } from "../theme";
import { findNav, NAV } from "./nav";

function readCollapsed(): boolean {
  try {
    return localStorage.getItem("utci-sidebar") === "collapsed";
  } catch {
    return false;
  }
}

/**
 * Bố cục Application: sidebar trái cao hết màn hình (nằm trên header/footer), header + footer thuộc cột nội dung,
 * chỉ vùng nội dung cuộn. ≥1100 px: sidebar đầy đủ (thu gọn được); 768–1100 px: dải biểu tượng; <768 px: ngăn kéo.
 */
export default function AppShell() {
  const { pathname } = useLocation();
  const { theme, toggle } = useTheme();
  const { health } = useHealth();
  const [collapsed, setCollapsed] = useState(readCollapsed);
  const [drawer, setDrawer] = useState(false);
  const current = findNav(pathname);

  useEffect(() => setDrawer(false), [pathname]);
  useEffect(() => {
    document.title = `${current?.item.label ?? "UTCI-VISION"} · UTCI-VISION`;
    document.querySelector(".scroll")?.scrollTo({ top: 0 });
  }, [pathname, current?.item.label]);
  useEffect(() => {
    try {
      localStorage.setItem("utci-sidebar", collapsed ? "collapsed" : "open");
    } catch {
      /* bỏ qua */
    }
  }, [collapsed]);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setDrawer(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div className={`shell ${collapsed ? "collapsed" : ""} ${drawer ? "drawer-open" : ""}`}>
      <aside className="sidebar" aria-label="Điều hướng chính">
        <NavLink to="/" className="brand" title="UTCI-VISION">
          <span className="brand-logo">UV</span>
          <span className="brand-text">
            <b>UTCI-VISION</b>
            <span>Nhận diện biển báo giao thông</span>
          </span>
        </NavLink>
        <nav className="nav">
          {NAV.map((g) => (
            <div className="nav-group" key={g.title}>
              <div className="nav-group-title">{g.title}</div>
              {g.items.map((i) => (
                <NavLink key={i.to} to={i.to} end title={i.label}>
                  <Icon name={i.icon} />
                  <span>{i.label}</span>
                  {i.tag && <span className={`nav-badge ${i.tag.toLowerCase()}`}>{i.tag}</span>}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
        <div className="sidebar-foot">
          <button className="collapse-btn icon-btn" onClick={() => setCollapsed((c) => !c)} title={collapsed ? "Mở rộng" : "Thu gọn"}>
            <span style={{ display: "inline-flex", transform: collapsed ? "rotate(180deg)" : undefined }}>
              <Icon name="chevrons" />
            </span>
            <span>Thu gọn</span>
          </button>
        </div>
      </aside>
      <div className="scrim" onClick={() => setDrawer(false)} />

      <div className="main-col">
        <header className="header">
          <button className="icon-btn menu-btn" aria-label="Mở menu" onClick={() => setDrawer(true)}>
            <Icon name="menu" />
          </button>
          <div className="crumbs">
            <span>{current?.group ?? "UTCI-VISION"}</span>
            <b>{current?.item.label ?? "Không tìm thấy trang"}</b>
          </div>
          <div className="spacer" />
          <HealthBadge />
          <button className="icon-btn" onClick={toggle} aria-label="Đổi giao diện sáng / tối" title="Sáng / tối">
            <Icon name={theme === "dark" ? "sun" : "moon"} />
          </button>
        </header>
        <div className="scroll">
          <main className="content">
            <Suspense fallback={<Busy text="Đang tải trang…" />}>
              <Outlet />
            </Suspense>
          </main>
          <footer className="footer">
            <span>
              <b>UTCI-VISION</b> {health ? `v${health.version}` : ""} · Đồ án Thị giác máy tính 2026 · nhóm 5 thành viên
            </span>
            <span className="sep" />
            <span>Mô hình 20261029-1030_yolo11s_960 · dataset processed/v1</span>
            <span>Dữ liệu CC BY 4.0 (Roboflow) · Ultralytics AGPL-3.0 · VietOCR</span>
            <span>© 2026 LiemDaiHiep · Apache-2.0</span>
          </footer>
        </div>
      </div>
    </div>
  );
}
