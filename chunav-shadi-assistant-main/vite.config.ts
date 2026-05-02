import { defineConfig } from "@lovable.dev/vite-tanstack-config";

const port = Number.parseInt(process.env.PORT || "3000", 10);

export default defineConfig({
  cloudflare: false,
  vite: {
    server: {
      host: "0.0.0.0",
      port,
      allowedHosts: ["all", ".onrender.com", "localhost"],
    },
    preview: {
      host: "0.0.0.0",
      port,
      allowedHosts: [
        "all",
        ".onrender.com",
        "chunav-mitra-1.onrender.com",
        "chunav-mitra-frontend.onrender.com",
        "localhost",
        "127.0.0.1",
      ],
    },
  },
});
