from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from seo_score.db.base import Base
from seo_score.db.ids import new_id


class Plan(StrEnum):
    FREE = "FREE"
    DEVELOPER = "DEVELOPER"
    PRO = "PRO"
    AGENCY = "AGENCY"


class AuditStatus(StrEnum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class AuditScope(StrEnum):
    PAGE = "PAGE"
    SITE = "SITE"


class UsageType(StrEnum):
    AUDIT = "AUDIT"
    BATCH = "BATCH"
    PDF = "PDF"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("usr"))
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    plan: Mapped[Plan] = mapped_column(String(32), default=Plan.FREE, nullable=False)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    webhook_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    webhook_secret: Mapped[str | None] = mapped_column(String(128), nullable=True)
    brand_logo_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    api_keys: Mapped[list[ApiKey]] = relationship(back_populates="user", cascade="all, delete-orphan")
    audits: Mapped[list[Audit]] = relationship(back_populates="user", cascade="all, delete-orphan")
    usage_events: Mapped[list[UsageEvent]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class ApiKey(Base):
    __tablename__ = "api_keys"
    __table_args__ = (Index("ix_api_keys_user_id", "user_id"),)

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("key"))
    user_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    prefix: Mapped[str] = mapped_column(String(32), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="api_keys")


class Audit(Base):
    __tablename__ = "audits"
    __table_args__ = (
        Index("ix_audits_user_created", "user_id", "created_at"),
        Index("ix_audits_user_domain", "user_id", "domain"),
        Index("ix_audits_status", "status"),
        Index("ix_audits_batch_id", "batch_id"),
    )

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("aud"))
    user_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[AuditStatus] = mapped_column(
        String(32), default=AuditStatus.QUEUED, nullable=False
    )
    scope: Mapped[AuditScope] = mapped_column(String(32), default=AuditScope.PAGE, nullable=False)
    overall_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    category_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    options: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    parent_audit_id: Mapped[str | None] = mapped_column(
        String(40), ForeignKey("audits.id", ondelete="SET NULL"), nullable=True
    )
    batch_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="audits")
    parent_audit: Mapped[Audit | None] = relationship(
        remote_side="Audit.id", back_populates="child_audits"
    )
    child_audits: Mapped[list[Audit]] = relationship(back_populates="parent_audit")
    result: Mapped[AuditResult | None] = relationship(
        back_populates="audit", uselist=False, cascade="all, delete-orphan"
    )
    usage_events: Mapped[list[UsageEvent]] = relationship(back_populates="audit")


class AuditResult(Base):
    __tablename__ = "audit_results"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("res"))
    audit_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("audits.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    checks: Mapped[list] = mapped_column(JSONB, nullable=False)
    snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    pagespeed: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    axe: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    pdf_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    audit: Mapped[Audit] = relationship(back_populates="result")


class UsageEvent(Base):
    __tablename__ = "usage_events"
    __table_args__ = (Index("ix_usage_events_user_period_type", "user_id", "period", "type"),)

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: new_id("evt"))
    user_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    audit_id: Mapped[str | None] = mapped_column(
        String(40), ForeignKey("audits.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[UsageType] = mapped_column(String(32), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    period: Mapped[str] = mapped_column(String(7), nullable=False)  # YYYY-MM
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="usage_events")
    audit: Mapped[Audit | None] = relationship(back_populates="usage_events")
