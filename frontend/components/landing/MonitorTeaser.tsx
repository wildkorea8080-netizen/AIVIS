import Link from "next/link";

const FEATURES = [
  "5개 AI 엔진(ChatGPT·Claude·Gemini·Perplexity·Grok) 언급률 추적",
  "질문마다 AI가 실제로 추천한 경쟁 업체 자동 수집",
  "매일 오전 9시 자동 실행 — 언급률 변화를 시계열로 기록",
  "엔진별 언급률 레이더와 실행 이력 히트맵",
];

// 실제 화면 구성을 보여주기 위한 예시 데이터.
// 특정 고객의 성과가 아니라 화면이 어떻게 생겼는지 보여주는 용도다.
const SAMPLE = [
  { name: "서울강남치과", share: 28, rank: "1.4위", own: false },
  { name: "내 브랜드", share: 22, rank: "2.1위", own: true },
  { name: "강남아이치과", share: 18, rank: "2.8위", own: false },
  { name: "연세미소치과", share: 17, rank: "3.2위", own: false },
  { name: "더플란트치과", share: 15, rank: "3.6위", own: false },
];

export default function MonitorTeaser() {
  return (
    <section className="bg-slate-950 py-24 px-4 border-t border-slate-800">
      <div className="max-w-5xl mx-auto">
        <div className="flex flex-col md:flex-row items-start gap-10">
          <div className="flex-1 space-y-4">
            <div className="inline-flex items-center gap-2 bg-violet-950 border border-violet-800 text-violet-300 text-xs font-medium px-3 py-1.5 rounded-full">
              <span className="w-1.5 h-1.5 bg-violet-400 rounded-full" />
              지금 사용 가능
            </div>
            <h2 className="text-3xl md:text-4xl font-black text-white">
              누가 그 질문을<br />
              <span className="text-violet-400">점유하고 있는지 봅니다</span>
            </h2>
            <p className="text-slate-400 leading-relaxed">
              언급률이 0%라는 사실만으로는 알 수 없습니다. 그 질문이 원래 경쟁이 치열한
              것인지, 아직 아무도 선점하지 않은 자리인지. 모니터링은 AI가 그 질문에
              실제로 추천한 업체를 그대로 보여줍니다.
            </p>
            <ul className="space-y-2 pt-1">
              {FEATURES.map((item) => (
                <li key={item} className="flex items-start gap-2 text-slate-300 text-sm leading-relaxed">
                  <span className="text-violet-400 mt-0.5 shrink-0">✓</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
            <div className="pt-3">
              <Link
                href="/monitor/new"
                className="inline-block bg-violet-600 hover:bg-violet-500 text-white font-semibold px-6 py-3 rounded-xl transition-colors"
              >
                모니터링 시작하기 →
              </Link>
            </div>
          </div>

          {/* 화면 미리보기 */}
          <div className="flex-1 w-full bg-slate-900 border border-slate-700 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-white font-semibold text-sm">경쟁 현황 (점유율)</span>
              <span className="text-slate-600 text-xs border border-slate-700 px-2 py-0.5 rounded">
                예시 화면
              </span>
            </div>

            <div className="space-y-2.5">
              {SAMPLE.map((s) => (
                <div key={s.name} className="flex items-center gap-3">
                  <span
                    className={`text-sm w-24 shrink-0 truncate ${
                      s.own ? "text-indigo-300 font-semibold" : "text-slate-400"
                    }`}
                  >
                    {s.name}
                  </span>
                  <div className="flex-1 bg-slate-800/60 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${s.own ? "bg-indigo-500" : "bg-slate-600"}`}
                      style={{ width: `${s.share}%` }}
                    />
                  </div>
                  <span className="w-16 shrink-0 text-right text-xs">
                    <span className={s.own ? "text-indigo-300 font-bold" : "text-slate-400"}>
                      {s.share}%
                    </span>
                    <span className="text-slate-600 ml-1">{s.rank}</span>
                  </span>
                </div>
              ))}
            </div>

            <p className="text-slate-600 text-xs leading-relaxed border-t border-slate-800 pt-3">
              질문별로도 어떤 업체가 추천됐는지 확인할 수 있어, 경쟁이 덜한 질문부터
              공략할 수 있습니다.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
