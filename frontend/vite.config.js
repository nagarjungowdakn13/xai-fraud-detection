import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:5000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
      "/fraud": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
      "/metrics": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
      "/events": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
      "/decision": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
    },
  },
});
