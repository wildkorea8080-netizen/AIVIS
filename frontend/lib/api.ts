import type { AuditRequest, ReadinessReport } from "./types";

const API_BASE = process.env.API_URL ?? "http://localhost:8000";

export async function submitAudit(req: AuditRequest): Promise<ReadinessReport> {
  const res = await fetch(`${API_BASE}/audit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
    // 워밍 상태에서는 10초 안팎이면 끝난다. 여유를 둔 이유는 무료 호스팅의
    // 콜드 스타트(유휴 후 첫 요청)가 30초를 넘길 수 있기 때문이다.
    signal: AbortSignal.timeout(60_000),
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
