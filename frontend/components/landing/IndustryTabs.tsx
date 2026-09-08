"use client";

import { useState } from "react";

const INDUSTRIES = [
  {
    id: "medical",
    label: "🏥 병원·치과",
    question: "강남역 근처 임플란트 잘 하는 치과 추천해줘",
    context: "지역과 시술을 함께 좁혀 묻는 패턴",
  },
  {
    id: "legal",
    label: "⚖️ 법률·세무",
    question: "서울 이혼 전문 변호사 중 비용 합리적인 곳 어디야?",
    context: "비용 조건까지 붙여 비교하는 패턴",
  },
  {
    id: "food",
    label: "🍽️ 식당·카페",
    question: "홍대 데이트하기 좋은 분위기 카페 추천해줘",
    context: "분위기·목적으로 찾는 추천 패턴",
  },
  {
    id: "beauty",
    label: "💇 뷰티·쇼핑",
    question: "강남 왁싱 샵 중 청결하고 실력 좋은 곳 알려줘",
    context: "신뢰도를 함께 확인하는 로컬 서비스 패턴",
  },
  {
    id: "brand",
    label: "🌐 온라인 브랜드",
    question: "국내 스타트업이 쓸 만한 HR SaaS 툴 추천해줘",
    context: "AI에게 소프트웨어 추천을 묻는 패턴",
  },
];

export default function IndustryTabs() {
  const [active, setActive] = useState("medical");
  const current = INDUSTRIES.find((i) => i.id === active)!;

  return (
    <section className="bg-slate-950 py-24 px-4">
      <div className="max-w-4xl mx-auto space-y-10">
        <div className="text-center space-y-3">
          <h2 className="text-3xl md:text-4xl font-black text-white">
            고객이 AI에게 이렇게 묻습니다
          </h2>
          <p className="text-slate-400 text-lg">업종을 선택해 실제 AI 질문 패턴을 확인하세요</p>
        </div>

        {/* 탭 */}
        <div className="flex flex-wrap justify-center gap-2">
          {INDUSTRIES.map((ind) => (
            <button
              key={ind.id}
              onClick={() => setActive(ind.id)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                active === ind.id
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-800 text-slate-400 hover:text-white"
              }`}
            >
              {ind.label}
            </button>
          ))}
        </div>

        {/* 질문 카드 */}
        <div className="bg-slate-900 border border-slate-700 rounded-2xl p-8 space-y-4">
          <p className="text-slate-500 text-xs">{current.context}</p>
          <div className="flex gap-3">
            <span className="text-slate-400 text-sm font-medium shrink-0">사용자:</span>
            <p className="text-white text-lg font-medium">"{current.question}"</p>
          </div>
          <div className="border-t border-slate-800 pt-4 flex gap-3">
            <span className="text-indigo-400 text-sm font-medium shrink-0">AI:</span>
            <p className="text-slate-300 text-sm leading-relaxed">
              <span className="bg-indigo-950 border border-indigo-800 text-indigo-300 px-2 py-0.5 rounded text-xs mr-2">
                당신의 비즈니스
              </span>
              가 이 답변에 등장할 수 있습니다. AIVIS Score를 높이면 AI 추천 확률이 올라갑니다.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
