import { meta } from "../../../../lib/content";
import { timingSafeEqual } from "node:crypto";
import { allowedPath, allowedMethod } from "../../../../lib/gateway.mjs";

export const runtime = "nodejs";
async function proxy(
  request: Request,
  context: { params: Promise<{ path: string[] }> },
) {
  const path = (await context.params).path.join("/");
  if (!allowedPath(path) || !allowedMethod(path, request.method))
    return new Response("Not found", { status: 404 });
  const expected = process.env.FLAMESAFE_WEB_ACCESS_TOKEN || "";
  const provided = request.headers.get("x-dashboard-token") || "";
  if (
    !expected ||
    Buffer.byteLength(expected) !== Buffer.byteLength(provided) ||
    !timingSafeEqual(Buffer.from(expected), Buffer.from(provided))
  )
    return new Response("Dashboard access token required", { status: 401 });
  if (
    request.method === "POST" &&
    request.headers.get("origin") !== new URL(request.url).origin
  )
    return new Response("Origin rejected", { status: 403 });
  const base = process.env.FLAMESAFE_BACKEND_URL;
  const token = process.env.FLAMESAFE_API_TOKEN;
  if (!base || !token)
    return new Response("Backend not configured", { status: 503 });
  let body: string | undefined;
  if (request.method === "POST") {
    const reader = request.body?.getReader();
    const chunks: Uint8Array[] = [];
    let size = 0;
    if (reader)
      while (true) {
        const part = await reader.read();
        if (part.done) break;
        size += part.value.length;
        if (size > 16384) {
          await reader.cancel();
          return new Response("Request too large", { status: 413 });
        }
        chunks.push(part.value);
      }
    body = Buffer.concat(chunks).toString("utf8");
    try {
      JSON.parse(body);
    } catch {
      return new Response("Invalid JSON", { status: 400 });
    }
  }
  try {
    const response = await fetch(`${base.replace(/\/$/, "")}/v1/${path}`, {
      method: request.method,
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        ...(path === "chat" ? { "X-Evidence-Build": meta.build_id } : {}),
      },
      body,
      cache: "no-store",
      redirect: "error",
      signal: AbortSignal.timeout(110000),
    });
    const payload = await response.text();
    if (response.ok && path === "chat" && JSON.parse(payload).evidence?.build_id !== meta.build_id)
      return Response.json({ detail: "The dashboard and evidence service use different releases." }, { status: 409 });
    return new Response(payload, {
      status: response.status,
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "no-store",
      },
    });
  } catch {
    return new Response("Backend unavailable", { status: 503 });
  }
}
export { proxy as GET, proxy as POST };
