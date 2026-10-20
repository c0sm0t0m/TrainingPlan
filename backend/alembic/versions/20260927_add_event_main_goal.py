"""Mark one event as the athlete's main goal

Revision ID: 20260927_goal
Revises: 20260924_wlib
Create Date: 2026-09-27 07:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "20260927_goal"
down_revision = "20260924_wlib"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("events") as batch_op:
        batch_op.add_column(
            sa.Column("is_main_goal", sa.Integer(), nullable=False, server_default="0")
        )
    # The next unfinished event is the main goal until the athlete picks another.
    op.execute(
        """
        UPDATE events
        SET is_main_goal = 1
        WHERE id = (
            SELECT id FROM events
            WHERE is_completed = 0
            ORDER BY event_date ASC
            LIMIT 1
        )
        """
    )


def downgrade() -> None:
    with op.batch_alter_table("events") as batch_op:
        batch_op.drop_column("is_main_goal")
