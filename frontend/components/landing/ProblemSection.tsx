const CARDS = [
  {
    icon: "🤖",
    title: "고객이 AI에게 묻습니다",
    desc: "\"강남 이혼 전문 변호사 추천해줘\", \"홍대 분위기 좋은 카페 어디야?\" — 고객은 이제 네이버·구글 대신 ChatGPT에게 묻습니다.",
  },
  {
    icon: "🎯",
    title: "AI는 아는 브랜드만 추천합니다",
    desc: "AI는 크롤링하고 학습한 정보만 답변합니다. 당신의 사이트가 AI에게 \"보이지 않으면\" 추천 목록에서 영원히 빠집니다.",
  },
  {
    icon: "⚡",
    title: "지금 준비해야 합니다",
    desc: "AI 검색 시대는 이미 시작됐습니다. 경쟁자가 먼저 최적화하면 AI의 학습 패턴이 굳어집니다. 지금이 선점 기회입니다.",
  },
];

export default function ProblemSection() {
  return (
    <section className="bg-slate-900 py-24 px-4">
      <div className="max-w-5xl mx-auto space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl md:text-4xl font-black text-white">
            검색이 바뀌었습니다.<br />
            <span className="text-indigo-400">AI에게 물어보는 시대입니다.</span>
          </h2>
          <p className="text-slate-400 text-lg">
            사람들은 추천을 원할 때 AI에게 직접 묻습니다.<br />
            AI가 당신을 모른다면, 존재하지 않는 것과 같습니다.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {CARDS.map((card) => (
            <div key={card.title} className="bg-slate-800 border border-slate-700 rounded-2xl p-6 space-y-3">
              <div className="text-4xl">{card.icon}</div>
              <h3 className="text-white font-bold text-lg">{card.title}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{card.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
