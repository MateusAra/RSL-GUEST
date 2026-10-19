"""Gates, search strings, snowballing, canonical records and QA arbitration (specs 002, 003, 005)."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "010_specs_002_003_005"
down_revision = "009_artifact_metadata"
branch_labels = None
depends_on = None

NEW_APPEND_ONLY_TABLES = ("project_gates", "quality_arbitrations")
# SQLite batch mode rebuilds these tables, which drops the append-only triggers from migration 005.
REBUILT_APPEND_ONLY_TABLES = ("raw_imports", "studies")
DOWNGRADE_REBUILT_TABLES = ("raw_imports", "studies", "search_executions", "duplicate_decisions")


def _create_sqlite_triggers(tables: tuple[str, ...]) -> None:
    for table in tables:
        op.execute(
            f"CREATE TRIGGER {table}_block_update BEFORE UPDATE ON {table} "
            f"BEGIN SELECT RAISE(ABORT, '{table} is append-only'); END"
        )
        op.execute(
            f"CREATE TRIGGER {table}_block_delete BEFORE DELETE ON {table} "
            f"BEGIN SELECT RAISE(ABORT, '{table} is append-only'); END"
        )


def _drop_sqlite_triggers(tables: tuple[str, ...]) -> None:
    for table in tables:
        op.execute(f"DROP TRIGGER IF EXISTS {table}_block_update")
        op.execute(f"DROP TRIGGER IF EXISTS {table}_block_delete")


def _create_append_only_triggers(dialect: str) -> None:
    if dialect == "sqlite":
        _create_sqlite_triggers(NEW_APPEND_ONLY_TABLES)
    elif dialect == "postgresql":
        op.execute(
            "CREATE FUNCTION reject_gate_and_arbitration_mutation() RETURNS trigger AS $$ "
            "BEGIN RAISE EXCEPTION 'gates and QA arbitrations are append-only'; END; "
            "$$ LANGUAGE plpgsql"
        )
        for table in NEW_APPEND_ONLY_TABLES:
            op.execute(
                f"CREATE TRIGGER {table}_block_mutation BEFORE UPDATE OR DELETE ON {table} "
                "FOR EACH ROW EXECUTE FUNCTION reject_gate_and_arbitration_mutation()"
            )


def _drop_append_only_triggers(dialect: str) -> None:
    if dialect == "sqlite":
        _drop_sqlite_triggers(NEW_APPEND_ONLY_TABLES)
    elif dialect == "postgresql":
        for table in NEW_APPEND_ONLY_TABLES:
            op.execute(f"DROP TRIGGER IF EXISTS {table}_block_mutation ON {table}")
        op.execute("DROP FUNCTION IF EXISTS reject_gate_and_arbitration_mutation()")


def upgrade() -> None:
    dialect = op.get_bind().dialect.name

    op.create_table(
        "project_gates",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("gate", sa.Integer(), nullable=False),
        sa.Column("confirmed_by", sa.String(length=64), sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("project_id", "gate", name="uq_project_gate"),
    )
    op.create_index("ix_project_gates_project_id", "project_gates", ["project_id"])

    op.create_table(
        "snowball_rounds",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=16), server_default="open", nullable=False),
        sa.Column("opened_by", sa.String(length=64), sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("closed_by", sa.String(length=64), sa.ForeignKey("app_users.id"), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closing_summary", sa.JSON(), nullable=True),
        sa.UniqueConstraint("project_id", "round_number", name="uq_snowball_round_number"),
    )
    op.create_index("ix_snowball_rounds_project_id", "snowball_rounds", ["project_id"])

    op.create_table(
        "quality_arbitrations",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("study_id", sa.String(length=64), sa.ForeignKey("studies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("criterion_id", sa.String(length=20), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("justification", sa.String(length=4000), nullable=False),
        sa.Column("arbiter_user_id", sa.String(length=64), sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_quality_arbitrations_project_id", "quality_arbitrations", ["project_id"])
    op.create_index("ix_quality_arbitrations_study_id", "quality_arbitrations", ["study_id"])

    # Plain ADD COLUMN keeps the append-only triggers; batch mode would rebuild the table on SQLite.
    op.add_column("search_executions", sa.Column("search_string_version", sa.Integer(), nullable=True))
    op.add_column("search_executions", sa.Column("year_from", sa.Integer(), nullable=True))
    op.add_column("search_executions", sa.Column("year_to", sa.Integer(), nullable=True))
    op.add_column("search_executions", sa.Column("reported_result_count", sa.Integer(), nullable=True))

    if dialect == "sqlite":
        _drop_sqlite_triggers(REBUILT_APPEND_ONLY_TABLES)
    with op.batch_alter_table("raw_imports") as batch:
        batch.alter_column("search_execution_id", existing_type=sa.String(length=64), nullable=True)
        batch.add_column(sa.Column("snowball_round_id", sa.String(length=64), nullable=True))
        batch.add_column(sa.Column("direction", sa.String(length=16), nullable=True))
        batch.add_column(sa.Column("anomalies", sa.JSON(), nullable=True))
        batch.create_foreign_key("fk_raw_imports_snowball_round", "snowball_rounds", ["snowball_round_id"], ["id"])
        batch.create_index("ix_raw_imports_snowball_round_id", ["snowball_round_id"])
        batch.create_check_constraint(
            "ck_raw_import_single_origin",
            "(search_execution_id IS NULL) <> (snowball_round_id IS NULL)",
        )

    with op.batch_alter_table("studies") as batch:
        batch.alter_column("search_execution_id", existing_type=sa.String(length=64), nullable=True)
        batch.add_column(sa.Column("snowball_round_id", sa.String(length=64), nullable=True))
        batch.add_column(sa.Column("origin", sa.String(length=40), server_default="search", nullable=False))
        batch.add_column(sa.Column("publication_type", sa.String(length=20), nullable=True))
        batch.create_foreign_key("fk_studies_snowball_round", "snowball_rounds", ["snowball_round_id"], ["id"])
        batch.create_index("ix_studies_snowball_round_id", ["snowball_round_id"])
        batch.create_check_constraint(
            "ck_study_single_origin",
            "(search_execution_id IS NULL) <> (snowball_round_id IS NULL)",
        )
    if dialect == "sqlite":
        _create_sqlite_triggers(REBUILT_APPEND_ONLY_TABLES)

    op.add_column(
        "duplicate_decisions", sa.Column("method", sa.String(length=16), server_default="manual", nullable=False)
    )
    op.add_column("quality_assessments", sa.Column("initial_scores", sa.JSON(), nullable=True))
    op.add_column("quality_assessments", sa.Column("instrument_version", sa.Integer(), nullable=True))
    op.add_column("quality_assessments", sa.Column("reopen_justification", sa.String(length=4000), nullable=True))

    _create_append_only_triggers(dialect)


def downgrade() -> None:
    dialect = op.get_bind().dialect.name
    _drop_append_only_triggers(dialect)

    with op.batch_alter_table("quality_assessments") as batch:
        batch.drop_column("reopen_justification")
        batch.drop_column("instrument_version")
        batch.drop_column("initial_scores")

    if dialect == "sqlite":
        _drop_sqlite_triggers(DOWNGRADE_REBUILT_TABLES)
    with op.batch_alter_table("duplicate_decisions") as batch:
        batch.drop_column("method")

    with op.batch_alter_table("studies") as batch:
        batch.drop_constraint("ck_study_single_origin", type_="check")
        batch.drop_index("ix_studies_snowball_round_id")
        batch.drop_constraint("fk_studies_snowball_round", type_="foreignkey")
        batch.drop_column("publication_type")
        batch.drop_column("origin")
        batch.drop_column("snowball_round_id")
        batch.alter_column("search_execution_id", existing_type=sa.String(length=64), nullable=False)

    with op.batch_alter_table("raw_imports") as batch:
        batch.drop_constraint("ck_raw_import_single_origin", type_="check")
        batch.drop_index("ix_raw_imports_snowball_round_id")
        batch.drop_constraint("fk_raw_imports_snowball_round", type_="foreignkey")
        batch.drop_column("anomalies")
        batch.drop_column("direction")
        batch.drop_column("snowball_round_id")
        batch.alter_column("search_execution_id", existing_type=sa.String(length=64), nullable=False)

    with op.batch_alter_table("search_executions") as batch:
        batch.drop_column("reported_result_count")
        batch.drop_column("year_to")
        batch.drop_column("year_from")
        batch.drop_column("search_string_version")
    if dialect == "sqlite":
        _create_sqlite_triggers(DOWNGRADE_REBUILT_TABLES)

    op.drop_index("ix_quality_arbitrations_study_id", table_name="quality_arbitrations")
    op.drop_index("ix_quality_arbitrations_project_id", table_name="quality_arbitrations")
    op.drop_table("quality_arbitrations")
    op.drop_index("ix_snowball_rounds_project_id", table_name="snowball_rounds")
    op.drop_table("snowball_rounds")
    op.drop_index("ix_project_gates_project_id", table_name="project_gates")
    op.drop_table("project_gates")
