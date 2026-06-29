import { Suspense } from "react";
import ReportContent from "./ReportContent";

export const metadata = { title: "AI 노출 진단 리포트 — AIVIS" };

export default function ReportPage() {
  return (
    <main className="min-h-screen bg-slate-950 pt-24 pb-20 px-4">
      <Suspense
        fallback={
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="text-center space-y-4">
              <div className="inline-block w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-slate-400">리포트를 불러오는 중...</p>
            </div>
          </div>
        }
      >
        <ReportContent />
      </Suspense>
    </main>
  );
}
