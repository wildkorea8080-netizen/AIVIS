"use client";

import Link from "next/link";
import { useState, useTransition } from "react";
import { unsubscribeAction } from "@/app/monitor/actions";

export default function UnsubscribeForm({ token }: { token: string }) {
  const [isPending, startTransition] = useTransition();
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 확인 버튼을 거치는 이유: 메일 클라이언트가 링크를 선제적으로 GET 한다.
  // 링크를 여는 것만으로 해지되면 열어보지도 않은 사용자가 조용히 해지된다.
  function handleClick() {
    setError(null);
    startTransition(async () => {
      try {
        await unsubscribeAction(token);
        setDone(true);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "해지에 실패했습니다.");
      }
    });
  }

  if (done) {
    return (
      <div className="space-y-4">
        <p className="text-green-400 text-sm">수신이 해지됐습니다.</p>
        <Link
          href={`/monitor/${token}`}
          className="inline-block bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm rounded-xl px-5 py-2.5"
        >
          대시보드로 가기
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <button
        onClick={handleClick}
        disabled={isPending}
        className="bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl px-6 py-3"
      >
        {isPending ? "처리 중..." : "수신 해지하기"}
      </button>
      {error && <p className="text-red-400 text-xs">⚠️ {error}</p>}
      <p>
        <Link href={`/monitor/${token}`} className="text-slate-500 hover:text-slate-300 text-xs">
          계속 받을래요 — 대시보드로 돌아가기
        </Link>
      </p>
    </div>
  );
}
