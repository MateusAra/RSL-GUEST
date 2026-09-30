"""Create immutable artifact metadata and object version records."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "009_artifact_metadata"
down_revision = "008_evidence_extraction"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "artifacts",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_name", sa.String(length=300), nullable=False),
        sa.Column("object_key", sa.String(length=500), nullable=False, unique=True),
        sa.Column("content_hash_sha256", sa.String(length=64), nullable=False),
        sa.Column("mime_type", sa.String(length=200), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.String(length=64), sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("project_id", "file_name", "version", name="uq_artifact_file_version"),
    )
    op.create_index("ix_artifacts_project_id", "artifacts", ["project_id"])

    dialect = op.get_bind().dialect.name
    if dialect == "sqlite":
        op.execute(
            "CREATE TRIGGER artifacts_block_update BEFORE UPDATE ON artifacts "
            "BEGIN SELECT RAISE(ABORT, 'artifacts are immutable'); END"
        )
        op.execute(
            "CREATE TRIGGER artifacts_block_delete BEFORE DELETE ON artifacts "
            "BEGIN SELECT RAISE(ABORT, 'artifacts are immutable'); END"
        )
    elif dialect == "postgresql":
        op.execute(
            "CREATE FUNCTION reject_artifact_mutation() RETURNS trigger AS $$ "
            "BEGIN RAISE EXCEPTION 'artifacts are immutable'; END; "
            "$$ LANGUAGE plpgsql"
        )
        op.execute(
            "CREATE TRIGGER artifacts_block_mutation BEFORE UPDATE OR DELETE ON artifacts "
            "FOR EACH ROW EXECUTE FUNCTION reject_artifact_mutation()"
        )


def downgrade() -> None:
    dialect = op.get_bind().dialect.name
    if dialect == "sqlite":
        op.execute("DROP TRIGGER IF EXISTS artifacts_block_update")
        op.execute("DROP TRIGGER IF EXISTS artifacts_block_delete")
    elif dialect == "postgresql":
        op.execute("DROP TRIGGER IF EXISTS artifacts_block_mutation ON artifacts")
        op.execute("DROP FUNCTION IF EXISTS reject_artifact_mutation()")
    op.drop_index("ix_artifacts_project_id", table_name="artifacts")
    op.drop_table("artifacts")