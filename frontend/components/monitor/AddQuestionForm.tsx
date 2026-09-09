"use client";

import { useState, useTransition, useRef } from "react";
import { addQuestionAction } from "@/app/monitor/actions";

export default function AddQuestionForm({ projectId }: { projectId: number }) {
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const ref = useRef<HTMLFormElement>(null);

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    setError(null);
    startTransition(async () => {
      try {
        await addQuestionAction(projectId, formData);
        ref.current?.reset();
      } catch (err: unknown) {
        // 성공 시 redirect()가 NEXT_REDIRECT를 던지므로 오류로 취급하면 안 된다
        if (err instanceof Error && err.message.includes("NEXT_REDIRECT")) return;
        setError(err instanceof Error ? err.message : "질문 추가에 실패했습니다.");
      }
    });
  }

  return (
    <div className="space-y-2">
    <form ref={ref} onSubmit={handleSubmit} className="flex gap-2">
      <input
        name="question"
        type="text"
        required
        placeholder="예: 강남 임플란트 잘하는 치과 추천해줘"
        className="flex-1 bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />
      <button
        type="submit"
        disabled={isPending}
        className="shrink-0 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-white text-sm font-medium rounded-xl px-4 py-2.5 transition-all"
      >
        {isPending ? "추가 중..." : "+ 추가"}
      </button>
    </form>
      {error && <p className="text-red-400 text-xs">⚠️ {error}</p>}
    </div>
  );
}
