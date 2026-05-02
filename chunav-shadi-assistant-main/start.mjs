import { serve } from "srvx/node";
import { serveStatic } from "srvx/static";
import app from "./dist/server/server.js";

const port = Number.parseInt(process.env.PORT || "3000", 10);
const hostname = "0.0.0.0";

serve({
  fetch: app.fetch.bind(app),
  middleware: [
    serveStatic({
      dir: "./dist/client",
    }),
  ],
  hostname,
  port,
  silent: false,
});
