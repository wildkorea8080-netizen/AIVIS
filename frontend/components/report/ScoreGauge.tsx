const SIZE = 200;
const STROKE = 18;
const R = (SIZE - STROKE) / 2;
const CIRCUMFERENCE = Math.PI * R; // 반원
const CENTER = SIZE / 2;

function scoreColor(score: number) {
  if (score < 40) return { stroke: "#ef4444", text: "text-red-400", label: "위험" };
  if (score < 70) return { stroke: "#f59e0b", text: "text-amber-400", label: "개선 필요" };
  if (score < 90) return { stroke: "#6366f1", text: "text-indigo-400", label: "양호" };
  return { stroke: "#22c55e", text: "text-green-400", label: "우수" };
}

/**
 * 점수는 애니메이션 없이 바로 렌더한다.
 * 이전에는 requestAnimationFrame으로 0부터 세어 올렸는데, 백그라운드 탭처럼
 * rAF가 멈추는 상황에서 화면에 0이 남아 실제 점수와 다른 값이 보였다.
 * 그려지는 효과는 CSS 애니메이션으로 옮겼다 — 끝난 뒤 요소 본래의 offset에
 * 머무르므로, 애니메이션이 실행되지 않아도 호(arc)는 올바른 위치에 있다.
 */
export default function ScoreGauge({ score }: { score: number }) {
  const { stroke, text, label } = scoreColor(score);
  const offset = CIRCUMFERENCE - (score / 100) * CIRCUMFERENCE;
  const arc = `M ${STROKE / 2} ${CENTER} A ${R} ${R} 0 0 1 ${SIZE - STROKE / 2} ${CENTER}`;

  return (
    <div className="flex flex-col items-center">
      <style>{`
        @keyframes aivis-gauge-draw {
          from { stroke-dashoffset: ${CIRCUMFERENCE}; }
        }
        .aivis-gauge-arc { animation: aivis-gauge-draw 1s ease-out; }
        @media (prefers-reduced-motion: reduce) {
          .aivis-gauge-arc { animation: none; }
        }
      `}</style>

      <svg width={SIZE} height={SIZE / 2 + STROKE} viewBox={`0 0 ${SIZE} ${SIZE / 2 + STROKE}`}>
        {/* 배경 반원 */}
        <path d={arc} fill="none" stroke="#1e293b" strokeWidth={STROKE} strokeLinecap="round" />
        {/* 점수 반원 */}
        <path
          className="aivis-gauge-arc"
          d={arc}
          fill="none"
          stroke={stroke}
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={offset}
        />
      </svg>

      <div className="-mt-2 text-center">
        <div className={`text-6xl font-black ${text}`}>{score}</div>
        <div className="text-slate-400 text-sm mt-1">/ 100점 · {label}</div>
      </div>
    </div>
  );
}
