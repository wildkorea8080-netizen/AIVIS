import { runAudit } from "./actions";
import AuditForm from "@/components/shared/AuditForm";

export const metadata = { title: "AI 노출 진단 — AIVIS" };

export default function AuditPage() {
  return (
    <main className="min-h-screen bg-slate-950 flex items-center justify-center px-4 py-20">
      <div className="w-full max-w-xl">
        <h1 className="text-3xl font-bold text-white text-center mb-2">
          AI 노출 진단
        </h1>
        <p className="text-slate-400 text-center mb-10">
          URL을 입력하면 30초 내로 AIVIS Score를 산출합니다.
        </p>
        <AuditForm action={runAudit} />
      </div>
    </main>
  );
}
