from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base, utcnow
from .accounts import User

review_coauthors = Table(
    "review_coauthors",
    Base.metadata,
    Column("review_id", ForeignKey("reviews.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

review_sources = Table(
    "review_sources",
    Base.metadata,
    Column("review_id", ForeignKey("reviews.id", ondelete="CASCADE"), primary_key=True),
    Column("source_id", ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True),
)


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    is_default: Mapped[bool] = mapped_column(default=False, nullable=False)
    # Automated search connector (rsl.search.CONNECTORS); NULL = manual import only.
    connector: Mapped[str | None] = mapped_column(String(32), nullable=True)


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("author_id", "name", name="uq_review_author_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    objective: Mapped[str] = mapped_column(Text, default="", nullable=False)
    population: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    intervention: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    comparison: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    outcome: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    context: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    quality_cutoff_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    author: Mapped[User] = relationship(foreign_keys=[author_id])
    co_authors: Mapped[list[User]] = relationship(secondary=review_coauthors, order_by=User.username)
    sources: Mapped[list[Source]] = relationship(secondary=review_sources, order_by=Source.name)

    def is_member(self, user: User) -> bool:
        return user.id == self.author_id or any(coauthor.id == user.id for coauthor in self.co_authors)


class Invite(Base):
    __tablename__ = "invites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    invited_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    invitee_email: Mapped[str] = mapped_column(String(254), index=True, nullable=False)
    invitee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)
    code: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    date_sent: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    date_answered: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    review: Mapped[Review] = relationship()
    invited_by: Mapped[User] = relationship(foreign_keys=[invited_by_id])


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    question: Mapped[str] = mapped_column(String(500), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    conclusion: Mapped[str] = mapped_column(Text, default="", nullable=False)


class SelectionCriteria(Base):
    __tablename__ = "selection_criteria"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    criteria_type: Mapped[str] = mapped_column(String(1), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)


class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    synonym_of_id: Mapped[int | None] = mapped_column(ForeignKey("keywords.id", ondelete="CASCADE"), nullable=True)
    related_to: Mapped[str] = mapped_column(String(1), default="", nullable=False)


class QualityQuestion(Base):
    __tablename__ = "quality_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class QualityAnswer(Base):
    __tablename__ = "quality_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)


class DataExtractionField(Base):
    __tablename__ = "data_extraction_fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    field_type: Mapped[str] = mapped_column(String(1), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    lookups: Mapped[list[DataExtractionLookup]] = relationship(
        cascade="all, delete-orphan", order_by="DataExtractionLookup.value"
    )


class DataExtractionLookup(Base):
    __tablename__ = "data_extraction_lookups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    field_id: Mapped[int] = mapped_column(
        ForeignKey("data_extraction_fields.id", ondelete="CASCADE"), index=True, nullable=False
    )
    value: Mapped[str] = mapped_column(String(1000), nullable=False)


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int | None] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    verb: Mapped[str] = mapped_column(String(100), nullable=False)
    target: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    user: Mapped[User] = relationship()
