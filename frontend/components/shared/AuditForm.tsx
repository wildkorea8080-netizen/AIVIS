"use client";

import { useState, useTransition } from "react";

interface AuditFormProps {
  action: (formData: FormData) => Promise<void>;
  compact?: boolean;
}

export default function AuditForm({ action, compact }: AuditFormProps) {
  const [mode, setMode] = useState<"brand" | "local">("brand");
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    const formData = new FormData(e.currentTarget);
    formData.set("mode", mode);
    startTransition(async () => {
      try {
        await action(formData);
      } catch (err: unknown) {
        // redirect()는 NEXT_REDIRECT 에러를 던지므로 무시
        if (err instanceof Error && err.message.includes("NEXT_REDIRECT")) return;
        setError(err instanceof Error ? err.message : "진단 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
      }
    });
  }

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-4">
      {/* 모드 토글 */}
      <div className="flex rounded-xl bg-slate-800 p-1 gap-1">
        {(["brand", "local"] as const).map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => setMode(m)}
            className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
              mode === m
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            {m === "brand" ? "🌐 온라인 브랜드" : "📍 오프라인 매장"}
          </button>
        ))}
      </div>

      {/* URL 입력 */}
      <div className={compact ? "" : "flex gap-3"}>
        <input
          name="url"
          type="url"
          required
          placeholder="https://yoursite.com"
          className="flex-1 w-full bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
        />
        {!compact && (
          <button
            type="submit"
            disabled={isPending}
            className="shrink-0 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white font-semibold rounded-xl px-6 py-3 transition-all flex items-center gap-2"
          >
            {isPending ? <Spinner /> : "AI 노출 진단하기 →"}
          </button>
        )}
      </div>

      {/* LOCAL 전용 필드 */}
      {mode === "local" && (
        <div className="grid grid-cols-2 gap-3">
          <input
            name="place_name"
            type="text"
            required
            placeholder="매장명 (예: 강남치과)"
            className="bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <input
            name="region"
            type="text"
            placeholder="지역 (예: 서울 강남구)"
            className="bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      )}

      {compact && (
        <button
          type="submit"
          disabled={isPending}
          className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white font-semibold rounded-xl py-3 px-6 transition-all flex items-center justify-center gap-2"
        >
          {isPending ? <><Spinner /> 분석 중...</> : "AI 노출 진단하기 →"}
        </button>
      )}

      {/* 에러 메시지 */}
      {error && (
        <div className="bg-red-950 border border-red-800 text-red-300 text-sm rounded-xl px-4 py-3">
          ⚠️ {error}
        </div>
      )}

      {/* 로딩 안내 */}
      {isPending && (
        <p className="text-slate-500 text-xs text-center animate-pulse">
          AI 신호를 수집하는 중입니다... 최대 30초 소요될 수 있습니다.
        </p>
      )}
    </form>
  );
}

function Spinner() {
  return (
    <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
  );
}
