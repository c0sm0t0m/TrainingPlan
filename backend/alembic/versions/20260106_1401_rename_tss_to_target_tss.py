"""Rename tss column to target_tss in workouts table

Revision ID: 20260106_1401
Revises: a4252933590c
Create Date: 2026-01-06 14:01:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260106_1401'
down_revision = 'a4252933590c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Rename tss to target_tss for clarity"""
    # SQLite doesn't support ALTER COLUMN directly, so we use batch operations
    with op.batch_alter_table('workouts') as batch_op:
        batch_op.alter_column('tss', new_column_name='target_tss')


def downgrade() -> None:
    """Revert target_tss back to tss"""
    with op.batch_alter_table('workouts') as batch_op:
        batch_op.alter_column('target_tss', new_column_name='tss')
