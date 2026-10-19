"""Consensus and third-reviewer arbitration for D/E triage conflicts (spec 004, RF26)."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "011_triage_resolutions"
down_revision = "010_specs_002_003_005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "triage_resolutions",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("study_id", sa.String(length=64), sa.ForeignKey("studies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("phase", sa.Integer(), nullable=False),
        sa.Column("stage", sa.String(length=16), nullable=False),
        sa.Column("user_id", sa.String(length=64), sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("decision", sa.String(length=16), nullable=False),
        sa.Column("criterion_id", sa.String(length=20), nullable=True),
        sa.Column("justification", sa.String(length=4000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("project_id", "study_id", "phase", "stage", "user_id", name="uq_triage_resolution_user"),
    )
    op.create_index("ix_triage_resolutions_project_id", "triage_resolutions", ["project_id"])
    op.create_index("ix_triage_resolutions_study_id", "triage_resolutions", ["study_id"])

    dialect = op.get_bind().dialect.name
    if dialect == "sqlite":
        op.execute(
            "CREATE TRIGGER triage_resolutions_block_update BEFORE UPDATE ON triage_resolutions "
            "BEGIN SELECT RAISE(ABORT, 'triage_resolutions is append-only'); END"
        )
        op.execute(
            "CREATE TRIGGER triage_resolutions_block_delete BEFORE DELETE ON triage_resolutions "
            "BEGIN SELECT RAISE(ABORT, 'triage_resolutions is append-only'); END"
        )
    elif dialect == "postgresql":
        op.execute(
            "CREATE FUNCTION reject_triage_resolution_mutation() RETURNS trigger AS $$ "
            "BEGIN RAISE EXCEPTION 'triage resolutions are append-only'; END; "
            "$$ LANGUAGE plpgsql"
        )
        op.execute(
            "CREATE TRIGGER triage_resolutions_block_mutation BEFORE UPDATE OR DELETE ON triage_resolutions "
            "FOR EACH ROW EXECUTE FUNCTION reject_triage_resolution_mutation()"
        )


def downgrade() -> None:
    dialect = op.get_bind().dialect.name
    if dialect == "sqlite":
        op.execute("DROP TRIGGER IF EXISTS triage_resolutions_block_update")
        op.execute("DROP TRIGGER IF EXISTS triage_resolutions_block_delete")
    elif dialect == "postgresql":
        op.execute("DROP TRIGGER IF EXISTS triage_resolutions_block_mutation ON triage_resolutions")
        op.execute("DROP FUNCTION IF EXISTS reject_triage_resolution_mutation()")
    op.drop_index("ix_triage_resolutions_study_id", table_name="triage_resolutions")
    op.drop_index("ix_triage_resolutions_project_id", table_name="triage_resolutions")
    op.drop_table("triage_resolutions")
