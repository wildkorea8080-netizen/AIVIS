const AI_MODELS = ["ChatGPT", "Claude", "Perplexity", "Gemini", "Grok"];

// 모의 데이터 — 언급 여부 히트맵 (질문 5개 × 8주)
const MOCK_DATA = [
  [0, 0, 0, 1, 1, 1, 1, 1],
  [0, 0, 1, 1, 1, 1, 1, 1],
  [0, 0, 0, 0, 1, 1, 1, 1],
  [0, 1, 1, 1, 1, 1, 1, 1],
  [0, 0, 0, 1, 1, 1, 1, 1],
];

export default function MonitorTeaser() {
  return (
    <section className="bg-slate-950 py-24 px-4 border-t border-slate-800">
      <div className="max-w-5xl mx-auto space-y-12">
        <div className="flex flex-col md:flex-row items-start gap-6">
          <div className="flex-1 space-y-4">
            <div className="inline-flex items-center gap-2 bg-violet-950 border border-violet-800 text-violet-300 text-xs font-medium px-3 py-1.5 rounded-full">
              Coming Soon
            </div>
            <h2 className="text-3xl md:text-4xl font-black text-white">
              AI가 실제로 당신을<br />
              <span className="text-violet-400">추천하는지 추적합니다</span>
            </h2>
            <p className="text-slate-400 leading-relaxed">
              진단을 넘어 실시간 모니터링으로. 매주 ChatGPT·Claude·Perplexity에
              질문을 던져 내 브랜드 언급률 변화를 추적합니다.
            </p>
            <ul className="space-y-2">
              {[
                "5대 AI 모델 언급률 레이더 차트",
                "주차별 언급률 변화 추이",
                "경쟁 브랜드 63개와 비교",
                "최적화 전략 방향성 자동 생성",
              ].map((item) => (
                <li key={item} className="flex items-center gap-2 text-slate-300 text-sm">
                  <span className="text-violet-400">✓</span> {item}
                </li>
              ))}
            </ul>
          </div>

          {/* 히트맵 미리보기 */}
          <div className="flex-1 bg-slate-900 border border-slate-700 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-white font-semibold text-sm">모니터링 추이</span>
              <span className="text-slate-500 text-xs">8주 기간</span>
            </div>

            {/* 히트맵 */}
            <div className="space-y-2">
              {MOCK_DATA.map((row, qi) => (
                <div key={qi} className="flex items-center gap-2">
                  <span className="text-slate-600 text-xs w-16 shrink-0">질문 {qi + 1}</span>
                  <div className="flex gap-1.5">
                    {row.map((val, wi) => (
                      <div
                        key={wi}
                        className={`w-7 h-7 rounded-md transition-all ${
                          val
                            ? "bg-green-500/80 shadow-sm shadow-green-500/30"
                            : "bg-slate-800"
                        }`}
                      />
                    ))}
                  </div>
                </div>
              ))}
              <div className="flex items-center gap-2 pt-1">
                <span className="text-slate-600 text-xs w-16" />
                <div className="flex gap-1.5">
                  {Array.from({ length: 8 }, (_, i) => (
                    <span key={i} className="w-7 text-center text-slate-600 text-xs">{i + 1}주</span>
                  ))}
                </div>
              </div>
            </div>

            {/* 언급률 */}
            <div className="border-t border-slate-800 pt-3 flex items-center justify-between">
              <div>
                <span className="text-slate-500 text-xs">전체 언급률</span>
                <div className="flex items-baseline gap-2 mt-0.5">
                  <span className="text-slate-400 text-sm line-through">10.8%</span>
                  <span className="text-green-400 font-black text-xl">42.2%</span>
                  <span className="text-green-400 text-xs">+31.4%p</span>
                </div>
              </div>
              <div className="text-right">
                <span className="text-slate-500 text-xs">5대 LLM 동시 추적</span>
                <div className="flex gap-1 mt-1 justify-end">
                  {AI_MODELS.map((m) => (
                    <span key={m} className="text-xs bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded">
                      {m.slice(0, 1)}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
