"use client";

import { useTransition } from "react";
import { runMonitorAction } from "@/app/monitor/actions";

export default function RunButton({ projectId }: { projectId: number }) {
  const [isPending, startTransition] = useTransition();

  function handleClick() {
    startTransition(async () => {
      await runMonitorAction(projectId);
    });
  }

  return (
    <button
      onClick={handleClick}
      disabled={isPending}
      className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white font-semibold rounded-xl px-5 py-2.5 text-sm transition-all"
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
  );
}
