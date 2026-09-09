"use client";

import { useState, useTransition } from "react";
import { runMonitorAction } from "@/app/monitor/actions";

interface Props {
  projectId: number;
  questionCount: number;
}

export default function RunButton({ projectId, questionCount }: Props) {
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);

  // 질문이 없으면 백엔드가 400을 준다. 누르고 실패하게 두는 대신 미리 막는다.
  const noQuestions = questionCount === 0;

  function handleClick() {
    setError(null);
    startTransition(async () => {
      try {
        await runMonitorAction(projectId);
      } catch (err: unknown) {
        // 성공 시 redirect()가 NEXT_REDIRECT를 던지므로 오류로 취급하면 안 된다
        if (err instanceof Error && err.message.includes("NEXT_REDIRECT")) return;
        setError(err instanceof Error ? err.message : "모니터링 실행에 실패했습니다.");
      }
    });
  }

  return (
    <div className="flex flex-col items-start sm:items-end gap-1.5">
      <button
        onClick={handleClick}
        disabled={isPending || noQuestions}
        className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:hover:bg-indigo-600 disabled:cursor-not-allowed text-white font-semibold rounded-xl px-5 py-2.5 text-sm transition-all"
      >
        {isPending ? (
          <>
            <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            AI에 질문 중... (30초 내외)
          </>
        ) : (
          <>▶ 지금 모니터링 실행</>
        )}
      </button>

      {noQuestions && (
        <p className="text-slate-500 text-xs">아래에서 질문을 먼저 추가하세요</p>
      )}

      {error && (
        <p className="text-red-400 text-xs max-w-xs sm:text-right">⚠️ {error}</p>
      )}
    </div>
  );
}
