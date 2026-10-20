"""Add planned workout ↔ Garmin activity match link fields

Revision ID: 20260927_match
Revises: 20260927_goal
Create Date: 2026-09-27 08:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "20260927_match"
down_revision = "20260927_goal"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("workouts") as batch_op:
        batch_op.add_column(sa.Column("matched_activity_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("match_confidence", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("match_status", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("matched_at", sa.DateTime(), nullable=True))
        batch_op.create_index("ix_workouts_matched_activity_id", ["matched_activity_id"])
        batch_op.create_foreign_key(
            "fk_workouts_matched_activity_id",
            "garmin_activities",
            ["matched_activity_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("workouts") as batch_op:
        batch_op.drop_constraint("fk_workouts_matched_activity_id", type_="foreignkey")
        batch_op.drop_index("ix_workouts_matched_activity_id")
        batch_op.drop_column("matched_at")
        batch_op.drop_column("match_status")
        batch_op.drop_column("match_confidence")
        batch_op.drop_column("matched_activity_id")
