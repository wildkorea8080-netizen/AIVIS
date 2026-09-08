import type { BrandStat } from "@/lib/types";

interface Props {
  stats: BrandStat[];
  brandKeyword: string;
}

export default function ShareOfVoice({ stats, brandKeyword }: Props) {
  if (stats.length === 0) {
    return (
      <div className="space-y-3">
        <h3 className="text-white font-bold text-sm">경쟁 현황 (점유율)</h3>
        <p className="text-slate-500 text-sm">
          아직 수집된 추천 업체가 없습니다. 모니터링을 실행하면 AI가 함께 추천한
          업체들이 여기에 모입니다.
        </p>
      </div>
    );
  }

  const total = stats.reduce((sum, s) => sum + s.mentions, 0);
  const own = stats.find((s) => s.is_own);
  const ownPosition = own ? stats.indexOf(own) + 1 : null;

  return (
    <div className="space-y-4">
      <div className="flex items-baseline justify-between gap-3">
        <h3 className="text-white font-bold text-sm">경쟁 현황 (점유율)</h3>
        <p className="text-slate-500 text-xs">
          {ownPosition
            ? `${stats.length}곳 중 ${ownPosition}위`
            : `${stats.length}곳 추천됨 · 내 브랜드 미등장`}
        </p>
      </div>

      <div className="space-y-2">
        {stats.slice(0, 10).map((s) => (
          <div key={s.name_key} className="flex items-center gap-3">
            <span
              className={`text-sm w-32 shrink-0 truncate ${
                s.is_own ? "text-indigo-300 font-semibold" : "text-slate-400"
              }`}
              title={s.name}
            >
              {s.name}
            </span>

            <div className="flex-1 bg-slate-800/60 rounded-full h-2 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-700 ${
                  s.is_own ? "bg-indigo-500" : "bg-slate-600"
                }`}
                style={{ width: `${(s.mentions / total) * 100}%` }}
              />
            </div>

            <span className="w-20 shrink-0 text-right text-xs">
              <span className={s.is_own ? "text-indigo-300 font-bold" : "text-slate-400"}>
                {Math.round((s.mentions / total) * 100)}%
              </span>
              {s.avg_rank !== null && (
                <span className="text-slate-600 ml-1.5">{s.avg_rank}위</span>
              )}
            </span>
          </div>
        ))}
      </div>

      {!own && (
        <p className="text-slate-500 text-xs leading-relaxed">
          AI 추천 목록에 <span className="text-slate-300">{brandKeyword}</span>가 아직
          등장하지 않습니다. 위 업체들이 현재 이 질문들을 점유하고 있습니다.
        </p>
      )}
    </div>
  );
}
