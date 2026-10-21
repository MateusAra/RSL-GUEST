"""Analyses (spec 008 adapted): optional hypotheses, verdicts, weighting and immutable snapshots."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base, utcnow

VERDICTS = {"supports": "Suporta", "partial": "Suporta parcialmente", "refutes": "Refuta", "inconclusive": "Inconclusivo"}


class Hypothesis(Base):
    __tablename__ = "hypotheses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    independent_variables: Mapped[str] = mapped_column(Text, default="", nullable=False)
    dependent_variables: Mapped[str] = mapped_column(Text, default="", nullable=False)
    operational_criteria: Mapped[str] = mapped_column(Text, default="", nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class HypothesisVerdict(Base):
    __tablename__ = "hypothesis_verdicts"
    __table_args__ = (UniqueConstraint("hypothesis_id", "article_id", name="uq_verdict_article"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hypothesis_id: Mapped[int] = mapped_column(ForeignKey("hypotheses.id", ondelete="CASCADE"), index=True, nullable=False)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True, nullable=False)
    verdict: Mapped[str] = mapped_column(String(16), nullable=False)
    justification: Mapped[str] = mapped_column(Text, default="", nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class AnalysisSettings(Base):
    __tablename__ = "analysis_settings"

    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), primary_key=True)
    high_min_pct: Mapped[float] = mapped_column(Float, default=70.0, nullable=False)
    high_weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    moderate_min_pct: Mapped[float] = mapped_column(Float, default=40.0, nullable=False)
    moderate_weight: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    author_concentration_pct: Mapped[float] = mapped_column(Float, default=20.0, nullable=False)


class AnalysisSnapshot(Base):
    """Immutable record of one analysis run: filters, weighting and results (spec 008, rule 4)."""

    __tablename__ = "analysis_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    label: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    filters: Mapped[dict] = mapped_column(JSON, nullable=False)
    settings: Mapped[dict] = mapped_column(JSON, nullable=False)
    results: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
