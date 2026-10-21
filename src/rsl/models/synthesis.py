"""Thematic synthesis: codebook, coded segments, themes, dual coding and reliability checklist."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base, utcnow

CODE_KINDS = {"deductive": "Dedutivo", "emergent": "Emergente"}
CODE_STATUSES = {"draft": "Rascunho", "active": "Ativo", "merged": "Fundido", "removed": "Removido"}
# Cruzes & Dybå (2011), itens 18–21 da avaliação de confiabilidade da síntese.
CHECKLIST_ITEMS = {
    18: "Os pressupostos e a abordagem da síntese estão explícitos.",
    19: "O que se afirma é sustentado pela evidência.",
    20: "A linguagem e os conceitos são usados de forma consistente.",
    21: "As perguntas de pesquisa são respondidas com base na evidência.",
}


class CodingSettings(Base):
    __tablename__ = "coding_settings"

    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), primary_key=True)
    dual_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sample_percent: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    coder_a_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    coder_b_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    codebook_verified_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    codebook_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    close_justification: Mapped[str] = mapped_column(Text, default="", nullable=False)


class Code(Base):
    __tablename__ = "codes"
    __table_args__ = (UniqueConstraint("review_id", "origin_lookup_id", name="uq_code_origin_lookup"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    definition: Mapped[str] = mapped_column(Text, default="", nullable=False)
    limits: Mapped[str] = mapped_column(Text, default="", nullable=False)
    kind: Mapped[str] = mapped_column(String(16), default="emergent", nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="draft", nullable=False)
    origin_field_id: Mapped[int | None] = mapped_column(
        ForeignKey("data_extraction_fields.id", ondelete="SET NULL"), nullable=True
    )
    origin_lookup_id: Mapped[int | None] = mapped_column(
        ForeignKey("data_extraction_lookups.id", ondelete="SET NULL"), nullable=True
    )
    merged_into_id: Mapped[int | None] = mapped_column(ForeignKey("codes.id", ondelete="SET NULL"), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class CodeEvent(Base):
    """Immutable history of codebook decisions (spec 007, RF43)."""

    __tablename__ = "code_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    code_id: Mapped[int | None] = mapped_column(ForeignKey("codes.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    previous: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    justification: Mapped[str] = mapped_column(Text, default="", nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class Segment(Base):
    __tablename__ = "segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    page: Mapped[str] = mapped_column(String(20), nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class SegmentCode(Base):
    """A code applied to a segment: by one coder (dual sample) or final (is_final)."""

    __tablename__ = "segment_codes"
    __table_args__ = (
        UniqueConstraint("segment_id", "code_id", "coder_id", "is_final", name="uq_segment_code_application"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    segment_id: Mapped[int] = mapped_column(ForeignKey("segments.id", ondelete="CASCADE"), index=True, nullable=False)
    code_id: Mapped[int] = mapped_column(ForeignKey("codes.id", ondelete="CASCADE"), index=True, nullable=False)
    coder_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_final: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class CodingSample(Base):
    __tablename__ = "coding_sample"

    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    coder_a_done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    coder_b_done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class SegmentResolution(Base):
    __tablename__ = "segment_resolutions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    segment_id: Mapped[int] = mapped_column(ForeignKey("segments.id", ondelete="CASCADE"), index=True, nullable=False)
    code_ids: Mapped[list] = mapped_column(JSON, nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("themes.id", ondelete="SET NULL"), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class ThemeCode(Base):
    __tablename__ = "theme_codes"

    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id", ondelete="CASCADE"), primary_key=True)
    code_id: Mapped[int] = mapped_column(ForeignKey("codes.id", ondelete="CASCADE"), primary_key=True)
    justification: Mapped[str] = mapped_column(Text, default="", nullable=False)


class SynthesisChecklistItem(Base):
    __tablename__ = "synthesis_checklist"

    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), primary_key=True)
    item: Mapped[int] = mapped_column(Integer, primary_key=True)
    met: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    justification: Mapped[str] = mapped_column(Text, default="", nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
