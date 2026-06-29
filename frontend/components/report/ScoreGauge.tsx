"use client";

import { useEffect, useState } from "react";

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

export default function ScoreGauge({ score }: { score: number }) {
  const [displayed, setDisplayed] = useState(0);

  useEffect(() => {
    let start: number | null = null;
    const duration = 1000;
    function step(ts: number) {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      setDisplayed(Math.round(progress * score));
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }, [score]);

  const { stroke, text, label } = scoreColor(score);
  const offset = CIRCUMFERENCE - (displayed / 100) * CIRCUMFERENCE;

  return (
    <div className="flex flex-col items-center">
      <svg width={SIZE} height={SIZE / 2 + STROKE} viewBox={`0 0 ${SIZE} ${SIZE / 2 + STROKE}`}>
        {/* 배경 반원 */}
        <path
          d={`M ${STROKE / 2} ${CENTER} A ${R} ${R} 0 0 1 ${SIZE - STROKE / 2} ${CENTER}`}
          fill="none"
          stroke="#1e293b"
          strokeWidth={STROKE}
          strokeLinecap="round"
        />
        {/* 점수 반원 */}
        <path
          d={`M ${STROKE / 2} ${CENTER} A ${R} ${R} 0 0 1 ${SIZE - STROKE / 2} ${CENTER}`}
          fill="none"
          stroke={stroke}
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 0.05s linear" }}
        />
      </svg>
      <div className="-mt-2 text-center">
        <div className={`text-6xl font-black ${text}`}>{displayed}</div>
        <div className="text-slate-400 text-sm mt-1">/ 100점 · {label}</div>
      </div>
    </div>
  );
}
