"""Create search, immutable imports, studies and duplicate decisions."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "005_search_import_deduplication"
down_revision = "004_project_configuration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "search_executions",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("base", sa.String(length=40), nullable=False),
        sa.Column("query", sa.String(length=4000), nullable=False),
        sa.Column("fields", sa.JSON(), nullable=False),
        sa.Column("result_limit", sa.Integer(), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", sa.String(length=64), sa.ForeignKey("app_users.id"), nullable=False),
    )
    op.create_index("ix_search_executions_project_id", "search_executions", ["project_id"])
    op.create_table(
        "raw_imports",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("search_execution_id", sa.String(length=64), sa.ForeignKey("search_executions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_name", sa.String(length=300), nullable=False),
        sa.Column("content_hash_sha256", sa.String(length=64), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("imported_count", sa.Integer(), nullable=False),
        sa.Column("imported_by", sa.String(length=64), sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_raw_imports_search_execution_id", "raw_imports", ["search_execution_id"])
    op.create_table(
        "studies",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("search_execution_id", sa.String(length=64), sa.ForeignKey("search_executions.id"), nullable=False),
        sa.Column("raw_import_id", sa.String(length=64), sa.ForeignKey("raw_imports.id"), nullable=False),
        sa.Column("title", sa.String(length=2000), nullable=False),
        sa.Column("normalized_title", sa.String(length=2000), nullable=False),
        sa.Column("authors", sa.JSON(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("venue", sa.String(length=500), nullable=True),
        sa.Column("doi", sa.String(length=500), nullable=True),
        sa.Column("abstract", sa.String(length=12000), nullable=True),
        sa.Column("keywords", sa.JSON(), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("imported_by", sa.String(length=64), sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_studies_project_id", "studies", ["project_id"])
    op.create_index("ix_studies_doi", "studies", ["doi"])
    op.create_table(
        "duplicate_candidates",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("study_id_a", sa.String(length=64), sa.ForeignKey("studies.id"), nullable=False),
        sa.Column("study_id_b", sa.String(length=64), sa.ForeignKey("studies.id"), nullable=False),
        sa.Column("match_type", sa.String(length=40), nullable=False),
        sa.Column("similarity", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("project_id", "study_id_a", "study_id_b", name="uq_duplicate_candidate_pair"),
    )
    op.create_index("ix_duplicate_candidates_project_id", "duplicate_candidates", ["project_id"])
    op.create_table(
        "duplicate_decisions",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("candidate_id", sa.String(length=64), sa.ForeignKey("duplicate_candidates.id"), nullable=False),
        sa.Column("decision", sa.String(length=32), nullable=False),
        sa.Column("canonical_study_id", sa.String(length=64), sa.ForeignKey("studies.id"), nullable=True),
        sa.Column("justification", sa.String(length=4000), nullable=False),
        sa.Column("decided_by", sa.String(length=64), sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_duplicate_decisions_candidate_id", "duplicate_decisions", ["candidate_id"])

    dialect = op.get_bind().dialect.name
    append_only_tables = ("search_executions", "raw_imports", "studies", "duplicate_candidates", "duplicate_decisions")
    if dialect == "sqlite":
        for table in append_only_tables:
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
            "CREATE FUNCTION reject_search_record_mutation() RETURNS trigger AS $$ "
            "BEGIN RAISE EXCEPTION 'search records are append-only'; END; "
            "$$ LANGUAGE plpgsql"
        )
        for table in append_only_tables:
            op.execute(
                f"CREATE TRIGGER {table}_block_mutation BEFORE UPDATE OR DELETE ON {table} "
                "FOR EACH ROW EXECUTE FUNCTION reject_search_record_mutation()"
            )


def downgrade() -> None:
    dialect = op.get_bind().dialect.name
    append_only_tables = ("duplicate_decisions", "duplicate_candidates", "studies", "raw_imports", "search_executions")
    if dialect == "sqlite":
        for table in append_only_tables:
            op.execute(f"DROP TRIGGER IF EXISTS {table}_block_update")
            op.execute(f"DROP TRIGGER IF EXISTS {table}_block_delete")
    elif dialect == "postgresql":
        for table in append_only_tables:
            op.execute(f"DROP TRIGGER IF EXISTS {table}_block_mutation ON {table}")
        op.execute("DROP FUNCTION IF EXISTS reject_search_record_mutation()")
    op.drop_index("ix_duplicate_decisions_candidate_id", table_name="duplicate_decisions")
    op.drop_table("duplicate_decisions")
    op.drop_index("ix_duplicate_candidates_project_id", table_name="duplicate_candidates")
    op.drop_table("duplicate_candidates")
    op.drop_index("ix_studies_doi", table_name="studies")
    op.drop_index("ix_studies_project_id", table_name="studies")
    op.drop_table("studies")
    op.drop_index("ix_raw_imports_search_execution_id", table_name="raw_imports")
    op.drop_table("raw_imports")
    op.drop_index("ix_search_executions_project_id", table_name="search_executions")
    op.drop_table("search_executions")