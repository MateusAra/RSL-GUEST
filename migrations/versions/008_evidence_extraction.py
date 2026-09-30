"""Create evidence-linked extraction values and independent verifications."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "008_evidence_extraction"
down_revision = "007_quality_assessments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "extractions",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("study_id", sa.String(length=64), sa.ForeignKey("studies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("field_id", sa.String(length=20), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("quote", sa.String(length=8000), nullable=True),
        sa.Column("page_reference", sa.String(length=100), nullable=True),
        sa.Column("extractor_user_id", sa.String(length=64), sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("project_id", "study_id", "field_id", "version", name="uq_extraction_field_version"),
    )
    op.create_index("ix_extractions_project_id", "extractions", ["project_id"])
    op.create_index("ix_extractions_study_id", "extractions", ["study_id"])
    op.create_table(
        "extraction_verifications",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("extraction_id", sa.String(length=64), sa.ForeignKey("extractions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("verifier_user_id", sa.String(length=64), sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("decision", sa.String(length=32), nullable=False),
        sa.Column("justification", sa.String(length=4000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_extraction_verifications_extraction_id", "extraction_verifications", ["extraction_id"])

    dialect = op.get_bind().dialect.name
    tables = ("extractions", "extraction_verifications")
    if dialect == "sqlite":
        for table in tables:
            op.execute(
                f"CREATE TRIGGER {table}_block_update BEFORE UPDATE ON {table} "
                f"BEGIN SELECT RAISE(ABORT, '{table} is append-only'); END"
            )
            op.execute(
                f"CREATE TRIGGER {table}_block_delete BEFORE DELETE ON {table} "
                f"BEGIN SELECT RAISE(ABORT, '{table} is append-only'); END"
            )
    elif dialect == "postgresql":
        op.execute(
            "CREATE FUNCTION reject_extraction_mutation() RETURNS trigger AS $$ "
            "BEGIN RAISE EXCEPTION 'extraction evidence is append-only'; END; "
            "$$ LANGUAGE plpgsql"
        )
        for table in tables:
            op.execute(
                f"CREATE TRIGGER {table}_block_mutation BEFORE UPDATE OR DELETE ON {table} "
                "FOR EACH ROW EXECUTE FUNCTION reject_extraction_mutation()"
            )


def downgrade() -> None:
    dialect = op.get_bind().dialect.name
    tables = ("extraction_verifications", "extractions")
    if dialect == "sqlite":
        for table in tables:
            op.execute(f"DROP TRIGGER IF EXISTS {table}_block_update")
            op.execute(f"DROP TRIGGER IF EXISTS {table}_block_delete")
    elif dialect == "postgresql":
        for table in tables:
            op.execute(f"DROP TRIGGER IF EXISTS {table}_block_mutation ON {table}")
        op.execute("DROP FUNCTION IF EXISTS reject_extraction_mutation()")
    op.drop_index("ix_extraction_verifications_extraction_id", table_name="extraction_verifications")
    op.drop_table("extraction_verifications")
    op.drop_index("ix_extractions_study_id", table_name="extractions")
    op.drop_index("ix_extractions_project_id", table_name="extractions")
    op.drop_table("extractions")