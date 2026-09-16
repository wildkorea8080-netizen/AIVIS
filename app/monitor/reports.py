"""주간 리포트 생성.

순수 모듈 — DB·네트워크·설정에 의존하지 않으므로 단위 테스트가 쉽다.
발송 여부 판단과 HTML 렌더링을 모두 여기서 한다.
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.models.orm import MonitorMention, MonitorProject, MonitorRun
from app.monitor.extraction import matches_brand

REPORT_WINDOW = timedelta(days=7)

# 표본이 이보다 적으면 보내지 않는다. 한두 건으로 낸 "0%"는 데이터가 아니라 잡음이고,
# 받는 사람에게는 브랜드가 사라진 것처럼 읽힌다.
MIN_RUNS_TO_SEND = 5

TOP_COMPETITORS = 5


@dataclass(frozen=True)
class CompetitorLine:
    name: str
    mentions: int
    is_own: bool


@dataclass(frozen=True)
class WeeklyReport:
    project_name: str
    brand_keyword: str
    dashboard_url: str
    unsubscribe_url: str

    total_runs: int          # 성공한 호출 수 (실패 제외)
    mentioned_runs: int
    mention_rate: float

    competitors: list[CompetitorLine] = field(default_factory=list)
    weakest_engine: str | None = None   # 이번 주 언급률이 가장 낮은 엔진
    failed_runs: int = 0


def _in_window(run: MonitorRun, now: datetime) -> bool:
    return now - run.ran_at <= REPORT_WINDOW


def build_weekly_report(
    project: MonitorProject,
    runs: list[MonitorRun],
    mentions_by_run: dict[int, list[MonitorMention]],
    *,
    now: datetime,
    base_url: str,
) -> WeeklyReport | None:
    """이번 주 리포트를 만든다. 보낼 만한 데이터가 없으면 None.

    실패한 호출(error가 있는 행)은 언급률 분모에서 제외한다 — 대시보드와 같은 규칙이라
    두 숫자가 어긋나지 않는다.
    """
    window = [r for r in runs if _in_window(r, now)]
    ok_runs = [r for r in window if r.error is None]

    if len(ok_runs) < MIN_RUNS_TO_SEND:
        return None

    mentioned = [r for r in ok_runs if r.mentioned]

    # 엔진별 언급률 — 가장 약한 곳 하나만 고른다
    by_engine: dict[str, list[MonitorRun]] = {}
    for r in ok_runs:
        by_engine.setdefault(r.ai_model, []).append(r)
    weakest = None
    if len(by_engine) > 1:
        weakest = min(
            by_engine,
            key=lambda name: sum(1 for r in by_engine[name] if r.mentioned) / len(by_engine[name]),
        )

    # 추천된 업체 집계 (성공한 run에 달린 것만)
    ok_ids = {r.id for r in ok_runs}
    counts: dict[str, tuple[str, int]] = {}
    for run_id, items in mentions_by_run.items():
        if run_id not in ok_ids:
            continue
        for m in items:
            name, n = counts.get(m.name_key, (m.name_raw, 0))
            counts[m.name_key] = (name, n + 1)

    competitors = [
        CompetitorLine(name=name, mentions=n, is_own=matches_brand(key, project.brand_keyword))
        for key, (name, n) in counts.items()
    ]
    competitors.sort(key=lambda c: -c.mentions)

    return WeeklyReport(
        project_name=project.name,
        brand_keyword=project.brand_keyword,
        dashboard_url=f"{base_url}/monitor/{project.owner_token}",
        unsubscribe_url=f"{base_url}/monitor/{project.owner_token}/unsubscribe",
        total_runs=len(ok_runs),
        mentioned_runs=len(mentioned),
        mention_rate=len(mentioned) / len(ok_runs),
        competitors=competitors[:TOP_COMPETITORS],
        weakest_engine=weakest,
        failed_runs=len(window) - len(ok_runs),
    )


# ── HTML 렌더링 ────────────────────────────────────────────────

_ENGINE_LABELS = {
    "chatgpt": "ChatGPT",
    "claude": "Claude",
    "gemini": "Gemini",
    "perplexity": "Perplexity",
    "grok": "Grok",
}


def render_subject(report: WeeklyReport) -> str:
    if report.mentioned_runs == 0:
        return f"[AIVIS] {report.project_name} — 이번 주 AI 추천에 등장하지 않았습니다"
    pct = round(report.mention_rate * 100)
    return f"[AIVIS] {report.project_name} — 이번 주 언급률 {pct}%"


def render_html(report: WeeklyReport) -> str:
    """이메일 본문.

    삽입값은 모두 escape한다. 프로젝트명은 사용자 입력이고,
    경쟁사명은 AI 응답에서 그대로 가져온 문자열이다.
    """
    e = html.escape
    pct = round(report.mention_rate * 100)

    if report.competitors:
        rows = "".join(
            f'<tr>'
            f'<td style="padding:8px 0;color:{"#4f46e5" if c.is_own else "#334155"};'
            f'font-weight:{"700" if c.is_own else "400"}">'
            f'{e(c.name)}{" (내 브랜드)" if c.is_own else ""}</td>'
            f'<td style="padding:8px 0;text-align:right;color:#64748b">{c.mentions}회</td>'
            f"</tr>"
            for c in report.competitors
        )
        competitor_block = (
            '<h2 style="font-size:15px;margin:28px 0 8px">AI가 추천한 업체</h2>'
            '<table style="width:100%;border-collapse:collapse;font-size:14px">'
            f"{rows}</table>"
        )
    else:
        competitor_block = (
            '<p style="color:#64748b;font-size:14px;margin:28px 0 0">'
            "이번 주에는 추천 업체를 수집하지 못했습니다.</p>"
        )

    if report.mentioned_runs == 0:
        headline = (
            f'<p style="font-size:15px;margin:0 0 4px">'
            f"이번 주 <b>{e(report.brand_keyword)}</b>는 AI 추천 답변에 "
            f"<b>한 번도 등장하지 않았습니다</b>.</p>"
        )
    else:
        headline = (
            f'<p style="font-size:15px;margin:0 0 4px">'
            f"이번 주 <b>{e(report.brand_keyword)}</b> 언급률은 "
            f"<b>{pct}%</b>입니다 ({report.mentioned_runs}/{report.total_runs}회).</p>"
        )

    weakest = ""
    if report.weakest_engine:
        label = _ENGINE_LABELS.get(report.weakest_engine, report.weakest_engine)
        weakest = (
            f'<p style="color:#475569;font-size:14px;margin:16px 0 0">'
            f"가장 약한 엔진은 <b>{e(label)}</b>입니다.</p>"
        )

    footnote = ""
    if report.failed_runs:
        footnote = (
            f'<p style="color:#94a3b8;font-size:12px;margin:8px 0 0">'
            f"일부 엔진 응답 실패: {report.failed_runs}건</p>"
        )

    return f"""<!doctype html>
<html lang="ko"><body style="margin:0;padding:24px;background:#f8fafc;
font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#0f172a">
<div style="max-width:560px;margin:0 auto;background:#fff;border-radius:16px;padding:32px">
  <p style="color:#6366f1;font-size:12px;font-weight:700;margin:0 0 4px">AIVIS 주간 리포트</p>
  <h1 style="font-size:20px;margin:0 0 20px">{e(report.project_name)}</h1>
  {headline}
  {competitor_block}
  {weakest}
  <p style="margin:28px 0 0">
    <a href="{e(report.dashboard_url)}"
       style="display:inline-block;background:#4f46e5;color:#fff;text-decoration:none;
              font-weight:600;font-size:14px;padding:12px 20px;border-radius:10px">
      대시보드에서 자세히 보기
    </a>
  </p>
  {footnote}
  <p style="color:#94a3b8;font-size:12px;margin:24px 0 0;border-top:1px solid #e2e8f0;padding-top:16px">
    이 메일은 프로젝트 생성 시 주간 리포트 수신에 동의하셔서 발송됩니다.
    <a href="{e(report.unsubscribe_url)}" style="color:#94a3b8">수신거부</a>
  </p>
</div>
</body></html>"""
