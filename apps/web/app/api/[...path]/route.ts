import { NextRequest } from "next/server";

// Always run this on the server at request time (never statically cached).
export const dynamic = "force-dynamic";

/**
 * Resolve the backend base URL at RUNTIME.
 *
 * Bracket notation (process.env["NEXT_PUBLIC_API_URL"]) is intentional: Next only
 * inlines dot-access `process.env.NEXT_PUBLIC_*` at build time. Bracket access stays
 * a real runtime lookup, so it picks up the value the deploy (Bicep) injects into the
 * web container at runtime — no rebuild needed when the backend URL changes.
 */
function backendBase(): string {
  return (
    process.env["BACKEND_API_URL"] ||
    process.env["NEXT_PUBLIC_API_URL"] ||
    "http://localhost:8000"
  );
}

async function proxy(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  const target = `${backendBase()}/api/${path.join("/")}${req.nextUrl.search}`;

  const headers = new Headers(req.headers);
  headers.delete("host");
  headers.delete("connection");
  headers.delete("content-length");

  const hasBody = req.method !== "GET" && req.method !== "HEAD";
  const init: RequestInit = {
    method: req.method,
    headers,
    body: hasBody ? await req.arrayBuffer() : undefined,
    redirect: "manual"
  };

  let upstream: Response;
  try {
    upstream = await fetch(target, init);
  } catch {
    return new Response(
      JSON.stringify({ detail: "Backend unreachable from the web server." }),
      { status: 502, headers: { "content-type": "application/json" } }
    );
  }

  const respHeaders = new Headers(upstream.headers);
  respHeaders.delete("content-encoding");
  respHeaders.delete("content-length");
  respHeaders.delete("transfer-encoding");

  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: respHeaders
  });
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
export const OPTIONS = proxy;
