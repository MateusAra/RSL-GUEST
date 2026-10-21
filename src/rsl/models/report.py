"""PRISMA 2020 reporting (spec 010 adapted): researcher-written sections, checklist and generated versions."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base, utcnow

# Sections of the report skeleton. The researchers write the text; Methods and Results also get data blocks.
REPORT_SECTIONS = {
    "title": "Título",
    "abstract": "Resumo",
    "introduction": "Introdução",
    "methods": "Métodos",
    "results": "Resultados",
    "discussion": "Discussão",
    "threats": "Ameaças à validade",
    "conclusion": "Conclusão",
    "ai_statement": "Declaração de uso de IA generativa",
}
REQUIRED_SECTIONS = ("threats", "ai_statement")
REFERENCE_STYLES = {"apa": "APA (simplificado)", "abnt": "ABNT (simplificado)"}


class ReportSection(Base):
    __tablename__ = "report_sections"

    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), primary_key=True)
    key: Mapped[str] = mapped_column(String(32), primary_key=True)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    updated_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class ReportSettings(Base):
    __tablename__ = "report_settings"

    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), primary_key=True)
    reference_style: Mapped[str] = mapped_column(String(8), default="apa", nullable=False)


class PrismaItem(Base):
    __tablename__ = "prisma_checklist"

    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), primary_key=True)
    item: Mapped[str] = mapped_column(String(8), primary_key=True)
    status: Mapped[str] = mapped_column(String(8), nullable=False)
    location: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    justification: Mapped[str] = mapped_column(Text, default="", nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class ReportVersion(Base):
    """Every generated report is kept: format, chosen style, the numbers used and the file itself."""

    __tablename__ = "report_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    format: Mapped[str] = mapped_column(String(8), nullable=False)
    reference_style: Mapped[str] = mapped_column(String(8), nullable=False)
    numbers: Mapped[dict] = mapped_column(JSON, nullable=False)
    file_name: Mapped[str] = mapped_column(String(300), nullable=False)
    object_key: Mapped[str] = mapped_column(String(500), nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
