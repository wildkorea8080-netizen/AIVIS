"use client";

import { useTransition, useRef } from "react";
import { addQuestionAction } from "@/app/monitor/actions";

export default function AddQuestionForm({ projectId }: { projectId: number }) {
  const [isPending, startTransition] = useTransition();
  const ref = useRef<HTMLFormElement>(null);

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    startTransition(async () => {
      await addQuestionAction(projectId, formData);
      ref.current?.reset();
    });
  }

  return (
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
  );
}
