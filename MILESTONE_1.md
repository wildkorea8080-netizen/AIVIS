# Milestone 1 — 자동 진단 collector (🟢)

목표: `URL`(+ 매장명, 선택적으로 지역)을 입력하면 외부 의존이 적은 노출 준비 신호를
자동 수집·채점해 `ReadinessReport`를 반환하는 진단 엔진 코어를 완성한다.
스크래퍼·유료 API·OAuth는 이 마일스톤 범위가 아니다.

---

## 1. 인터페이스 계약

모든 collector는 이 계약을 따른다. 이것이 깨지지 않는 한 collector는 서로 독립이다.

```python
from pydantic import BaseModel
from typing import Literal

State = Literal["yes", "partial", "no", "unknown"]

class Finding(BaseModel):
    item_id: str          # 루브릭 항목 id (예: "l_schema", "l_place")
    label: str            # 사람이 읽는 항목명
    state: State          # 자동 판정 결과
    evidence: str | None  # 근거 (찾은 스키마 타입, 매칭된 주소 등)

class SignalResult(BaseModel):
    collector: str
    status: Literal["ok", "partial", "error"]
    findings: list[Finding]
    raw: dict = {}        # 디버그·후속 활용용 원자료
    error: str | None = None

class ReadinessReport(BaseModel):
    target_url: str
    place_name: str | None
    region: str | None
    mode: Literal["local", "brand"]
    score: int                       # 0~100
    findings: list[Finding]          # 전 collector 합본
    results: list[SignalResult]      # collector별 원본
```

`Collector` 추상 클래스: `async def collect(self, ctx: AuditContext) -> SignalResult`.
`AuditContext`: `url`, `place_name`, `region`, `mode`, 공유 `httpx.AsyncClient`.

오케스트레이터는 모든 collector를 `asyncio.gather`로 병렬 실행하고, findings를 모아
`scoring.engine`으로 점수를 낸 뒤 `ReadinessReport`를 만든다. 한 collector가
`error`여도 전체는 진행한다(해당 항목은 `unknown` 처리).

---

## 2. 구현할 collector 5종

### 2.1 SchemaCollector
- 대상 URL HTML을 fetch → `extruct`로 JSON-LD/Microdata 파싱.
- 탐지 타입 → 항목 매핑:
  - LOCAL: `LocalBusiness`/`Restaurant`/`Store` 또는 `Menu`/`FAQPage` 존재 → `l_schema`
  - BRAND: `FAQPage` → `b_faq`, `Organization`/`Product` → `b_org`
- state: 핵심 타입 있음 `yes` / 일부만 `partial` / 없음 `no`.
- evidence: 발견된 `@type` 목록.

### 2.2 LlmsTxtCollector
- `GET {origin}/llms.txt`.
- 200 + 본문 비어있지 않음 → `yes`(`l_llms` / `b_llms`), 200이지만 빈약 → `partial`, 404 → `no`.

### 2.3 RobotsCollector
- `GET {origin}/robots.txt` 파싱.
- 점검 봇: `GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`, `CCBot`.
- 어떤 봇도 `Disallow: /` 되어 있지 않으면 `yes`(`b_bots`; LOCAL은 별도 항목 없으면 raw로만 보고).
- 일부 차단 `partial`, 전부/핵심 차단 `no`. robots 없음(=전체 허용) → `yes`.
- evidence: 차단된 봇 목록.

### 2.4 PlaceCollector
- **카카오 로컬 API**(키워드 검색)로 `place_name`(+ region) 조회. 선택적으로 구글 Places.
- 매칭되는 장소 존재 → `l_place` = `yes`, 후보 다수/모호 → `partial`, 없음 → `no`.
- 반환된 이름·주소·전화·카테고리를 `raw`에 저장(다음 마일스톤의 NAP 일관성 비교용 baseline).
- 키 없거나 호출 실패 → `status="error"`, 항목 `unknown`.
- BRAND 모드에서는 비활성(빈 findings).

### 2.5 MentionCollector
- **네이버 검색 API**(blog, cafearticle)로 `place_name`(+ region) 언급 수 조회.
- `total` 카운트로 state: 일정 임계치 이상 `yes`, 소수 `partial`, 0 `no`.
  (임계치는 설정값으로 빼둘 것 — 업종·지역 편차 큼.)
- LOCAL: `l_comm`, BRAND: `b_comm`. evidence: 언급 수 + 대표 링크 1~2개.

> 참고: 콘텐츠 구조 정성평가(`l_content`/`b_bluf` 등 LLM 판정)와 애그리게이터
> 등재 확인은 🟡 항목으로 **Milestone 2**에서 추가한다. M1에서는 해당 항목을 `unknown`으로 둔다.

---

## 3. 인수 기준 (Definition of Done)

1. `POST /audit { url, place_name?, region?, mode }` → `ReadinessReport` 200 반환.
2. 5개 collector가 병렬 실행되고, 임의의 한 collector 실패가 전체를 막지 않는다.
3. 모든 외부 호출에 타임아웃(기본 8s)과 에러 흡수가 있다.
4. 점수는 루브릭 가중치를 정확히 반영하고, `unknown` 항목은 분모에서 제외하거나
   감점 없이 처리한다(택1을 `rubric.py` 주석에 명시).
5. pytest: 각 collector를 `respx`로 모킹한 단위 테스트 + 오케스트레이터 통합 테스트
   (정상/일부실패/전체 fallback 케이스) 포함, 전부 통과.
6. `.env.example`에 필요한 키(`KAKAO_REST_KEY`, `NAVER_CLIENT_ID/SECRET`,
   선택 `GOOGLE_PLACES_KEY`)가 문서화돼 있다.
7. 키가 없으면 해당 collector만 `error`로 우아하게 빠지고 나머지는 동작한다.

---

## 4. Claude Code 킥오프 프롬프트 (그대로 붙여넣기)

```
이 저장소의 CLAUDE.md와 docs/MILESTONE_1.md를 먼저 읽어줘.

지금부터 Milestone 1을 시작한다. 바로 코드를 쓰지 말고 plan mode로 다음을 설계해서
제안해줘:

1) 저장소 구조 스캐폴딩 (CLAUDE.md의 목표 구조 기준)
2) models: SignalResult / Finding / ReadinessReport / AuditContext (Pydantic v2)
3) collectors/base.py 의 Collector 추상 클래스와 오케스트레이터(asyncio.gather +
   collector별 에러 흡수)
4) scoring/rubric.py — MILESTONE_1.md 표의 항목 id·가중치를 LOCAL/BRAND 두 세트로
   코드화, scoring/engine.py — findings -> 0~100 점수 (unknown 처리 방식 명시)
5) collector 5종(schema, llmstxt, robots, place, mention)의 구현 순서와 각 pytest 케이스
6) FastAPI 엔드포인트 POST /audit

제약:
- 공식 API(카카오 로컬, 네이버 검색)와 단순 fetch만 사용. 스크래퍼 금지.
- 모든 외부 호출 async + 타임아웃 + 에러 흡수.
- 키 없으면 해당 collector만 error로 빠지고 전체는 진행.

설계가 끝나면 멈추고 내 승인을 기다려줘. 승인하면 collector를 1개씩 TDD로 구현한다.
```
