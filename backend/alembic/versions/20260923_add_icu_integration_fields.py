"""Add Intervals.icu integration fields on users and workouts

Revision ID: 20260923_icu
Revises: 20260106_1401
Create Date: 2026-09-23 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '20260923_icu'
down_revision = '20260106_1401'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('icu_api_key', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('icu_athlete_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('icu_connected', sa.Boolean(), server_default='0', nullable=True))
        batch_op.add_column(sa.Column('icu_last_sync', sa.DateTime(), nullable=True))

    with op.batch_alter_table('workouts') as batch_op:
        batch_op.add_column(sa.Column('icu_external_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('icu_synced_at', sa.DateTime(), nullable=True))
        batch_op.add_column(
            sa.Column('icu_sync_status', sa.String(), server_default='not_synced', nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table('workouts') as batch_op:
        batch_op.drop_column('icu_sync_status')
        batch_op.drop_column('icu_synced_at')
        batch_op.drop_column('icu_external_id')

    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('icu_last_sync')
        batch_op.drop_column('icu_connected')
        batch_op.drop_column('icu_athlete_id')
        batch_op.drop_column('icu_api_key')
