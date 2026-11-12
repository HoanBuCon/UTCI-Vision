import { lazy } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import AppShell from "./layout/AppShell";

// tách code theo trang: Recharts chỉ tải ở trang có biểu đồ
const AboutPage = lazy(() => import("./pages/AboutPage"));
const ComparePage = lazy(() => import("./pages/ComparePage"));
const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const DataPage = lazy(() => import("./pages/DataPage"));
const DlDemoPage = lazy(() => import("./pages/DlDemoPage"));
const LibraryPage = lazy(() => import("./pages/LibraryPage"));
const PipelinePage = lazy(() => import("./pages/PipelinePage"));
const ResultsPage = lazy(() => import("./pages/ResultsPage"));
const TraditionalPage = lazy(() => import("./pages/TraditionalPage"));
const VideoPage = lazy(() => import("./pages/VideoPage"));
const WebcamPage = lazy(() => import("./pages/WebcamPage"));

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<DashboardPage />} />
        <Route path="data" element={<DataPage />} />
        <Route path="library" element={<LibraryPage />} />
        <Route path="pipeline" element={<PipelinePage />} />
        <Route path="demo/dl" element={<DlDemoPage />} />
        <Route path="demo/traditional" element={<TraditionalPage />} />
        <Route path="demo/video" element={<VideoPage />} />
        <Route path="demo/webcam" element={<WebcamPage />} />
        <Route path="compare" element={<ComparePage />} />
        <Route path="results" element={<ResultsPage />} />
        <Route path="about" element={<AboutPage />} />
        {/* đường dẫn cũ */}
        <Route path="video" element={<Navigate to="/demo/video" replace />} />
        <Route path="webcam" element={<Navigate to="/demo/webcam" replace />} />
        <Route path="explain" element={<Navigate to="/pipeline" replace />} />
        <Route path="*" element={<p className="muted">Không tìm thấy trang.</p>} />
      </Route>
    </Routes>
  );
}
