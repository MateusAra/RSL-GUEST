"""Create independent project-scoped triage votes."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "006_triage_votes"
down_revision = "005_search_import_deduplication"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "triage_votes",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("study_id", sa.String(length=64), sa.ForeignKey("studies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("phase", sa.Integer(), nullable=False),
        sa.Column("reviewer_user_id", sa.String(length=64), sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("vote", sa.String(length=16), nullable=False),
        sa.Column("criterion_id", sa.String(length=20), nullable=True),
        sa.Column("confirmed", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint(
            "project_id", "study_id", "phase", "reviewer_user_id", name="uq_triage_vote_reviewer"
        ),
    )
    op.create_index("ix_triage_votes_project_id", "triage_votes", ["project_id"])
    op.create_index("ix_triage_votes_study_id", "triage_votes", ["study_id"])
    op.create_index("ix_triage_votes_reviewer_user_id", "triage_votes", ["reviewer_user_id"])


def downgrade() -> None:
    op.drop_index("ix_triage_votes_reviewer_user_id", table_name="triage_votes")
    op.drop_index("ix_triage_votes_study_id", table_name="triage_votes")
    op.drop_index("ix_triage_votes_project_id", table_name="triage_votes")
    op.drop_table("triage_votes")