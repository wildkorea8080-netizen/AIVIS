import type { AuditRequest, ReadinessReport } from "./types";

const API_BASE = process.env.API_URL ?? "http://localhost:8000";

export async function submitAudit(req: AuditRequest): Promise<ReadinessReport> {
  const res = await fetch(`${API_BASE}/audit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
    signal: AbortSignal.timeout(30_000),
    cache: "no-store",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = err?.detail;
    if (Array.isArray(detail)) {
      throw new Error(detail.map((d: { msg: string }) => d.msg).join(", "));
    }
    throw new Error(typeof detail === "string" ? detail : `HTTP ${res.status}`);
  }
  return res.json();
}
