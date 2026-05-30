import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  if (mode === "production" && !process.env.VITE_API_URL?.trim()) {
    console.warn(
      "\n[Vite] VITE_API_URL is not set. Set it to your Railway API URL in Vercel env vars.\n" +
        "       Images will load from public/; API calls will fail until configured.\n",
    );
  }

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        "/api": {
          target: "http://127.0.0.1:8000",
          changeOrigin: true,
        },
        "/images": {
          target: "http://127.0.0.1:8000",
          changeOrigin: true,
        },
      },
    },
  };
});
