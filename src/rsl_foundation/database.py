from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, JSON, LargeBinary, String, UniqueConstraint, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class UserRecord(Base):
    __tablename__ = "app_users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class AuthSessionRecord(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("app_users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    refresh_token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class ProjectRecord(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    objective: Mapped[str] = mapped_column(String(4000), nullable=False)
    study_type: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_user_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("app_users.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    version: Mapped[int] = mapped_column(default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class ProjectMembershipRecord(Base):
    __tablename__ = "project_members"

    project_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("app_users.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class AuditEventRecord(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    actor_user_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("app_users.id"), nullable=False, index=True
    )
    performed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    previous_value: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)


class ProjectDocumentRecord(Base):
    __tablename__ = "project_documents"
    __table_args__ = (
        UniqueConstraint("project_id", "kind", "document_key", "version", name="uq_project_document_version"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(String(40), nullable=False)
    document_key: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[int] = mapped_column(nullable=False)
    data: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    created_by: Mapped[str] = mapped_column(String(64), ForeignKey("app_users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class ProtocolDeviationRecord(Base):
    __tablename__ = "protocol_deviations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stage: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(4000), nullable=False)
    justification: Mapped[str] = mapped_column(String(4000), nullable=False)
    affected_section: Mapped[str] = mapped_column(String(100), nullable=False)
    author_user_id: Mapped[str] = mapped_column(String(64), ForeignKey("app_users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class SearchExecutionRecord(Base):
    __tablename__ = "search_executions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    base: Mapped[str] = mapped_column(String(40), nullable=False)
    query: Mapped[str] = mapped_column(String(4000), nullable=False)
    fields: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    result_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    search_string_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    year_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    year_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reported_result_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    created_by: Mapped[str] = mapped_column(String(64), ForeignKey("app_users.id"), nullable=False)


class RawImportRecord(Base):
    __tablename__ = "raw_imports"
    __table_args__ = (
        CheckConstraint(
            "(search_execution_id IS NULL) <> (snowball_round_id IS NULL)",
            name="ck_raw_import_single_origin",
        ),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    search_execution_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("search_executions.id", ondelete="CASCADE"), nullable=True, index=True
    )
    snowball_round_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("snowball_rounds.id"), nullable=True, index=True
    )
    direction: Mapped[str | None] = mapped_column(String(16), nullable=True)
    anomalies: Mapped[list[dict[str, object]] | None] = mapped_column(JSON, nullable=True)
    file_name: Mapped[str] = mapped_column(String(300), nullable=False)
    content_hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    imported_count: Mapped[int] = mapped_column(Integer, nullable=False)
    imported_by: Mapped[str] = mapped_column(String(64), ForeignKey("app_users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class StudyRecord(Base):
    __tablename__ = "studies"
    __table_args__ = (
        CheckConstraint(
            "(search_execution_id IS NULL) <> (snowball_round_id IS NULL)",
            name="ck_study_single_origin",
        ),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    search_execution_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("search_executions.id"), nullable=True
    )
    snowball_round_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("snowball_rounds.id"), nullable=True, index=True
    )
    origin: Mapped[str] = mapped_column(String(40), default="search", nullable=False)
    publication_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    raw_import_id: Mapped[str] = mapped_column(String(64), ForeignKey("raw_imports.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(2000), nullable=False)
    normalized_title: Mapped[str] = mapped_column(String(2000), nullable=False)
    authors: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    venue: Mapped[str | None] = mapped_column(String(500), nullable=True)
    doi: Mapped[str | None] = mapped_column(String(500), nullable=True, index=True)
    abstract: Mapped[str | None] = mapped_column(String(12000), nullable=True)
    keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    imported_by: Mapped[str] = mapped_column(String(64), ForeignKey("app_users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class DuplicateCandidateRecord(Base):
    __tablename__ = "duplicate_candidates"
    __table_args__ = (
        UniqueConstraint("project_id", "study_id_a", "study_id_b", name="uq_duplicate_candidate_pair"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    study_id_a: Mapped[str] = mapped_column(String(64), ForeignKey("studies.id"), nullable=False)
    study_id_b: Mapped[str] = mapped_column(String(64), ForeignKey("studies.id"), nullable=False)
    match_type: Mapped[str] = mapped_column(String(40), nullable=False)
    similarity: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class DuplicateDecisionRecord(Base):
    __tablename__ = "duplicate_decisions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    candidate_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("duplicate_candidates.id"), nullable=False, index=True
    )
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    canonical_study_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("studies.id"), nullable=True)
    justification: Mapped[str] = mapped_column(String(4000), nullable=False)
    method: Mapped[str] = mapped_column(String(16), default="manual", nullable=False)
    decided_by: Mapped[str] = mapped_column(String(64), ForeignKey("app_users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class TriageVoteRecord(Base):
    __tablename__ = "triage_votes"
    __table_args__ = (
        UniqueConstraint(
            "project_id", "study_id", "phase", "reviewer_user_id", name="uq_triage_vote_reviewer"
        ),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    study_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("studies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    phase: Mapped[int] = mapped_column(Integer, nullable=False)
    reviewer_user_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("app_users.id"), nullable=False, index=True
    )
    vote: Mapped[str] = mapped_column(String(16), nullable=False)
    criterion_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class TriageResolutionRecord(Base):
    """Consensus position of R1/R2 or arbitration of R3 for a D/E conflict (spec 004, RF26)."""

    __tablename__ = "triage_resolutions"
    __table_args__ = (
        UniqueConstraint("project_id", "study_id", "phase", "stage", "user_id", name="uq_triage_resolution_user"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    study_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("studies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    phase: Mapped[int] = mapped_column(Integer, nullable=False)
    stage: Mapped[str] = mapped_column(String(16), nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("app_users.id"), nullable=False)
    decision: Mapped[str] = mapped_column(String(16), nullable=False)
    criterion_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    justification: Mapped[str] = mapped_column(String(4000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class QualityAssessmentRecord(Base):
    __tablename__ = "quality_assessments"
    __table_args__ = (
        UniqueConstraint(
            "project_id", "study_id", "reviewer_user_id", name="uq_quality_assessment_reviewer"
        ),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    study_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("studies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reviewer_user_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("app_users.id"), nullable=False, index=True
    )
    scores: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    category_scores: Mapped[dict[str, float]] = mapped_column(JSON, nullable=False)
    classification: Mapped[str] = mapped_column(String(32), nullable=False)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    initial_scores: Mapped[list[dict[str, object]] | None] = mapped_column(JSON, nullable=True)
    instrument_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reopen_justification: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class QualityArbitrationRecord(Base):
    __tablename__ = "quality_arbitrations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    study_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("studies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    criterion_id: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    justification: Mapped[str] = mapped_column(String(4000), nullable=False)
    arbiter_user_id: Mapped[str] = mapped_column(String(64), ForeignKey("app_users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class ProjectGateRecord(Base):
    __tablename__ = "project_gates"
    __table_args__ = (UniqueConstraint("project_id", "gate", name="uq_project_gate"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    gate: Mapped[int] = mapped_column(Integer, nullable=False)
    confirmed_by: Mapped[str] = mapped_column(String(64), ForeignKey("app_users.id"), nullable=False)
    details: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    confirmed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class SnowballRoundRecord(Base):
    __tablename__ = "snowball_rounds"
    __table_args__ = (UniqueConstraint("project_id", "round_number", name="uq_snowball_round_number"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="open", nullable=False)
    opened_by: Mapped[str] = mapped_column(String(64), ForeignKey("app_users.id"), nullable=False)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    closed_by: Mapped[str | None] = mapped_column(String(64), ForeignKey("app_users.id"), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closing_summary: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)


class ExtractionRecord(Base):
    __tablename__ = "extractions"
    __table_args__ = (
        UniqueConstraint("project_id", "study_id", "field_id", "version", name="uq_extraction_field_version"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    study_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("studies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    field_id: Mapped[str] = mapped_column(String(20), nullable=False)
    value: Mapped[object] = mapped_column(JSON, nullable=False)
    quote: Mapped[str | None] = mapped_column(String(8000), nullable=True)
    page_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extractor_user_id: Mapped[str] = mapped_column(String(64), ForeignKey("app_users.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class ExtractionVerificationRecord(Base):
    __tablename__ = "extraction_verifications"
    __table_args__ = (
        UniqueConstraint("extraction_id", "verifier_user_id", name="uq_extraction_verifier"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    extraction_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("extractions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    verifier_user_id: Mapped[str] = mapped_column(String(64), ForeignKey("app_users.id"), nullable=False)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    justification: Mapped[str] = mapped_column(String(4000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class ArtifactRecord(Base):
    __tablename__ = "artifacts"
    __table_args__ = (
        UniqueConstraint("project_id", "file_name", "version", name="uq_artifact_file_version"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_name: Mapped[str] = mapped_column(String(300), nullable=False)
    object_key: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    content_hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by: Mapped[str] = mapped_column(String(64), ForeignKey("app_users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


def build_engine(database_url: str):
    if database_url.startswith("sqlite"):
        options: dict[str, object] = {"connect_args": {"check_same_thread": False}}
        if ":memory:" in database_url:
            options["poolclass"] = StaticPool
        return create_engine(database_url, **options)
    return create_engine(database_url, pool_pre_ping=True)


SessionFactory = sessionmaker
