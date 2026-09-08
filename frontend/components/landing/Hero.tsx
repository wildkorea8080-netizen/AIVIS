import { runAudit } from "@/app/audit/actions";
import AuditForm from "@/components/shared/AuditForm";

// 코드에서 확인 가능한 수치만 싣는다.
// 8개 = collector 항목 수, 5개 = ai_clients.ENGINES 등록 수, 30초 = 진단 요청 타임아웃
const STATS = [
  { value: "8개", label: "자동 점검 항목" },
  { value: "5개", label: "추적 AI 엔진" },
  { value: "30초", label: "무료 즉시 결과" },
];

export default function Hero() {
  return (
    <section className="relative min-h-screen bg-slate-950 flex items-center justify-center px-4 pt-16 overflow-hidden">
      {/* 배경 그라데이션 */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-900/20 rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-3xl w-full text-center space-y-8">
        {/* 배지 */}
        <div className="inline-flex items-center gap-2 bg-indigo-950 border border-indigo-800 text-indigo-300 text-xs font-medium px-4 py-2 rounded-full">
          <span className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse" />
          AEO · GEO · AI Search Optimization
        </div>

        {/* 헤드라인 */}
        <h1 className="text-4xl md:text-6xl font-black text-white leading-tight tracking-tight">
          AI가 고객 질문에 답할 때,{" "}
          <br className="hidden md:block" />
          <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
            당신의 비즈니스
          </span>
          가 거기 있나요?
        </h1>

        <p className="text-slate-400 text-lg md:text-xl leading-relaxed max-w-2xl mx-auto">
          ChatGPT·Claude·Gemini·Perplexity·Grok이 추천하는 비즈니스가 되세요.
          <br />
          온라인 브랜드는 URL로, 오프라인 매장은 상호와 지역만으로 진단합니다.
        </p>

        {/* 통계 */}
        <div className="flex justify-center gap-8 md:gap-12">
          {STATS.map((s) => (
            <div key={s.label} className="text-center">
              <div className="text-2xl md:text-3xl font-black text-indigo-400">{s.value}</div>
              <div className="text-slate-500 text-xs mt-1">{s.label}</div>
            </div>
          ))}
        </div>

        {/* 진단 폼 */}
        <div className="max-w-xl mx-auto">
          <AuditForm action={runAudit} compact />
        </div>

        {/* 소셜 프루프 */}
        <p className="text-slate-600 text-sm">
          신용카드 불필요 · 회원가입 불필요 · 결과 링크 공유 가능
        </p>
      </div>
    </section>
  );
}
