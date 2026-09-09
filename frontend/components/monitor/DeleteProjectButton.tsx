"use client";

import { useState, useTransition } from "react";
import { deleteProjectAction } from "@/app/monitor/actions";

export default function DeleteProjectButton({
  projectId,
  projectName,
}: {
  projectId: number;
  projectName: string;
}) {
  const [isPending, startTransition] = useTransition();
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleDelete() {
    setError(null);
    startTransition(async () => {
      try {
        await deleteProjectAction(projectId);
      } catch (err: unknown) {
        if (err instanceof Error && err.message.includes("NEXT_REDIRECT")) return;
        setError(err instanceof Error ? err.message : "삭제에 실패했습니다.");
        setConfirming(false);
      }
    });
  }

  if (!confirming) {
    return (
      <button
        onClick={() => setConfirming(true)}
        className="text-slate-600 hover:text-red-400 text-xs transition-colors"
      >
        프로젝트 삭제
      </button>
    );
  }

  return (
    <div className="flex flex-col items-start gap-1">
      <p className="text-slate-400 text-xs">
        &ldquo;{projectName}&rdquo;의 질문과 실행 이력이 모두 삭제됩니다. 되돌릴 수 없습니다.
      </p>
      <div className="flex items-center gap-3">
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
      </div>
      {error && <p className="text-red-400 text-xs">⚠️ {error}</p>}
    </div>
  );
}
