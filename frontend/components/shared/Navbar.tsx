import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-950/80 backdrop-blur border-b border-slate-800">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="text-white font-bold text-xl tracking-tight">
          AIVIS<span className="text-indigo-400">.</span>
        </Link>
        <div className="flex items-center gap-6">
          <Link href="/audit" className="text-slate-400 hover:text-white text-sm transition-colors">
            무료 진단
          </Link>
          <Link href="/monitor" className="text-slate-400 hover:text-white text-sm transition-colors">
            모니터링
          </Link>
          <Link
            href="/audit"
            className="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            시작하기
          </Link>
        </div>
      </div>
    </nav>
  );
}
