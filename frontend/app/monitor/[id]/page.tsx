import { notFound } from "next/navigation";
import { getProject, getDashboard, listQuestions } from "@/lib/monitor-api";
import MentionHeatmap from "@/components/monitor/MentionHeatmap";
import ModelRadar from "@/components/monitor/ModelRadar";
import ShareOfVoice from "@/components/monitor/ShareOfVoice";
import RunButton from "@/components/monitor/RunButton";
import AddQuestionForm from "@/components/monitor/AddQuestionForm";
import DeleteQuestionButton from "@/components/monitor/DeleteQuestionButton";
import DeleteProjectButton from "@/components/monitor/DeleteProjectButton";

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

  // 서버에 닿지 못한 경우와 프로젝트가 없는 경우를 구분한다.
  // 둘을 뭉뚱그리면 백엔드가 잠들었을 뿐인데 "없는 프로젝트"라고 알리게 된다.
  const [projectResult, dashboard, questions] = await Promise.all([
    getProject(projectId).then(
      (project) => ({ reachable: true as const, project }),
      () => ({ reachable: false as const, project: null }),
    ),
    getDashboard(projectId).catch(() => null),
    listQuestions(projectId).catch(() => []),
  ]);

  if (!projectResult.reachable) return <ServerUnreachable />;
  const project = projectResult.project;
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
            <div className="mt-2">
              <DeleteProjectButton projectId={projectId} projectName={project.name} />
            </div>
          </div>
          <RunButton projectId={projectId} questionCount={questions.length} />
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

          {/* 등록된 질문은 실행 전에도 보여준다. 개수만 바뀌면 저장이 안 된 것처럼 보인다. */}
          {questions.length > 0 && (
            <ul className="space-y-2">
              {questions.map((q, idx) => (
                <li
                  key={q.id}
                  className="flex items-start gap-3 bg-slate-800/50 border border-slate-700/60 rounded-xl px-4 py-3"
                >
                  <span className="text-slate-600 text-xs font-mono shrink-0 mt-0.5">
                    Q{idx + 1}
                  </span>
                  <span className="flex-1 text-slate-300 text-sm leading-snug">{q.question}</span>
                  <DeleteQuestionButton projectId={projectId} questionId={q.id} />
                </li>
              ))}
            </ul>
          )}

          {questions.length === 0 ? (
            <div className="text-center py-10 space-y-3">
              <p className="text-slate-400">고객이 AI에게 물어볼 만한 질문을 추가하세요.</p>
              <p className="text-slate-500 text-sm">예: 감성 캠핑용 우드 스툴 만드는 국내 브랜드 알려줘</p>
            </div>
          ) : needsRun ? (
            <div className="text-center py-8 space-y-2">
              <p className="text-slate-300">질문 {questions.length}개가 등록됐습니다.</p>
              <p className="text-slate-500 text-sm">
                위 <span className="text-indigo-400">▶ 지금 모니터링 실행</span>을 누르면 AI에 질문을 던져 추적을 시작합니다.
              </p>
            </div>
          ) : (
            <>
              <div className="space-y-1">
                <p className="text-slate-500 text-xs font-medium uppercase tracking-wide">모니터링 추이</p>
                <p className="text-slate-600 text-xs">초록: 언급됨 · 회색: 미언급 · 빈칸: 미실행</p>
              </div>
              <MentionHeatmap rows={dashboard?.rows ?? []} engines={dashboard?.by_model ?? []} />
            </>
          )}
        </div>

        {/* AI 모델별 레이더 */}
        {!needsRun && dashboard && (
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6">
            <ModelRadar stats={dashboard.by_model ?? []} />
          </div>
        )}

        {/* 경쟁 현황 */}
        {!needsRun && dashboard && (
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6">
            <ShareOfVoice
              stats={dashboard.share_of_voice ?? []}
              brandKeyword={project.brand_keyword}
            />
          </div>
        )}

        {/* 질문별 상세 언급률 */}
        {!needsRun && dashboard && dashboard.rows.length > 0 && (
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 space-y-4">
            <h3 className="text-white font-bold text-sm">질문별 언급률</h3>
            <div className="space-y-3">
              {dashboard.rows.map((row) => (
                <div key={row.question_id} className="space-y-2">
                  <div className="flex items-center gap-4">
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

                  {row.competitors.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      <span className="text-slate-600 text-xs self-center">이 질문의 추천 업체:</span>
                      {row.competitors.slice(0, 6).map((c) => (
                        <span
                          key={c.name_key}
                          title={`${c.mentions}회 추천${c.avg_rank !== null ? ` · 평균 ${c.avg_rank}위` : ""}`}
                          className={`text-xs px-2 py-0.5 rounded-md ${
                            c.is_own
                              ? "bg-indigo-600/25 text-indigo-300 font-semibold"
                              : "bg-slate-800 text-slate-400"
                          }`}
                        >
                          {c.name}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ServerUnreachable() {
  return (
    <div className="min-h-screen bg-slate-950 pt-32 px-4">
      <div className="max-w-md mx-auto text-center space-y-4">
        <h1 className="text-xl font-bold text-white">서버를 깨우는 중입니다</h1>
        <p className="text-slate-400 text-sm leading-relaxed">
          한동안 사용이 없으면 서버가 절전 상태로 들어갑니다. 깨어나는 데 1분 정도
          걸릴 수 있으니 잠시 후 새로고침해 주세요.
        </p>
        <p className="text-slate-600 text-xs">
          계속 같은 화면이 보이면 서버가 내려간 상태일 수 있습니다.
        </p>
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
