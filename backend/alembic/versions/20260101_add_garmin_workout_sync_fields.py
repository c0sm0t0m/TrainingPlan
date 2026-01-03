"""add garmin workout sync fields

Revision ID: 20260101_1230
Revises: 
Create Date: 2026-01-01 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260101_1230'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add Garmin sync tracking fields to workouts table."""
    # Add new columns for Garmin sync tracking
    op.add_column('workouts', sa.Column('garmin_workout_id', sa.String(), nullable=True))
    op.add_column('workouts', sa.Column('garmin_synced_at', sa.DateTime(), nullable=True))
    op.add_column('workouts', sa.Column('garmin_sync_status', sa.String(), server_default='not_synced', nullable=False))


def downgrade() -> None:
    """Remove Garmin sync tracking fields from workouts table."""
    op.drop_column('workouts', 'garmin_sync_status')
    op.drop_column('workouts', 'garmin_synced_at')
    op.drop_column('workouts', 'garmin_workout_id')
