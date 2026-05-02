import { defineConfig } from "@lovable.dev/vite-tanstack-config";

const port = Number.parseInt(process.env.PORT || "3000", 10);

export default defineConfig({
  cloudflare: false,
  vite: {
    server: {
      host: "0.0.0.0",
      port,
    },
    preview: {
      host: "0.0.0.0",
      port,
    },
  },
});
