"use client";

import { useState, useTransition } from "react";

interface AuditFormProps {
  action: (formData: FormData) => Promise<void>;
  compact?: boolean;
}

const INDUSTRY_EXAMPLES: Record<string, { label: string; place: string; region: string }> = {
  "병원·치과":  { label: "병원·치과",  place: "강남 이루다치과",  region: "서울 강남구" },
  "법률·세무":  { label: "법률·세무",  place: "김변호사 법률사무소", region: "서울 서초구" },
  "식당·카페":  { label: "식당·카페",  place: "홍대 브런치카페",  region: "서울 마포구" },
  "뷰티·헬스":  { label: "뷰티·헬스",  place: "압구정 피부관리실", region: "서울 강남구" },
};

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
        if (err instanceof Error && err.message.includes("NEXT_REDIRECT")) return;
        setError(err instanceof Error ? err.message : "진단 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
      }
    });
  }

  function applyExample(key: string) {
    const ex = INDUSTRY_EXAMPLES[key];
    if (!ex) return;
    const form = document.querySelector("form") as HTMLFormElement;
    if (!form) return;
    (form.elements.namedItem("place_name") as HTMLInputElement).value = ex.place;
    (form.elements.namedItem("region") as HTMLInputElement).value = ex.region;
  }

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-4">
      {/* 모드 토글 */}
      <div className="flex rounded-xl bg-slate-800/80 p-1 gap-1">
        {(["brand", "local"] as const).map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => setMode(m)}
            className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all ${
              mode === m
                ? "bg-indigo-600 text-white shadow"
                : "text-slate-400 hover:text-white"
            }`}
          >
            {m === "brand" ? "🌐 온라인 브랜드" : "📍 오프라인 매장"}
          </button>
        ))}
      </div>

      {/* BRAND 모드 */}
      {mode === "brand" && (
        <div className={compact ? "space-y-3" : "flex gap-3"}>
          <input
            name="url"
            type="url"
            required
            placeholder="https://yoursite.com"
            className="flex-1 w-full bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
          />
          {!compact && (
            <SubmitButton isPending={isPending} />
          )}
        </div>
      )}

      {/* LOCAL 모드 */}
      {mode === "local" && (
        <div className="space-y-3">
          {/* 업종 빠른 입력 */}
          {!compact && (
            <div className="flex gap-2 flex-wrap">
              <span className="text-slate-500 text-xs self-center">예시:</span>
              {Object.keys(INDUSTRY_EXAMPLES).map((key) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => applyExample(key)}
                  className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg transition-all"
                >
                  {key}
                </button>
              ))}
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <input
              name="place_name"
              type="text"
              required
              placeholder="매장명 (예: 강남치과)"
              className="bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 col-span-2 sm:col-span-1"
            />
            <input
              name="region"
              type="text"
              placeholder="지역 (예: 서울 강남구)"
              className="bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 col-span-2 sm:col-span-1"
            />
          </div>

          <div className="relative">
            <input
              name="url"
              type="url"
              placeholder="홈페이지 URL (선택사항)"
              className="w-full bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 pr-20"
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-600 text-xs">선택</span>
          </div>
        </div>
      )}

      {/* compact 버튼 또는 non-compact LOCAL 버튼 */}
      {(compact || mode === "local") && (
        <SubmitButton isPending={isPending} compact={compact} />
      )}

      {error && (
        <div className="bg-red-950 border border-red-800 text-red-300 text-sm rounded-xl px-4 py-3">
          ⚠️ {error}
        </div>
      )}

      {isPending && (
        <p className="text-slate-500 text-xs text-center animate-pulse">
          AI 신호를 수집하는 중입니다... 첫 요청은 서버가 깨어나느라 1분까지 걸릴 수 있습니다.
        </p>
      )}
    </form>
  );
}

function SubmitButton({ isPending, compact }: { isPending: boolean; compact?: boolean }) {
  return (
    <button
      type="submit"
      disabled={isPending}
      className={`${compact ? "w-full" : "w-full sm:w-auto"} bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white font-semibold rounded-xl py-3 px-6 transition-all flex items-center justify-center gap-2`}
    >
      {isPending ? (
        <>
          <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          분석 중...
        </>
      ) : (
        "AI 노출 진단하기 →"
      )}
    </button>
  );
}
