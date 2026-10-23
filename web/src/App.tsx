import { NavLink, Route, Routes } from "react-router-dom";
import HealthBadge from "./components/HealthBadge";
import ExplainPage from "./pages/ExplainPage";
import ImagePage from "./pages/ImagePage";
import LibraryPage from "./pages/LibraryPage";
import VideoPage from "./pages/VideoPage";
import WebcamPage from "./pages/WebcamPage";

const NAV = [
  { to: "/", label: "Ảnh" },
  { to: "/video", label: "Video" },
  { to: "/webcam", label: "Webcam" },
  { to: "/library", label: "Thư viện biển báo" },
  { to: "/explain", label: "Giải thích" },
];

export default function App() {
  return (
    <div className="app">
      <header className="topbar">
        <strong>UTCI-VISION</strong>
        <nav>
          {NAV.map((n) => (
            <NavLink key={n.to} to={n.to} end>
              {n.label}
            </NavLink>
          ))}
        </nav>
        <HealthBadge />
      </header>
      <main>
        <Routes>
          <Route path="/" element={<ImagePage />} />
          <Route path="/video" element={<VideoPage />} />
          <Route path="/webcam" element={<WebcamPage />} />
          <Route path="/library" element={<LibraryPage />} />
          <Route path="/explain" element={<ExplainPage />} />
        </Routes>
      </main>
    </div>
  );
}
