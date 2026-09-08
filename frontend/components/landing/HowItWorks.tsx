const STEPS = [
  {
    step: "01",
    icon: "🔍",
    title: "30초 무료 진단",
    desc: "AIVIS가 8가지 신호를 자동 수집합니다. 구조화 데이터, robots.txt, llms.txt, 사이트맵, 렌더링 방식, 메타태그, 플레이스 등록, 커뮤니티 언급을 한 번에 확인합니다.",
  },
  {
    step: "02",
    icon: "📋",
    title: "항목별 원인 분석",
    desc: "AIVIS Score와 항목별 상태를 확인합니다. 어떤 신호가 AI 노출을 막고 있는지, 무엇부터 손대야 하는지 개선 팁과 함께 보여줍니다.",
  },
  {
    step: "03",
    icon: "📡",
    title: "모니터링으로 확인",
    desc: "개선한 뒤에는 실제로 달라졌는지 봐야 합니다. 매일 5개 AI 엔진에 질문을 던져 내 브랜드가 추천되는지, 누가 그 자리를 차지하고 있는지 추적합니다.",
  },
];

export default function HowItWorks() {
  return (
    <section className="bg-slate-900 py-24 px-4">
      <div className="max-w-5xl mx-auto space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl md:text-4xl font-black text-white">
            3단계로 AI 추천 비즈니스가 됩니다
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {STEPS.map((s, i) => (
            <div key={s.step} className="relative space-y-4">
              {i < STEPS.length - 1 && (
                <div className="hidden md:block absolute top-8 left-[calc(100%+1rem)] w-8 text-slate-600 text-xl">→</div>
              )}
              <div className="flex items-center gap-3">
                <span className="text-slate-600 font-black text-2xl">{s.step}</span>
                <span className="text-3xl">{s.icon}</span>
              </div>
              <h3 className="text-white font-bold text-xl">{s.title}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
