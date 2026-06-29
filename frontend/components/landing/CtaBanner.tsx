import Link from "next/link";

export default function CtaBanner() {
  return (
    <section className="bg-gradient-to-r from-indigo-900 via-violet-900 to-indigo-900 py-20 px-4">
      <div className="max-w-2xl mx-auto text-center space-y-6">
        <h2 className="text-3xl md:text-4xl font-black text-white">
          지금 바로 무료로 진단받으세요
        </h2>
        <p className="text-indigo-200 text-lg">
          30초, URL 하나면 됩니다. 신용카드 불필요.
        </p>
        <Link
          href="/audit"
          className="inline-block bg-white text-indigo-700 font-bold text-lg px-10 py-4 rounded-2xl hover:bg-indigo-50 transition-colors shadow-lg"
        >
          AI 노출 진단하기 →
        </Link>
        <p className="text-indigo-400 text-sm">
          경쟁자보다 먼저 시작하는 것이 유일한 전략입니다
        </p>
      </div>
    </section>
  );
}
