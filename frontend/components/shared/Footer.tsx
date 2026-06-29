export default function Footer() {
  return (
    <footer className="bg-slate-950 border-t border-slate-800 py-10 px-4">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-slate-500 text-sm">
        <span>
          <strong className="text-white">AIVIS</strong> — AI 검색 노출 진단 서비스
        </span>
        <span>© 2025 AIVIS. All rights reserved.</span>
      </div>
    </footer>
  );
}
