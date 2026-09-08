"use client";

import type { ModelStat } from "@/lib/types";

const MODEL_COLOR: Record<string, string> = {
  chatgpt: "#10b981",
  claude: "#f59e0b",
  gemini: "#3b82f6",
  perplexity: "#8b5cf6",
  grok: "#ec4899",
};
const FALLBACK_COLOR = "#64748b";

type EngineState = "unconfigured" | "not-run" | "measured";

function stateOf(s: ModelStat): EngineState {
  if (!s.configured) return "unconfigured";
  if (s.total_runs === 0) return "not-run";
  return "measured";
}

const CX = 130;
const CY = 118;
const R = 80;

export default function ModelRadar({ stats }: { stats: ModelStat[] }) {
  if (stats.length < 3) return null;

  const n = stats.length;
  const angles = stats.map((_, i) => (i * 2 * Math.PI) / n - Math.PI / 2);

  const at = (scale: number, i: number) => ({
    x: CX + R * scale * Math.cos(angles[i]),
    y: CY + R * scale * Math.sin(angles[i]),
  });

  const toPath = (pts: { x: number; y: number }[]) =>
    pts.map((p, i) => `${i === 0 ? "M" : "L"}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ") + " Z";

  const dataPoints = stats.map((s, i) => at(stateOf(s) === "measured" ? s.rate : 0, i));
  const measuredCount = stats.filter((s) => stateOf(s) === "measured").length;
  const hasArea = stats.some((s) => stateOf(s) === "measured" && s.rate > 0);

  return (
    <div className="space-y-4">
      <div className="flex items-baseline justify-between gap-3">
        <h3 className="text-white font-bold text-sm">AI 엔진별 언급률</h3>
        <p className="text-slate-500 text-xs">
          {measuredCount}/{stats.length}개 엔진 추적 중
        </p>
      </div>

      <div className="flex flex-col lg:flex-row items-center gap-8">
        <svg viewBox="0 0 260 240" className="w-[260px] h-[240px] shrink-0">
          {[0.25, 0.5, 0.75, 1].map((scale) => (
            <path
              key={scale}
              d={toPath(stats.map((_, i) => at(scale, i)))}
              fill="none"
              stroke="#1e293b"
              strokeWidth="1"
            />
          ))}

          {stats.map((s, i) => {
            const end = at(1, i);
            const inactive = stateOf(s) !== "measured";
            return (
              <line
                key={s.ai_model}
                x1={CX}
                y1={CY}
                x2={end.x}
                y2={end.y}
                stroke={inactive ? "#1e293b" : "#334155"}
                strokeWidth="1"
                strokeDasharray={inactive ? "3 3" : undefined}
              />
            );
          })}

          {hasArea && (
            <path d={toPath(dataPoints)} fill="#6366f1" fillOpacity="0.25" stroke="#6366f1" strokeWidth="2" />
          )}

          {stats.map((s, i) => {
            const p = dataPoints[i];
            const state = stateOf(s);
            if (state !== "measured") {
              return (
                <circle key={s.ai_model} cx={p.x} cy={p.y} r="3"
                  fill="#0f172a" stroke="#475569" strokeWidth="1.5" />
              );
            }
            return (
              <circle key={s.ai_model} cx={p.x} cy={p.y} r="4"
                fill={MODEL_COLOR[s.ai_model] ?? FALLBACK_COLOR} />
            );
          })}

          {stats.map((s, i) => {
            const lp = at(1.22, i);
            const inactive = stateOf(s) !== "measured";
            return (
              <text
                key={s.ai_model}
                x={lp.x}
                y={lp.y}
                textAnchor="middle"
                dominantBaseline="middle"
                fill={inactive ? "#475569" : "#cbd5e1"}
                fontSize="11"
                fontWeight={inactive ? 400 : 600}
              >
                {s.label}
              </text>
            );
          })}
        </svg>

        <div className="flex-1 w-full space-y-2.5">
          {stats.map((s) => (
            <EngineRow key={s.ai_model} stat={s} />
          ))}
          <p className="text-slate-600 text-xs pt-2 leading-relaxed">
            점선 축은 아직 추적하지 않는 엔진입니다. API 키를 등록하면 자동으로 포함됩니다.
          </p>
        </div>
      </div>
    </div>
  );
}

function EngineRow({ stat }: { stat: ModelStat }) {
  const state = stateOf(stat);
  const color = MODEL_COLOR[stat.ai_model] ?? FALLBACK_COLOR;

  return (
    <div className="flex items-center gap-3">
      <span
        className={`text-sm w-20 shrink-0 ${state === "measured" ? "text-slate-300" : "text-slate-600"}`}
      >
        {stat.label}
      </span>

      <div className="flex-1 bg-slate-800/60 rounded-full h-2 overflow-hidden">
        {state === "measured" && (
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{ width: `${stat.rate * 100}%`, backgroundColor: color }}
          />
        )}
      </div>

      <div className="w-24 shrink-0 text-right">
        {state === "unconfigured" && (
          <span className="text-slate-600 text-xs">미설정</span>
        )}
        {state === "not-run" && (
          <span className="text-amber-500/80 text-xs">미실행</span>
        )}
        {state === "measured" && (
          <span className="inline-flex items-baseline gap-1.5">
            <span className={`text-sm font-bold ${stat.rate > 0 ? "text-green-400" : "text-slate-600"}`}>
              {Math.round(stat.rate * 100)}%
            </span>
            {stat.avg_rank !== null && (
              <span className="text-slate-500 text-xs">{stat.avg_rank}위</span>
            )}
          </span>
        )}
      </div>
    </div>
  );
}
