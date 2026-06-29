"use client";

import { useSearchParams } from "next/navigation";
import { useMemo } from "react";
import { decodeReport } from "@/lib/report-codec";
import ScoreGauge from "@/components/report/ScoreGauge";
import FindingCard from "@/components/report/FindingCard";
import ContactCTA from "@/components/report/ContactCTA";
import type { ReadinessReport } from "@/lib/types";

function scoreLabel(score: number): { text: string; color: string } {
  if (score >= 70) return { text: "높음", color: "text-green-400" };
  if (score >= 40) return { text: "보통", color: "text-amber-400" };
  return { text: "낮음", color: "text-red-400" };
}

function improveTips(findings: ReadinessReport["findings"]): string[] {
  const tips: Record<string, string> = {
    l_schema: "사이트에 LocalBusiness JSON-LD 스키마를 추가하세요",
    l_llms: "웹사이트 루트에 /llms.txt 파일을 생성하세요",
    l_place: "카카오맵·네이버 지도에 매장을 등록하고 정보를 최신화하세요",
    l_comm: "네이버 블로그·카카오 채널에 매장 소개 콘텐츠를 발행하세요",
    b_bots: "robots.txt에서 GPTBot·ClaudeBot 차단을 해제하세요",
    b_org: "사이트에 Organization JSON-LD 스키마를 추가하세요",
    b_faq: "FAQ 페이지에 FAQPage 스키마 마크업을 추가하세요",
    b_llms: "웹사이트 루트에 /llms.txt 파일을 생성하세요",
    b_comm: "외부 미디어·블로그에 브랜드 언급 콘텐츠를 확대하세요",
  };
  return findings
    .filter((f) => f.state === "no" || f.state === "partial")
    .slice(0, 5)
    .map((f) => tips[f.item_id] ?? `${f.label} 항목을 개선하세요`);
}

export default function ReportContent() {
  const params = useSearchParams();
  const encoded = params.get("d");

  const report = useMemo<ReadinessReport | null>(() => {
    if (!encoded) return null;
    try {
      return decodeReport(encoded);
    } catch {
      return null;
    }
  }, [encoded]);

  if (!report) {
    return (
      <div className="max-w-2xl mx-auto text-center py-20">
        <p className="text-slate-400 text-lg">리포트 데이터를 찾을 수 없습니다.</p>
        <a href="/audit" className="mt-6 inline-block bg-indigo-600 text-white px-6 py-3 rounded-xl">
          다시 진단하기
        </a>
      </div>
    );
  }

  const { target_url, place_name, mode, score, findings, generated_at } = report;
  const reportUrl = typeof window !== "undefined" ? window.location.href : "";
  const date = new Date(generated_at).toLocaleString("ko-KR");
  const sl = scoreLabel(score);
  const tips = improveTips(findings);

  const activeFindings = findings.filter((f) => f.state !== "unknown");
  const unknownFindings = findings.filter((f) => f.state === "unknown");

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      {/* 헤더 */}
      <div className="text-center space-y-2">
        <p className="text-slate-500 text-sm">{date} 기준</p>
        <h1 className="text-2xl font-bold text-white">AI 노출 준비도 리포트</h1>
        <p className="text-indigo-400 text-sm font-mono break-all">{target_url}</p>
        {place_name && (
          <p className="text-slate-400 text-sm">
            {place_name} · {mode === "local" ? "오프라인 매장" : "온라인 브랜드"}
          </p>
        )}
      </div>

      {/* 점수 게이지 */}
      <div className="bg-slate-900 border border-slate-700 rounded-2xl p-8 flex flex-col items-center gap-4">
        <ScoreGauge score={score} />
        <p className="text-slate-400 text-sm text-center max-w-sm">
          각 항목을 개선하면 ChatGPT·Perplexity·Gemini의 추천 답변에 등장할 확률이 높아집니다.
        </p>
      </div>

      {/* 현황 분석 요약 */}
      <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 space-y-5">
        <h2 className="text-white font-bold text-base">현황 분석</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-slate-800 rounded-xl p-4 text-center">
            <p className="text-slate-500 text-xs mb-1">AI 노출 준비도</p>
            <p className={`font-black text-lg ${sl.color}`}>{sl.text}</p>
          </div>
          <div className="bg-slate-800 rounded-xl p-4 text-center">
            <p className="text-slate-500 text-xs mb-1">종합 기회 점수</p>
            <p className="font-black text-lg text-white">{score}점</p>
          </div>
          <div className="bg-slate-800 rounded-xl p-4 text-center">
            <p className="text-slate-500 text-xs mb-1">개선 필요 항목</p>
            <p className="font-black text-lg text-amber-400">
              {findings.filter((f) => f.state === "no" || f.state === "partial").length}개
            </p>
          </div>
        </div>

        {tips.length > 0 && (
          <div className="space-y-2">
            <p className="text-slate-400 text-xs font-medium uppercase tracking-wide">최적화 전략 방향성</p>
            <ul className="space-y-2">
              {tips.map((tip, i) => (
                <li key={i} className="flex items-start gap-2 text-slate-300 text-sm">
                  <span className="text-indigo-400 mt-0.5 shrink-0">→</span>
                  {tip}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Finding 카드 목록 */}
      <div className="space-y-3">
        <h2 className="text-white font-bold text-lg">항목별 진단 결과</h2>
        {activeFindings.map((f) => (
          <FindingCard key={f.item_id} finding={f} />
        ))}
        {unknownFindings.length > 0 && (
          <details className="text-slate-500 text-sm cursor-pointer">
            <summary className="hover:text-slate-300 transition-colors py-2">
              확인 불가 항목 {unknownFindings.length}개 (Milestone 2에서 추가 예정)
            </summary>
            <div className="mt-2 space-y-2">
              {unknownFindings.map((f) => (
                <FindingCard key={f.item_id} finding={f} />
              ))}
            </div>
          </details>
        )}
      </div>

      {/* CTA */}
      <ContactCTA reportUrl={reportUrl} />

      <div className="text-center">
        <a href="/audit" className="text-indigo-400 hover:text-indigo-300 text-sm transition-colors">
          다른 사이트 진단하기 →
        </a>
      </div>
    </div>
  );
}
