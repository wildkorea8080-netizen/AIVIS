interface Props {
  targetUrl: string;
  placeName?: string | null;
  mode: "local" | "brand";
}

export default function MonitorCTA({ targetUrl, placeName, mode }: Props) {
  const params = new URLSearchParams({
    url: targetUrl,
    ...(placeName ? { keyword: placeName } : {}),
    mode,
  });

  return (
    <div className="bg-gradient-to-r from-indigo-950 to-violet-950 border border-indigo-700 rounded-2xl p-6 space-y-4">
      <div className="flex items-start gap-4">
        <div className="text-3xl">📡</div>
        <div className="space-y-1">
          <h3 className="text-white font-bold">이 브랜드, AI가 실제로 추천하나요?</h3>
          <p className="text-indigo-300 text-sm leading-relaxed">
            진단은 준비도 체크입니다. 모니터링을 시작하면 ChatGPT·Claude가
            실제로 내 브랜드를 언급하는지 매주 추적합니다.
          </p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <a
          href={`/monitor/new?${params.toString()}`}
          className="flex-1 text-center bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl py-3 px-4 text-sm transition-all"
        >
          모니터링 시작하기 →
        </a>
        <a
          href="/audit"
          className="flex-1 text-center bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium rounded-xl py-3 px-4 text-sm transition-all"
        >
          다른 사이트 진단하기
        </a>
      </div>

      <p className="text-slate-600 text-xs text-center">무료 · 로그인 불필요</p>
    </div>
  );
}
