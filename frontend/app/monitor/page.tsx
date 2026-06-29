export default function MonitorIndexPage() {
  return (
    <div className="min-h-screen bg-slate-950 pt-24 px-4">
      <div className="max-w-2xl mx-auto text-center space-y-6">
        <div className="inline-flex items-center gap-2 bg-violet-950 border border-violet-800 text-violet-300 text-xs font-medium px-4 py-2 rounded-full">
          <span className="w-2 h-2 bg-violet-400 rounded-full animate-pulse" />
          AI 언급률 모니터링
        </div>
        <h1 className="text-4xl font-black text-white">
          ChatGPT·Claude가<br />
          <span className="text-violet-400">내 브랜드를 추천하나요?</span>
        </h1>
        <p className="text-slate-400 text-lg">
          질문을 등록하면 매주 AI 모델에 실제로 물어보고<br />
          내 브랜드 언급률 변화를 추적합니다.
        </p>
        <a
          href="/monitor/new"
          className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl px-8 py-4 text-lg transition-all"
        >
          모니터링 시작하기 →
        </a>
        <p className="text-slate-600 text-sm">로그인 불필요 · 무료 시작</p>
      </div>
    </div>
  );
}
