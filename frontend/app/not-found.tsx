import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-slate-950 pt-32 px-4">
      <div className="max-w-md mx-auto text-center space-y-4">
        <p className="text-slate-600 text-sm font-mono">404</p>
        <h1 className="text-xl font-bold text-white">페이지를 찾을 수 없습니다</h1>
        <p className="text-slate-400 text-sm leading-relaxed">
          주소가 잘못됐거나 삭제된 프로젝트입니다. 모니터링 대시보드 주소는 프로젝트마다
          고유하므로, 저장해 둔 링크를 다시 확인해 주세요.
        </p>
        <div className="flex justify-center gap-3 pt-2">
          <Link href="/monitor" className="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl px-5 py-2.5">
            내 프로젝트
          </Link>
          <Link href="/" className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm rounded-xl px-5 py-2.5">
            홈으로
          </Link>
        </div>
      </div>
    </div>
  );
}
