"""Create append-only audit events."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "003_append_only_audit"
down_revision = "002_projects_members"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("actor_user_id", sa.String(length=64), sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("performed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("previous_value", sa.JSON(), nullable=True),
        sa.Column("new_value", sa.JSON(), nullable=True),
        sa.Column("request_id", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_audit_events_entity_id", "audit_events", ["entity_id"])
    op.create_index("ix_audit_events_actor_user_id", "audit_events", ["actor_user_id"])

    dialect = op.get_bind().dialect.name
    if dialect == "sqlite":
        op.execute(
            "CREATE TRIGGER audit_events_block_update BEFORE UPDATE ON audit_events "
            "BEGIN SELECT RAISE(ABORT, 'audit_events is append-only'); END"
        )
        op.execute(
            "CREATE TRIGGER audit_events_block_delete BEFORE DELETE ON audit_events "
            "BEGIN SELECT RAISE(ABORT, 'audit_events is append-only'); END"
        )
    elif dialect == "postgresql":
        op.execute(
            "CREATE FUNCTION reject_audit_event_mutation() RETURNS trigger AS $$ "
            "BEGIN RAISE EXCEPTION 'audit_events is append-only'; END; "
            "$$ LANGUAGE plpgsql"
        )
        op.execute(
            "CREATE TRIGGER audit_events_block_mutation BEFORE UPDATE OR DELETE ON audit_events "
            "FOR EACH ROW EXECUTE FUNCTION reject_audit_event_mutation()"
        )


def downgrade() -> None:
    dialect = op.get_bind().dialect.name
    if dialect == "sqlite":
        op.execute("DROP TRIGGER IF EXISTS audit_events_block_update")
        op.execute("DROP TRIGGER IF EXISTS audit_events_block_delete")
    elif dialect == "postgresql":
        op.execute("DROP TRIGGER IF EXISTS audit_events_block_mutation ON audit_events")
        op.execute("DROP FUNCTION IF EXISTS reject_audit_event_mutation()")
    op.drop_index("ix_audit_events_actor_user_id", table_name="audit_events")
    op.drop_index("ix_audit_events_entity_id", table_name="audit_events")
    op.drop_table("audit_events")