import { meta } from "../../../../lib/content";
import { timingSafeEqual } from "node:crypto";
import { allowedPath, allowedMethod } from "../../../../lib/gateway.mjs";

export const runtime = "nodejs";

// Public Ask abuse limit: in-memory, per instance (not shared across instances).
const WINDOW_MS = 10 * 60 * 1000;
const MAX_REQUESTS = 10;
const hits = new Map<string, number[]>();

function clientIp(request: Request): string {
  const forwarded = request.headers.get("x-forwarded-for") || "";
  return forwarded.split(",")[0].trim() || "unknown";
}

function rateLimited(ip: string): boolean {
  const now = Date.now();
  if (hits.size > 5000)
    for (const [key, times] of hits)
      if (times[times.length - 1] <= now - WINDOW_MS) hits.delete(key);
  const recent = (hits.get(ip) || []).filter((t) => t > now - WINDOW_MS);
  if (recent.length >= MAX_REQUESTS) {
    hits.set(ip, recent);
    return true;
  }
  recent.push(now);
  hits.set(ip, recent);
  return false;
}

async function proxy(
  request: Request,
  context: { params: Promise<{ path: string[] }> },
) {
  const path = (await context.params).path.join("/");
  if (!allowedPath(path) || !allowedMethod(path, request.method))
    return new Response("Not found", { status: 404 });
  const publicChat =
    process.env.FLAMESAFE_PUBLIC_ASK === "true" &&
    path === "chat" &&
    request.method === "POST";
  if (!publicChat) {
    const expected = process.env.FLAMESAFE_WEB_ACCESS_TOKEN || "";
    const provided = request.headers.get("x-dashboard-token") || "";
    if (
      !expected ||
      Buffer.byteLength(expected) !== Buffer.byteLength(provided) ||
      !timingSafeEqual(Buffer.from(expected), Buffer.from(provided))
    )
      return new Response("Dashboard access token required", { status: 401 });
  }
  if (
    request.method === "POST" &&
    request.headers.get("origin") !== new URL(request.url).origin
  )
    return new Response("Origin rejected", { status: 403 });
  if (publicChat && rateLimited(clientIp(request)))
    return Response.json(
      { detail: "Too many questions right now. Try again in a few minutes." },
      { status: 429, headers: { "Retry-After": "600" } },
    );
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
