import type { DashboardRow } from "@/lib/types";

const AI_MODELS = ["chatgpt", "claude", "perplexity", "gemini", "grok"];
const MODEL_LABEL: Record<string, string> = {
  chatgpt: "ChatGPT", claude: "Claude", perplexity: "Perplexity", gemini: "Gemini", grok: "Grok",
};

interface Props {
  rows: DashboardRow[];
}

export default function MentionHeatmap({ rows }: Props) {
  if (rows.length === 0) {
    return (
      <div className="text-center py-12 text-slate-500 text-sm">
        아직 실행 이력이 없습니다. 위 버튼으로 첫 모니터링을 시작하세요.
      </div>
    );
  }

  // 실행 이력을 날짜별로 그룹화
  const allDates = Array.from(
    new Set(rows.flatMap((r) => r.runs.map((run) => run.ran_at.slice(0, 10))))
  ).sort();

  return (
    <div className="space-y-6 overflow-x-auto">
      {rows.map((row) => {
        // 날짜 × 모델 매핑
        const grid: Record<string, Record<string, boolean | null>> = {};
        for (const date of allDates) {
          grid[date] = {};
          for (const m of AI_MODELS) grid[date][m] = null;
        }
        for (const run of row.runs) {
          const date = run.ran_at.slice(0, 10);
          if (grid[date]) grid[date][run.ai_model] = run.mentioned;
        }

        const mentionCount = row.runs.filter((r) => r.mentioned).length;
        const total = row.runs.length;

        return (
          <div key={row.question_id} className="space-y-2">
            <div className="flex items-start justify-between gap-4">
              <p className="text-slate-300 text-sm leading-snug flex-1">{row.question}</p>
              <span className={`shrink-0 text-sm font-bold ${row.mention_rate > 0.5 ? "text-green-400" : row.mention_rate > 0 ? "text-amber-400" : "text-slate-500"}`}>
                {total > 0 ? `${Math.round(row.mention_rate * 100)}%` : "—"}
              </span>
            </div>

            {/* 히트맵 그리드 */}
            <div className="flex gap-1 items-end">
              {/* 모델 레이블 */}
              <div className="flex flex-col gap-1 shrink-0 w-20">
                {AI_MODELS.map((m) => (
                  <div key={m} className="h-6 flex items-center">
                    <span className="text-slate-600 text-xs">{MODEL_LABEL[m]}</span>
                  </div>
                ))}
              </div>

              {/* 날짜별 셀 */}
              <div className="flex gap-1">
                {allDates.map((date) => (
                  <div key={date} className="flex flex-col gap-1">
                    {AI_MODELS.map((m) => {
                      const val = grid[date][m];
                      return (
                        <div
                          key={m}
                          title={`${date} ${MODEL_LABEL[m]}: ${val === null ? "미실행" : val ? "언급됨" : "미언급"}`}
                          className={`w-6 h-6 rounded-sm transition-all ${
                            val === null
                              ? "bg-slate-800"
                              : val
                              ? "bg-green-500 shadow-sm shadow-green-500/30"
                              : "bg-slate-700"
                          }`}
                        />
                      );
                    })}
                    <span className="text-slate-700 text-[9px] text-center mt-0.5">{date.slice(5)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
