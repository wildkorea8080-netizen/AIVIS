# CLAUDE.md — BOIM (가제)

> AI 검색 노출 진단·모니터링 서비스. 오프라인 매장과 온라인 브랜드가
> ChatGPT·Perplexity·Gemini·카카오맵 AI·네이버 플레이스 AI의 **추천 답변에
> 등장하도록** 사전 작업을 진단·추천하고, 그 효과를 모니터링한다.

## 제품 구조 (2개 모듈)

1. **준비도 진단 (Auditor)** — URL·매장명을 입력하면 노출 준비 신호를 수집·채점하고
   30/60/90일 실행계획을 생성한다.
2. **가시성 모니터 (Monitor)** — 질문 세트를 실제 AI 엔진에 던져 노출 여부·순위·
   점유율(Share of Voice)을 시계열로 추적한다.

이 저장소는 **백엔드(진단 엔진)**부터 시작한다. 모니터·대시보드는 이후 마일스톤.

## 기술 스택

- 백엔드: Python 3.12, FastAPI, Pydantic v2, httpx(async), extruct, BeautifulSoup4
- DB: Neon PostgreSQL (SQLAlchemy 2.0 + Alembic)
- 작업 큐/스케줄: 이후 마일스톤에서 Celery 또는 APScheduler
- 프런트: Next.js 14 (이후 마일스톤)
- 테스트: pytest + pytest-asyncio + respx(HTTP mocking)

## 핵심 원칙 (반드시 준수)

1. **공식 API·OAuth 우선, 스크래핑 최소화.** 카카오 로컬 API·구글 Places API·
   네이버 검색 API 등 공식 경로를 먼저 쓴다. 리뷰·통계처럼 공식 API가 없는 데이터는
   "매장 사장이 자기 계정(네이버 스마트플레이스·구글 비즈니스 프로필)을 OAuth로
   연결" 하는 흐름으로 합법적으로 읽는다. 스크래핑은 최후 수단이며 별도 모듈로 격리한다.
2. **합법성·ToS 우선.** 가짜 리뷰 생성, 대량 무단 스크래핑 등 ToS·법 위반 기능은 만들지 않는다.
3. **collector는 외부 의존을 격리한다.** 각 신호원(소스)은 독립 collector로, 인터페이스
   계약(`SignalResult`)을 따른다. 한 소스가 죽어도 나머지는 동작해야 한다.
4. **점수는 설명 가능해야 한다.** 모든 점수는 항목별 `Finding`(상태+근거)으로 환원된다.
   불투명한 단일 점수 금지.
5. **비밀키는 환경변수.** 키·시크릿은 `.env`로만 주입하고 절대 커밋하지 않는다.

## 저장소 구조 (목표)

```
app/
  main.py                 # FastAPI 진입점
  models/                 # Pydantic 스키마 (SignalResult, Finding, ReadinessReport)
  collectors/
    base.py               # Collector 추상 클래스 + 계약
    schema_collector.py
    llmstxt_collector.py
    robots_collector.py
    place_collector.py
    mention_collector.py
  scoring/
    rubric.py             # 항목·가중치 정의 (LOCAL / BRAND)
    engine.py             # findings -> 점수 환산
  config.py               # 환경변수 로딩
tests/
docs/
  MILESTONE_1.md
.env.example
```

## 채점 루브릭 (요약 — 상세는 scoring/rubric.py)

오프라인 매장(LOCAL) 100점: 플레이스&정보 일관성 22 / 리뷰 신호 24 /
구조화데이터&사이트 18 / 지역 권위 22 / 정보 최신성 14.
온라인 브랜드(BRAND) 100점: SEO기반 20 / 크롤러접근 18 / 구조화데이터 16 /
콘텐츠구조 16 / 제3자권위 18 / E-E-A-T 12.
(항목 id·가중치는 MILESTONE_1.md 표를 그대로 코드로 옮긴다.)

## 현재 마일스톤

**Milestone 1 — 🟢 자동 진단 collector.** 외부 의존이 적고 즉시 자동화 가능한
신호만 먼저 구현한다: 스키마 / llms.txt / robots / 플레이스 존재(NAP) / 블로그 언급.
상세 스펙·인터페이스·인수 기준은 `docs/MILESTONE_1.md` 참조.

## 작업 방식

- 큰 변경은 먼저 plan mode로 설계를 제안하고 승인받은 뒤 구현한다.
- collector는 1개씩, 각각 pytest와 함께 완성한다(TDD 권장).
- 외부 호출은 전부 async + 타임아웃 + 에러를 `SignalResult.status="error"`로 흡수한다.
