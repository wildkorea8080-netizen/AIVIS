export interface FindingMeta {
  title: string;
  whyItMatters: string;
  improveTip: string;
  weight: number;
}

export const FINDINGS_META: Record<string, FindingMeta> = {
  l_schema: {
    title: "구조화 데이터 (Schema.org)",
    whyItMatters: "AI가 매장 정보를 정확히 이해하는 핵심 신호입니다.",
    improveTip: "LocalBusiness 또는 Restaurant 스키마를 홈페이지 <head>에 추가하세요.",
    weight: 12,
  },
  l_llms: {
    title: "llms.txt 파일",
    whyItMatters: "ChatGPT·Perplexity 등이 크롤 시 우선 참조하는 파일입니다.",
    improveTip: "웹사이트 루트(/llms.txt)에 매장 소개를 간결하게 작성하세요.",
    weight: 6,
  },
  l_place: {
    title: "플레이스 등록 (카카오맵)",
    whyItMatters: "AI 지역 검색 응답의 상당수가 플레이스 데이터를 활용합니다.",
    improveTip: "카카오맵, 구글 비즈니스 프로필에 매장 정보를 등록하세요.",
    weight: 22,
  },
  l_comm: {
    title: "블로그·커뮤니티 언급",
    whyItMatters: "제3자 언급이 많을수록 AI 추천 확률이 높아집니다.",
    improveTip: "네이버 블로그, 카카오 브런치에 매장 후기가 쌓이도록 유도하세요.",
    weight: 22,
  },
  b_faq: {
    title: "FAQ 구조화 데이터",
    whyItMatters: "AI가 FAQ 콘텐츠를 직접 인용해 답변합니다.",
    improveTip: "FAQPage 스키마를 추가하고 주요 질문·답변을 구조화하세요.",
    weight: 4,
  },
  b_org: {
    title: "Organization/Brand 스키마",
    whyItMatters: "브랜드 신뢰도와 정체성을 AI에게 전달합니다.",
    improveTip: "Organization 스키마에 sameAs 속성으로 소셜 채널을 연결하세요.",
    weight: 8,
  },
  b_llms: {
    title: "llms.txt 파일",
    whyItMatters: "AI 크롤러에게 브랜드 핵심 정보를 직접 전달합니다.",
    improveTip: "/llms.txt를 생성해 브랜드 소개, 주요 제품, 연락처를 작성하세요.",
    weight: 4,
  },
  b_bots: {
    title: "AI 크롤러 접근 허용",
    whyItMatters: "차단된 봇은 콘텐츠를 학습하지 못해 AI 추천에서 제외됩니다.",
    improveTip: "robots.txt에서 GPTBot, ClaudeBot, PerplexityBot 차단을 해제하세요.",
    weight: 18,
  },
  b_comm: {
    title: "외부 언급·미디어",
    whyItMatters: "언론·블로그·디렉토리 언급이 AI 권위 신호가 됩니다.",
    improveTip: "언론 보도, 업종별 디렉토리 등재, 파트너십 콘텐츠를 늘리세요.",
    weight: 18,
  },
};
