import { notFound } from "next/navigation";
import { getProject } from "@/lib/monitor-api";
import UnsubscribeForm from "@/components/monitor/UnsubscribeForm";

export const dynamic = "force-dynamic";

export default async function UnsubscribePage({ params }: { params: { token: string } }) {
  const project = await getProject(params.token).catch(() => null);
  if (!project) return notFound();

  return (
    <div className="min-h-screen bg-slate-950 pt-32 px-4">
      <div className="max-w-md mx-auto text-center space-y-5">
        <h1 className="text-xl font-bold text-white">주간 리포트 수신 해지</h1>
        <p className="text-slate-400 text-sm leading-relaxed">
          <span className="text-slate-200">{project.name}</span> 프로젝트의 주간 리포트를
          더 이상 받지 않습니다. 모니터링 자체는 계속되며, 대시보드에서 언제든 확인할 수 있습니다.
        </p>
        <UnsubscribeForm token={params.token} />
      </div>
    </div>
  );
}
