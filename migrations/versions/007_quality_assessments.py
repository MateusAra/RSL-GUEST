"""Create independent QA assessments."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "007_quality_assessments"
down_revision = "006_triage_votes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "quality_assessments",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("study_id", sa.String(length=64), sa.ForeignKey("studies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewer_user_id", sa.String(length=64), sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("scores", sa.JSON(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("category_scores", sa.JSON(), nullable=False),
        sa.Column("classification", sa.String(length=32), nullable=False),
        sa.Column("confirmed", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("project_id", "study_id", "reviewer_user_id", name="uq_quality_assessment_reviewer"),
    )
    op.create_index("ix_quality_assessments_project_id", "quality_assessments", ["project_id"])
    op.create_index("ix_quality_assessments_study_id", "quality_assessments", ["study_id"])
    op.create_index("ix_quality_assessments_reviewer_user_id", "quality_assessments", ["reviewer_user_id"])


def downgrade() -> None:
    op.drop_index("ix_quality_assessments_reviewer_user_id", table_name="quality_assessments")
    op.drop_index("ix_quality_assessments_study_id", table_name="quality_assessments")
    op.drop_index("ix_quality_assessments_project_id", table_name="quality_assessments")
    op.drop_table("quality_assessments")