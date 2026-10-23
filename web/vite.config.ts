import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// Cổng đọc từ ../.env (UTCI_DEV_PORT, UTCI_API_PORT) — không dùng cổng mặc định 5173/8000.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, "..", "UTCI_");
  const devPort = Number(env.UTCI_DEV_PORT ?? 15173);
  const api = `http://127.0.0.1:${env.UTCI_API_PORT ?? 18100}`;
  return {
    plugins: [react()],
    server: { port: devPort, strictPort: true, proxy: { "/api": { target: api, changeOrigin: true, ws: true } } },
    preview: { port: devPort, strictPort: true },
  };
});
