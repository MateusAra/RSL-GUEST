from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base, utcnow
from .reviews import DataExtractionLookup, Source

ARTICLE_STATUSES = {"U": "Não classificado", "A": "Aceito", "R": "Rejeitado", "D": "Duplicado"}


class SearchSession(Base):
    """Search string of the review: base string (source NULL) or adapted to one source."""

    __tablename__ = "search_sessions"
    __table_args__ = (UniqueConstraint("review_id", "source_id", name="uq_search_session_source"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"), nullable=True)
    search_string: Mapped[str] = mapped_column(Text, default="", nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class SearchResult(Base):
    """One imported file (BibTeX, RIS or CSV) for a source."""

    __tablename__ = "search_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(300), nullable=False)
    object_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    imported_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True, index=True)
    search_result_id: Mapped[int | None] = mapped_column(
        ForeignKey("search_results.id", ondelete="SET NULL"), nullable=True
    )
    bibtex_key: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    title: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    author: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    journal: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    year: Mapped[str] = mapped_column(String(10), default="", nullable=False)
    pages: Mapped[str] = mapped_column(String(20), default="", nullable=False)
    volume: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    abstract: Mapped[str] = mapped_column(Text, default="", nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(1), default="U", nullable=False, index=True)
    comments: Mapped[str] = mapped_column(Text, default="", nullable=False)
    doi: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    affiliation: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    author_keywords: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    keywords: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    publisher: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    issn: Mapped[str] = mapped_column(String(50), default="", nullable=False)
    language: Mapped[str] = mapped_column(String(50), default="", nullable=False)
    note: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    selection_criteria_id: Mapped[int | None] = mapped_column(
        ForeignKey("selection_criteria.id", ondelete="SET NULL"), nullable=True
    )
    finished_data_extraction: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    source: Mapped[Source | None] = relationship()


class QualityAssessment(Base):
    __tablename__ = "quality_assessments"
    __table_args__ = (UniqueConstraint("article_id", "question_id", name="uq_quality_assessment_question"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("quality_questions.id", ondelete="CASCADE"), nullable=False)
    answer_id: Mapped[int | None] = mapped_column(ForeignKey("quality_answers.id", ondelete="CASCADE"), nullable=True)


data_extraction_select_values = Table(
    "data_extraction_select_values",
    Base.metadata,
    Column("extraction_id", ForeignKey("data_extractions.id", ondelete="CASCADE"), primary_key=True),
    Column("lookup_id", ForeignKey("data_extraction_lookups.id", ondelete="CASCADE"), primary_key=True),
)


class DataExtraction(Base):
    __tablename__ = "data_extractions"
    __table_args__ = (UniqueConstraint("article_id", "field_id", name="uq_data_extraction_field"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True, nullable=False)
    field_id: Mapped[int] = mapped_column(ForeignKey("data_extraction_fields.id", ondelete="CASCADE"), nullable=False)
    value: Mapped[str] = mapped_column(Text, default="", nullable=False)

    select_values: Mapped[list[DataExtractionLookup]] = relationship(secondary=data_extraction_select_values)
