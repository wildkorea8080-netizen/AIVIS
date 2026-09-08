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
    weight: 15,
  },
  // ── 신규 M1 항목 ──────────────────────────────────────────
  l_meta: {
    title: "메타태그 · 콘텐츠 구조",
    whyItMatters: "title·description·H 태그는 AI가 페이지 주제를 이해하는 핵심 단서입니다.",
    improveTip: "title 20-65자, description 50-160자로 작성하고 H1을 정확히 1개만 사용하세요.",
    weight: 6,
  },
  b_meta: {
    title: "메타태그 · 콘텐츠 구조",
    whyItMatters: "title·description·H 태그 위계가 AI의 콘텐츠 이해도를 결정합니다.",
    improveTip: "title 20-65자, description 50-160자, H1→H2→H3 위계를 지키고 이미지에 alt를 추가하세요.",
    weight: 8,
  },
  l_sitemap: {
    title: "사이트맵 (sitemap.xml)",
    whyItMatters: "사이트맵이 있으면 AI 봇이 모든 페이지를 빠짐없이 크롤합니다.",
    improveTip: "/sitemap.xml을 생성하고 robots.txt에 경로를 명시하세요.",
    weight: 3,
  },
  b_sitemap: {
    title: "사이트맵 (sitemap.xml)",
    whyItMatters: "사이트맵은 AI 크롤러가 전체 콘텐츠를 색인하는 가이드입니다.",
    improveTip: "/sitemap.xml에 주요 페이지 URL을 등록하고 정기적으로 업데이트하세요.",
    weight: 4,
  },
  l_render: {
    title: "SSR 렌더링 (GPT봇 접근)",
    whyItMatters: "CSR(JS 렌더링) 사이트는 GPT봇이 콘텐츠를 읽지 못할 수 있습니다.",
    improveTip: "Next.js SSR, Nuxt SSR 등 서버사이드 렌더링 방식으로 전환하세요.",
    weight: 3,
  },
  b_render: {
    title: "SSR 렌더링 (GPT봇 접근)",
    whyItMatters: "GPT·Claude 봇은 CSR 페이지 콘텐츠를 가져가지 못해 학습에서 제외됩니다.",
    improveTip: "Next.js App Router(SSR)를 사용하거나 정적 HTML 사전 렌더링을 적용하세요.",
    weight: 4,
  },
};
