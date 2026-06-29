const STEPS = [
  {
    step: "01",
    icon: "🔍",
    title: "30초 무료 진단",
    desc: "URL을 입력하면 AIVIS가 5가지 신호를 자동 수집합니다. robots.txt, 구조화 데이터, 플레이스 등록, 커뮤니티 언급을 즉시 분석합니다.",
  },
  {
    step: "02",
    icon: "📋",
    title: "항목별 원인 분석",
    desc: "AIVIS Score와 항목별 상태를 확인합니다. 어떤 신호가 AI 노출을 막고 있는지, 무엇부터 개선해야 하는지 명확하게 알 수 있습니다.",
  },
  {
    step: "03",
    icon: "🚀",
    title: "최적화 실행",
    desc: "항목별 개선 팁을 직접 실행하거나, 전문가 대행을 통해 빠르게 개선합니다. 평균 2~4주 내에 AI가 당신의 비즈니스를 인식하기 시작합니다.",
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
