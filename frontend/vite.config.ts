import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  // Replaced at build time; jest provides the same global via its config.
  define: {
    __API_URL__: JSON.stringify(
      process.env.VITE_API_URL ?? "http://localhost:8000",
    ),
  },
  server: {
    host: true,
    port: 5173,
  },
});
