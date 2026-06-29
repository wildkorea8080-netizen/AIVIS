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
    name: Mapped[str] = mapped_column(String(200))          # 예: "강남 이루다치과"
    target_url: Mapped[str] = mapped_column(Text)
    mode: Mapped[str] = mapped_column(String(10))           # local | brand
    brand_keyword: Mapped[str] = mapped_column(String(200))  # 언급 감지용 키워드
    owner_email: Mapped[str | None] = mapped_column(String(200))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

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
    response_snippet: Mapped[str | None] = mapped_column(Text)  # 응답 일부 스냅샷
    rank: Mapped[int | None] = mapped_column(Integer)       # 몇 번째로 언급됐는지

    ran_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)

    question: Mapped["MonitorQuestion"] = relationship(back_populates="runs")
