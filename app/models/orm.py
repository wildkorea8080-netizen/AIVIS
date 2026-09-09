"""SQLAlchemy 2.0 ORM models."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    String, Integer, Text, DateTime, ForeignKey, Boolean, JSON, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Audit Reports ──────────────────────────────────────────────

class AuditReport(Base):
    """POST /audit 결과를 영구 저장. share_id로 /report/{share_id} 조회 가능."""

    __tablename__ = "audit_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    share_id: Mapped[str] = mapped_column(String(36), unique=True, default=lambda: str(uuid4()), index=True)

    target_url: Mapped[str] = mapped_column(Text)
    place_name: Mapped[str | None] = mapped_column(String(200))
    region: Mapped[str | None] = mapped_column(String(100))
    mode: Mapped[str] = mapped_column(String(10))  # local | brand

    score: Mapped[int] = mapped_column(Integer)
    findings: Mapped[dict] = mapped_column(JSON)   # list[Finding] 직렬화
    results: Mapped[dict] = mapped_column(JSON)    # list[SignalResult] 직렬화

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


# ── Monitor ───────────────────────────────────────────────────

class MonitorProject(Base):
    """모니터링 프로젝트 (브랜드 하나 = 프로젝트 하나)."""

    __tablename__ = "monitor_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # 대시보드 주소이자 접근 권한. 순번 id로 주소를 만들면 남의 프로젝트를
    # 훑을 수 있어, AuditReport.share_id와 같은 capability URL 방식을 쓴다.
    owner_token: Mapped[str] = mapped_column(
        String(36), unique=True, default=lambda: str(uuid4()), index=True
    )

    name: Mapped[str] = mapped_column(String(200))          # 예: "강남 이루다치과"
    target_url: Mapped[str] = mapped_column(Text)
    mode: Mapped[str] = mapped_column(String(10))           # local | brand
    brand_keyword: Mapped[str] = mapped_column(String(200))  # 언급 감지용 키워드
    owner_email: Mapped[str | None] = mapped_column(String(200))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    # 소프트 삭제. 링크를 가진 누구나 실행 이력을 영구 파괴할 수 있으면 안 되므로
    # 사용자 삭제는 행을 지우지 않고 이 값만 채운다.
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    questions: Mapped[list["MonitorQuestion"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class MonitorQuestion(Base):
    """AI 엔진에 던질 모니터링 질문."""

    __tablename__ = "monitor_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("monitor_projects.id"))
    question: Mapped[str] = mapped_column(Text)             # "강남 임플란트 잘 하는 치과 추천해줘"
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    project: Mapped["MonitorProject"] = relationship(back_populates="questions")
    runs: Mapped[list["MonitorRun"]] = relationship(back_populates="question", cascade="all, delete-orphan")


class MonitorRun(Base):
    """질문 × AI모델 × 실행일 = 1행. 언급 여부와 응답 스냅샷을 기록."""

    __tablename__ = "monitor_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("monitor_questions.id"))

    ai_model: Mapped[str] = mapped_column(String(50))       # chatgpt | claude | perplexity | gemini | grok
    mentioned: Mapped[bool] = mapped_column(Boolean)        # 브랜드 언급 여부
    response_snippet: Mapped[str | None] = mapped_column(Text)  # 브랜드가 언급된 문장 발췌 (UI 표시용)
    response_text: Mapped[str | None] = mapped_column(Text)     # 응답 전문 — 추출 로직을 고쳐도 재호출 없이 재추출 가능
    rank: Mapped[int | None] = mapped_column(Integer)       # 몇 번째로 언급됐는지

    ran_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)

    question: Mapped["MonitorQuestion"] = relationship(back_populates="runs")
    mentions: Mapped[list["MonitorMention"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class MonitorMention(Base):
    """한 응답에서 추천된 업체 하나. 내 브랜드와 경쟁사를 모두 담는다.

    is_own은 저장하지 않는다 — project.brand_keyword가 바뀌면 과거 행이 거짓이 되므로
    조회 시점에 name_key와 비교해 판정한다.
    """

    __tablename__ = "monitor_mentions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("monitor_runs.id"), index=True)

    name_raw: Mapped[str] = mapped_column(String(200))            # AI가 쓴 그대로 (표시용)
    name_key: Mapped[str] = mapped_column(String(200), index=True)  # 정규화 키 (집계용)
    rank: Mapped[int] = mapped_column(Integer)                    # 목록 내 순번 (1-based)

    run: Mapped["MonitorRun"] = relationship(back_populates="mentions")
