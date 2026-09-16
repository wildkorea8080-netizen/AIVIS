import Link from "next/link";
import { lookupProjects } from "@/lib/monitor-api";
import { readProjectTokens } from "@/lib/project-cookie";

export const dynamic = "force-dynamic";

function formatDate(iso: string | null) {
  if (!iso) return "아직 실행 안 함";
  return new Date(iso).toISOString().slice(0, 10);
}

export default async function MonitorHome() {
  const tokens = readProjectTokens();
  const projects = await lookupProjects(tokens).catch(() => null);

  return (
    <div className="min-h-screen bg-slate-950 pt-24 pb-16 px-4">
      <div className="max-w-3xl mx-auto space-y-8">
        <div className="flex items-end justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black text-white">내 모니터링 프로젝트</h1>
            <p className="text-slate-500 text-sm mt-1">
              이 브라우저에서 만든 프로젝트입니다. 대시보드 주소를 북마크해두면 다른 기기에서도 열 수 있습니다.
            </p>
          </div>
          <Link
            href="/monitor/new"
            className="shrink-0 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl px-5 py-2.5 text-sm"
          >
            + 새 프로젝트
          </Link>
        </div>

        {projects === null ? (
          <p className="text-slate-400 text-sm">
            서버를 깨우는 중입니다. 잠시 후 새로고침해 주세요.
          </p>
        ) : projects.length === 0 ? (
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-10 text-center space-y-3">
            <p className="text-slate-300">아직 프로젝트가 없습니다.</p>
            <p className="text-slate-500 text-sm">
              질문을 등록하면 AI가 내 브랜드를 실제로 추천하는지 매일 추적합니다.
            </p>
          </div>
        ) : (
          <ul className="space-y-3">
            {projects.map((p) => (
              <li key={p.owner_token}>
                <Link
                  href={`/monitor/${p.owner_token}`}
                  className="block bg-slate-900 border border-slate-700 hover:border-indigo-500 rounded-2xl p-5 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0">
                      <p className="text-white font-bold truncate">{p.name}</p>
                      <p className="text-slate-500 text-xs font-mono truncate mt-0.5">{p.target_url}</p>
                    </div>
                    <span className="text-indigo-400 text-sm shrink-0">열기 →</span>
                  </div>
                  <div className="flex gap-4 mt-3 text-xs text-slate-500">
                    <span>키워드 {p.brand_keyword}</span>
                    <span>질문 {p.question_count}개</span>
                    <span>마지막 실행 {formatDate(p.last_run_at)}</span>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
