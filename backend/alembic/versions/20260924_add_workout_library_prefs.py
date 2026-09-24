"""Add workout_library_enabled_ids preference on users

Revision ID: 20260924_wlib
Revises: 20260923_icu
Create Date: 2026-09-24 07:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "20260924_wlib"
down_revision = "20260923_icu"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column("workout_library_enabled_ids", sa.Text(), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("workout_library_enabled_ids")
