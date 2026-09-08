import { notFound } from "next/navigation";
import { getProject, getDashboard, listQuestions } from "@/lib/monitor-api";
import MentionHeatmap from "@/components/monitor/MentionHeatmap";
import ModelRadar from "@/components/monitor/ModelRadar";
import RunButton from "@/components/monitor/RunButton";
import AddQuestionForm from "@/components/monitor/AddQuestionForm";

function mentionLabel(rate: number) {
  if (rate >= 0.7) return { text: "매우 높음", color: "text-green-400" };
  if (rate >= 0.4) return { text: "높음", color: "text-emerald-400" };
  if (rate >= 0.2) return { text: "보통", color: "text-amber-400" };
  if (rate > 0) return { text: "낮음", color: "text-orange-400" };
  return { text: "없음", color: "text-slate-500" };
}

export default async function MonitorDashboard({ params }: { params: { id: string } }) {
  const projectId = parseInt(params.id);
  if (isNaN(projectId)) return notFound();

  const [project, dashboard, questions] = await Promise.all([
    getProject(projectId).catch(() => null),
    getDashboard(projectId).catch(() => null),
    listQuestions(projectId).catch(() => []),
  ]);

  if (!project) return notFound();

  const label = mentionLabel(dashboard?.total_mention_rate ?? 0);
  const totalRuns = dashboard?.rows.flatMap((r) => r.runs).length ?? 0;
  const needsRun = totalRuns === 0;

  return (
    <div className="min-h-screen bg-slate-950 pt-20 pb-16 px-4">
      <div className="max-w-5xl mx-auto space-y-6">

        {/* 헤더 */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <a href="/audit" className="text-slate-500 hover:text-slate-300 text-sm transition-colors">← 새 진단</a>
              <span className="text-slate-700">·</span>
              <a href={`/audit?url=${encodeURIComponent(project.target_url)}`} className="text-indigo-400 hover:text-indigo-300 text-sm transition-colors">재진단</a>
            </div>
            <h1 className="text-2xl font-black text-white">{project.name}</h1>
            <p className="text-slate-500 text-sm font-mono mt-0.5">{project.target_url}</p>
          </div>
          <RunButton projectId={projectId} />
        </div>

        {/* 현황 요약 카드 */}
        <div className="grid grid-cols-3 gap-4">
          <SummaryCard
            label="브랜드 언급률"
            value={label.text}
            valueColor={label.color}
            sub={totalRuns > 0 ? `${totalRuns}회 실행 기준` : "아직 실행 없음"}
          />
          <SummaryCard
            label="전체 언급률"
            value={totalRuns > 0 ? `${Math.round((dashboard?.total_mention_rate ?? 0) * 100)}%` : "—"}
            valueColor="text-white"
            sub={`질문 ${questions.length}개`}
          />
          <SummaryCard
            label="모니터링 질문"
            value={`${questions.length}개`}
            valueColor="text-indigo-400"
            sub="활성 질문"
          />
        </div>

        {/* 질문 목록 + 히트맵 */}
        <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-white font-bold">모니터링 질문 목록 <span className="text-slate-500 font-normal text-sm">{questions.length}개</span></h2>
          </div>

          <AddQuestionForm projectId={projectId} />

          {needsRun ? (
            <div className="text-center py-10 space-y-3">
              <p className="text-slate-400">질문을 추가하고 모니터링을 실행하면</p>
              <p className="text-slate-400">AI가 내 브랜드를 언급하는지 추적합니다.</p>
            </div>
          ) : (
            <>
              <div className="space-y-1">
                <p className="text-slate-500 text-xs font-medium uppercase tracking-wide">모니터링 추이</p>
                <p className="text-slate-600 text-xs">초록: 언급됨 · 회색: 미언급 · 빈칸: 미실행</p>
              </div>
              <MentionHeatmap rows={dashboard?.rows ?? []} />
            </>
          )}
        </div>

        {/* AI 모델별 레이더 */}
        {!needsRun && dashboard && (
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6">
            <ModelRadar stats={dashboard.by_model ?? []} />
          </div>
        )}

        {/* 질문별 상세 언급률 */}
        {!needsRun && dashboard && dashboard.rows.length > 0 && (
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 space-y-4">
            <h3 className="text-white font-bold text-sm">질문별 언급률</h3>
            <div className="space-y-3">
              {dashboard.rows.map((row) => (
                <div key={row.question_id} className="flex items-center gap-4">
                  <p className="flex-1 text-slate-300 text-sm leading-snug">{row.question}</p>
                  <div className="shrink-0 flex items-center gap-2">
                    <div className="w-24 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                      <div
                        className="h-full bg-green-500 rounded-full transition-all"
                        style={{ width: `${row.mention_rate * 100}%` }}
                      />
                    </div>
                    <span className={`text-sm font-bold w-8 text-right ${row.mention_rate > 0 ? "text-green-400" : "text-slate-600"}`}>
                      {Math.round(row.mention_rate * 100)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function SummaryCard({
  label, value, valueColor, sub,
}: {
  label: string; value: string; valueColor: string; sub: string;
}) {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5 space-y-1">
      <p className="text-slate-500 text-xs">{label}</p>
      <p className={`text-xl font-black ${valueColor}`}>{value}</p>
      <p className="text-slate-600 text-xs">{sub}</p>
    </div>
  );
}
