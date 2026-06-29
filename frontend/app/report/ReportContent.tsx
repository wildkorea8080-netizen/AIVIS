"use client";

import { useSearchParams } from "next/navigation";
import { useMemo } from "react";
import { decodeReport } from "@/lib/report-codec";
import ReportView from "@/app/report/ReportView";

export default function ReportContent() {
  const params = useSearchParams();
  const encoded = params.get("d");

  const report = useMemo(() => {
    if (!encoded) return null;
    try {
      return decodeReport(encoded);
    } catch {
      return null;
    }
  }, [encoded]);

  if (!report) {
    return (
      <div className="max-w-2xl mx-auto text-center py-20">
        <p className="text-slate-400 text-lg">리포트 데이터를 찾을 수 없습니다.</p>
        <a href="/audit" className="mt-6 inline-block bg-indigo-600 text-white px-6 py-3 rounded-xl">
          다시 진단하기
        </a>
      </div>
    );
  }

  const reportUrl = typeof window !== "undefined" ? window.location.href : "";
  return <ReportView report={report} reportUrl={reportUrl} />;
}
