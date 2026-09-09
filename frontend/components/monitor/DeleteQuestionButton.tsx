"use client";

import { useState, useTransition } from "react";
import { deleteQuestionAction } from "@/app/monitor/actions";

export default function DeleteQuestionButton({
  projectId,
  questionId,
}: {
  projectId: number;
  questionId: number;
}) {
  const [isPending, startTransition] = useTransition();
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleDelete() {
    setError(null);
    startTransition(async () => {
      try {
        await deleteQuestionAction(projectId, questionId);
      } catch (err: unknown) {
        if (err instanceof Error && err.message.includes("NEXT_REDIRECT")) return;
        setError(err instanceof Error ? err.message : "삭제에 실패했습니다.");
        setConfirming(false);
      }
    });
  }

  if (error) {
    return <span className="text-red-400 text-xs shrink-0">⚠️ {error}</span>;
  }

  if (!confirming) {
    return (
      <button
        onClick={() => setConfirming(true)}
        className="text-slate-600 hover:text-red-400 text-xs shrink-0 transition-colors"
        aria-label="질문 삭제"
      >
        삭제
      </button>
    );
  }

  return (
    <span className="flex items-center gap-2 shrink-0">
      <button
        onClick={handleDelete}
        disabled={isPending}
        className="text-red-400 hover:text-red-300 disabled:opacity-50 text-xs font-semibold"
      >
        {isPending ? "삭제 중..." : "삭제 확인"}
      </button>
      <button
        onClick={() => setConfirming(false)}
        className="text-slate-500 hover:text-slate-300 text-xs"
      >
        취소
      </button>
    </span>
  );
}
