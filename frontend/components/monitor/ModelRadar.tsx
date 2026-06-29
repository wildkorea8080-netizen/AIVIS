"use client";

import type { DashboardRow } from "@/lib/types";

const MODELS = ["chatgpt", "claude", "perplexity", "gemini", "grok"];
const MODEL_LABEL: Record<string, string> = {
  chatgpt: "ChatGPT", claude: "Claude", perplexity: "Perplexity", gemini: "Gemini", grok: "Grok",
};
const MODEL_COLOR: Record<string, string> = {
  chatgpt: "#10b981", claude: "#f59e0b", perplexity: "#6366f1", gemini: "#3b82f6", grok: "#ec4899",
};

interface Props {
  rows: DashboardRow[];
}

function calcModelRate(rows: DashboardRow[], model: string): number {
  const runs = rows.flatMap((r) => r.runs.filter((run) => run.ai_model === model));
  if (!runs.length) return 0;
  return runs.filter((r) => r.mentioned).length / runs.length;
}

export default function ModelRadar({ rows }: Props) {
  const rates = MODELS.map((m) => ({ model: m, rate: calcModelRate(rows, m) }));
  const hasData = rates.some((r) => r.rate > 0);

  // SVG 레이더 차트 (5각형)
  const cx = 120, cy = 120, r = 90;
  const angles = MODELS.map((_, i) => (i * 2 * Math.PI) / MODELS.length - Math.PI / 2);

  function point(rate: number, i: number) {
    const a = angles[i];
    const d = r * rate;
    return { x: cx + d * Math.cos(a), y: cy + d * Math.sin(a) };
  }

  function bgPoint(scale: number, i: number) {
    const a = angles[i];
    return { x: cx + r * scale * Math.cos(a), y: cy + r * scale * Math.sin(a) };
  }

  const dataPoints = rates.map((r, i) => point(r.rate, i));
  const dataPath = dataPoints.map((p, i) => `${i === 0 ? "M" : "L"}${p.x},${p.y}`).join(" ") + " Z";

  return (
    <div className="space-y-4">
      <h3 className="text-slate-300 text-sm font-medium">AI 모델별 언급률</h3>
      <div className="flex flex-col sm:flex-row items-center gap-6">
        {/* 레이더 SVG */}
        <svg width="240" height="240" viewBox="0 0 240 240" className="shrink-0">
          {/* 배경 격자 */}
          {[0.25, 0.5, 0.75, 1].map((scale) => {
            const pts = MODELS.map((_, i) => bgPoint(scale, i));
            const path = pts.map((p, i) => `${i === 0 ? "M" : "L"}${p.x},${p.y}`).join(" ") + " Z";
            return <path key={scale} d={path} fill="none" stroke="#334155" strokeWidth="1" />;
          })}
          {/* 축 선 */}
          {MODELS.map((_, i) => {
            const end = bgPoint(1, i);
            return <line key={i} x1={cx} y1={cy} x2={end.x} y2={end.y} stroke="#334155" strokeWidth="1" />;
          })}
          {/* 데이터 영역 */}
          {hasData && (
            <path d={dataPath} fill="#6366f1" fillOpacity="0.3" stroke="#6366f1" strokeWidth="2" />
          )}
          {/* 데이터 점 */}
          {hasData && dataPoints.map((p, i) => (
            <circle key={i} cx={p.x} cy={p.y} r="4" fill={MODEL_COLOR[MODELS[i]]} />
          ))}
          {/* 레이블 */}
          {MODELS.map((m, i) => {
            const lp = bgPoint(1.18, i);
            return (
              <text key={m} x={lp.x} y={lp.y} textAnchor="middle" dominantBaseline="middle"
                fill="#94a3b8" fontSize="10">
                {MODEL_LABEL[m]}
              </text>
            );
          })}
        </svg>

        {/* 모델별 수치 테이블 */}
        <div className="flex-1 w-full space-y-2">
          {rates.map(({ model, rate }) => (
            <div key={model} className="flex items-center gap-3">
              <span className="text-slate-400 text-sm w-24 shrink-0">{MODEL_LABEL[model]}</span>
              <div className="flex-1 bg-slate-800 rounded-full h-2 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{ width: `${rate * 100}%`, backgroundColor: MODEL_COLOR[model] }}
                />
              </div>
              <span className={`text-sm font-bold w-10 text-right ${rate > 0 ? "text-green-400" : "text-slate-600"}`}>
                {rate > 0 ? `${Math.round(rate * 100)}%` : "—"}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
