import { serve } from "srvx/node";
import app from "./dist/server/server.js";

const port = Number.parseInt(process.env.PORT || "3000", 10);
const hostname = "0.0.0.0";

serve({
  fetch: app.fetch.bind(app),
  hostname,
  port,
  silent: false,
});
