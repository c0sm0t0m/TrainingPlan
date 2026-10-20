"""Indexes for calendar activity and workout lookups

Revision ID: 20261004_cal
Revises: 20260927_match
Create Date: 2026-10-04 21:10:00.000000

"""
from alembic import op


revision = "20261004_cal"
down_revision = "20260927_match"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_garmin_activities_user_start",
        "garmin_activities",
        ["user_id", "start_time_local"],
    )
    op.create_index(
        "ix_workouts_training_plan_id",
        "workouts",
        ["training_plan_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_workouts_training_plan_id", table_name="workouts")
    op.drop_index("ix_garmin_activities_user_start", table_name="garmin_activities")
