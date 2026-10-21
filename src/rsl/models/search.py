from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base, utcnow
from .reviews import Source

RUN_MODES = ("preview", "import")
RUN_STATUSES = {"queued": "Na fila", "running": "Executando", "done": "Concluída", "failed": "Falhou"}


class UserApiKey(Base):
    """A user's own key for a search API, stored encrypted (rsl.crypto) and never sent back to the client."""

    __tablename__ = "user_api_keys"
    __table_args__ = (UniqueConstraint("user_id", "provider", name="uq_user_api_key_provider"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    secret: Mapped[str] = mapped_column(Text, nullable=False)
    extra: Mapped[str] = mapped_column(Text, default="", nullable=False)
    last_four: Mapped[str] = mapped_column(String(4), default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class SearchRun(Base):
    """One automated execution of a source's search string against its API."""

    __tablename__ = "search_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    connector: Mapped[str] = mapped_column(String(32), nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    year_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    year_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_records: Mapped[int] = mapped_column(Integer, nullable=False)
    mode: Mapped[str] = mapped_column(String(8), nullable=False)
    status: Mapped[str] = mapped_column(String(8), default="queued", nullable=False)
    total_reported: Mapped[int | None] = mapped_column(Integer, nullable=True)
    retrieved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    imported: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skipped_existing: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    warnings: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    preview: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str] = mapped_column(Text, default="", nullable=False)
    search_result_id: Mapped[int | None] = mapped_column(
        ForeignKey("search_results.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    source: Mapped[Source] = relationship()
