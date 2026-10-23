/**
 * Chế độ Giải thích (FR-WEB-05, FR-PIPE-14). Phụ trách: TV2 — S4.
 * TODO: api.detectImage(file, { debug: true }) -> hiển thị theo thứ tự khâu:
 *  chất lượng ảnh & ảnh sau tăng cường [CV] -> box YOLO thô [DL] -> đặc trưng vùng + điểm xác minh [CV+ML]
 *  -> vùng số / dòng chữ / biển phụ [CV] -> VietOCR [DL] + regex / từ điển -> kết quả cuối.
 */
export default function ExplainPage() {
  return (
    <section>
      <h1>Giải thích pipeline</h1>
      <p className="todo">Khung trang — hiện thực ở Sprint 4.</p>
    </section>
  );
}
