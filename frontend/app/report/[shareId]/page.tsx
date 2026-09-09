import { notFound } from "next/navigation";
import { Suspense } from "react";
import type { ReadinessReport } from "@/lib/types";
import ReportView from "@/app/report/ReportView";

const API_BASE = process.env.API_URL ?? "http://localhost:8000";

async function fetchReport(shareId: string): Promise<ReadinessReport | null> {
  try {
    // 타임아웃이 없으면 잠든 서버를 기다리다 플랫폼이 함수를 죽여 500이 뜬다
    const res = await fetch(`${API_BASE}/report/${shareId}`, {
      cache: "no-store",
      signal: AbortSignal.timeout(50_000),
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function SharedReportPage({ params }: { params: { shareId: string } }) {
  const report = await fetchReport(params.shareId);
  if (!report) return notFound();

  const shareUrl = `${process.env.NEXT_PUBLIC_BASE_URL ?? "http://localhost:3001"}/report/${params.shareId}`;

  return (
    <div className="min-h-screen bg-slate-950 pt-20 pb-16 px-4">
      <Suspense>
        <ReportView report={report} reportUrl={shareUrl} />
      </Suspense>
    </div>
  );
}
