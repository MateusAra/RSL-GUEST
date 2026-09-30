"""Create versioned project configuration and append-only deviations."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "004_project_configuration"
down_revision = "003_append_only_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "project_documents",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(length=40), nullable=False),
        sa.Column("document_key", sa.String(length=100), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(length=64), sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("project_id", "kind", "document_key", "version", name="uq_project_document_version"),
    )
    op.create_index("ix_project_documents_project_id", "project_documents", ["project_id"])
    op.create_table(
        "protocol_deviations",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stage", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=4000), nullable=False),
        sa.Column("justification", sa.String(length=4000), nullable=False),
        sa.Column("affected_section", sa.String(length=100), nullable=False),
        sa.Column("author_user_id", sa.String(length=64), sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_protocol_deviations_project_id", "protocol_deviations", ["project_id"])

    dialect = op.get_bind().dialect.name
    tables = ("project_documents", "protocol_deviations")
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
            "CREATE FUNCTION reject_project_document_mutation() RETURNS trigger AS $$ "
            "BEGIN RAISE EXCEPTION 'project configuration and deviations are append-only'; END; "
            "$$ LANGUAGE plpgsql"
        )
        for table in tables:
            op.execute(
                f"CREATE TRIGGER {table}_block_mutation BEFORE UPDATE OR DELETE ON {table} "
                "FOR EACH ROW EXECUTE FUNCTION reject_project_document_mutation()"
            )


def downgrade() -> None:
    dialect = op.get_bind().dialect.name
    tables = ("protocol_deviations", "project_documents")
    if dialect == "sqlite":
        for table in tables:
            op.execute(f"DROP TRIGGER IF EXISTS {table}_block_update")
            op.execute(f"DROP TRIGGER IF EXISTS {table}_block_delete")
    elif dialect == "postgresql":
        for table in tables:
            op.execute(f"DROP TRIGGER IF EXISTS {table}_block_mutation ON {table}")
        op.execute("DROP FUNCTION IF EXISTS reject_project_document_mutation()")
    op.drop_index("ix_protocol_deviations_project_id", table_name="protocol_deviations")
    op.drop_table("protocol_deviations")
    op.drop_index("ix_project_documents_project_id", table_name="project_documents")
    op.drop_table("project_documents")