"use client";

import { useState } from "react";

export default function ContactCTA({ reportUrl }: { reportUrl: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(reportUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 space-y-4">
      <div>
        <h3 className="text-white font-bold text-lg">직접 개선이 어려우신가요?</h3>
        <p className="text-slate-400 text-sm mt-1">
          전문가에게 맡기면 평균 2~4주 내에 AI 추천 등재가 시작됩니다.
        </p>
      </div>
      <div className="flex flex-wrap gap-3">
        <a
          href="mailto:hello@aivis.kr?subject=AIVIS 대행 문의"
          className="flex-1 min-w-36 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm text-center py-3 px-4 rounded-xl transition-colors"
        >
          이메일로 문의하기
        </a>
        <button
          onClick={handleCopy}
          className="flex-1 min-w-36 bg-slate-800 hover:bg-slate-700 text-white font-medium text-sm py-3 px-4 rounded-xl transition-colors"
        >
          {copied ? "✅ 복사됨!" : "결과 링크 복사"}
        </button>
      </div>
    </div>
  );
}
