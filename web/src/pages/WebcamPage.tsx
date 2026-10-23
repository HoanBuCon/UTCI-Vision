/**
 * Trang Webcam realtime (FR-WEB-03). Phụ trách: TV2 (TV3 hỗ trợ) — S4.
 * TODO:
 *  1. getUserMedia -> <video>; mỗi vòng: vẽ frame lên canvas ẩn (≤ 960 px), toBlob JPEG q≈0.7
 *  2. WebSocket api.streamUrl(): gửi blob, CHỜ nhận DetectResponse rồi mới gửi frame tiếp (back-pressure)
 *  3. Vẽ box lên canvas theo kết quả mới nhất; hiển thị FPS + latency_ms
 *  4. Panel "biển vừa gặp": mỗi track_id hiện một lần, kèm giá trị/chữ khi tác vụ nền trả về
 */
export default function WebcamPage() {
  return (
    <section>
      <h1>Webcam thời gian thực</h1>
      <p className="todo">Khung trang — hiện thực ở Sprint 4.</p>
    </section>
  );
}
