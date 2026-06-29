import { createProjectAction } from "@/app/monitor/actions";

export default function NewMonitorPage() {
  return (
    <div className="min-h-screen bg-slate-950 pt-24 px-4">
      <div className="max-w-lg mx-auto space-y-8">
        <div className="space-y-2">
          <h1 className="text-3xl font-black text-white">모니터링 프로젝트 생성</h1>
          <p className="text-slate-400">AI가 내 브랜드를 언급하는지 매주 추적합니다.</p>
        </div>

        <form action={createProjectAction} className="space-y-4">
          <Field label="프로젝트명" name="name" placeholder="예: 강남 이루다치과" required />
          <Field label="웹사이트 URL" name="target_url" type="url" placeholder="https://yoursite.com" required />
          <Field label="브랜드 키워드" name="brand_keyword" placeholder="예: 이루다치과 (AI 응답에서 찾을 단어)" required />

          <div className="space-y-1.5">
            <label className="text-slate-300 text-sm font-medium">모드</label>
            <div className="flex rounded-xl bg-slate-800 p-1 gap-1">
              {(["brand", "local"] as const).map((m) => (
                <label key={m} className="flex-1 cursor-pointer">
                  <input type="radio" name="mode" value={m} defaultChecked={m === "brand"} className="sr-only peer" />
                  <div className="text-center py-2 rounded-lg text-sm font-medium text-slate-400 peer-checked:bg-indigo-600 peer-checked:text-white transition-all">
                    {m === "brand" ? "🌐 온라인 브랜드" : "📍 오프라인 매장"}
                  </div>
                </label>
              ))}
            </div>
          </div>

          <Field label="이메일 (선택, 리포트 수신)" name="owner_email" type="email" placeholder="you@example.com" />

          <button
            type="submit"
            className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl py-3 transition-all"
          >
            프로젝트 생성 →
          </button>
        </form>
      </div>
    </div>
  );
}

function Field({
  label, name, placeholder, type = "text", required,
}: {
  label: string; name: string; placeholder: string; type?: string; required?: boolean;
}) {
  return (
    <div className="space-y-1.5">
      <label htmlFor={name} className="text-slate-300 text-sm font-medium">{label}</label>
      <input
        id={name} name={name} type={type} placeholder={placeholder} required={required}
        className="w-full bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />
    </div>
  );
}
