import { serve } from "srvx/node";
import { serveStatic } from "srvx/static";
import app from "./dist/server/server.js";

const port = Number.parseInt(process.env.PORT || "3000", 10);
const hostname = "0.0.0.0";

function applyCacheHeaders(response, requestUrl) {
  const responseWithHeaders = new Response(response.body, response);
  const pathname = new URL(requestUrl).pathname;
  const contentType = responseWithHeaders.headers.get("content-type") || "";

  if (pathname.startsWith("/assets/")) {
    responseWithHeaders.headers.set("Cache-Control", "public, max-age=31536000, immutable");
    return responseWithHeaders;
  }

  if (
    contentType.includes("text/html") ||
    pathname === "/" ||
    !pathname.includes(".")
  ) {
    responseWithHeaders.headers.set("Cache-Control", "no-store, max-age=0");
    return responseWithHeaders;
  }

  if (pathname === "/manifest.json" || pathname.startsWith("/icon-") || pathname === "/favicon.svg") {
    responseWithHeaders.headers.set("Cache-Control", "public, max-age=3600");
  }

  return responseWithHeaders;
}

serve({
  async fetch(request) {
    const response = await app.fetch(request);
    return applyCacheHeaders(response, request.url);
  },
  middleware: [
    serveStatic({
      dir: "./dist/client",
    }),
  ],
  hostname,
  port,
  silent: false,
});
