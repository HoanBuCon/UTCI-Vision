import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import type { JobStatus } from "../api/types";
import Dropzone from "../components/Dropzone";

interface SummaryRow {
  class_name?: string;
  first_seen_s?: number;
  frames?: number;
  value?: string;
  text?: string;
  sub_sign?: string;
}

/** Trang Video (FR-WEB-02): tải video -> job nền -> tiến độ -> video kết quả + bảng biển đã xuất hiện. */
export default function VideoPage() {
  const [job, setJob] = useState<JobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const timer = useRef<number | null>(null);

  useEffect(() => () => void (timer.current && window.clearInterval(timer.current)), []);

  async function run(file: File) {
    setError(null);
    setJob(null);
    setUploading(true);
    try {
      const { job_id } = await api.createVideoJob(file);
      setJob({ job_id, status: "queued", progress: 0, result_video_url: null, summary: [], error: null });
      timer.current = window.setInterval(async () => {
        try {
          const s = await api.jobStatus(job_id);
          setJob(s);
          if (s.status === "done" || s.status === "failed") window.clearInterval(timer.current!);
        } catch (e) {
          setError((e as Error).message);
          window.clearInterval(timer.current!);
        }
      }, 1000);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setUploading(false);
    }
  }

  const running = uploading || job?.status === "queued" || job?.status === "running";
  const rows = (job?.summary ?? []) as SummaryRow[];
  return (
    <section>
      <h1>Nhận diện từ video</h1>
      <Dropzone accept="video/*" hint="Kéo-thả hoặc chọn video (MP4/AVI/MOV/MKV/WebM, ≤ 200 MB, ≤ 3 phút)" disabled={running} onFile={run} />
      {uploading && <p className="muted">Đang tải lên…</p>}
      {error && <p className="error">Lỗi: {error}</p>}
      {job && (
        <div className="card">
          <p>
            Job <code>{job.job_id}</code> — {{ queued: "đang chờ", running: "đang xử lý", done: "xong", failed: "lỗi" }[job.status]}
          </p>
          <progress value={job.progress} max={1} /> {(job.progress * 100).toFixed(0)}%
          {job.error && <p className="error">{job.error}</p>}
          {job.result_video_url && (
            <>
              <video className="result-video" src={job.result_video_url} controls />
              <p className="small">
                <a href={`${job.result_video_url}?download=true`}>Tải video kết quả</a> (nếu trình duyệt không phát được, hãy tải về)
              </p>
            </>
          )}
          {rows.length > 0 && (
            <>
              <h2>Biển đã xuất hiện ({rows.length})</h2>
              <table>
                <thead>
                  <tr>
                    <th>Thời điểm</th>
                    <th>Biển</th>
                    <th>Số frame</th>
                    <th>Giá trị / chữ</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r, i) => (
                    <tr key={i}>
                      <td>{r.first_seen_s?.toFixed(1)} s</td>
                      <td>{r.class_name}</td>
                      <td>{r.frames}</td>
                      <td>{[r.value, r.text, r.sub_sign && `biển phụ: ${r.sub_sign}`].filter(Boolean).join(" · ")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </div>
      )}
    </section>
  );
}
