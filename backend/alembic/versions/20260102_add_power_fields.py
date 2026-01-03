"""add power fields to garmin activities

Revision ID: 20260102_add_power
Revises: 20260101_add_garmin_workout_sync_fields
Create Date: 2026-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260102_add_power'
down_revision = '20260101_add_garmin_workout_sync_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Add power data fields for cycling activities"""
    op.add_column('garmin_activities', sa.Column('average_power_watts', sa.Float(), nullable=True))
    op.add_column('garmin_activities', sa.Column('max_power_watts', sa.Float(), nullable=True))
    op.add_column('garmin_activities', sa.Column('normalized_power_watts', sa.Float(), nullable=True))
    op.add_column('garmin_activities', sa.Column('threshold_power_watts', sa.Float(), nullable=True))


def downgrade():
    """Remove power data fields"""
    op.drop_column('garmin_activities', 'threshold_power_watts')
    op.drop_column('garmin_activities', 'normalized_power_watts')
    op.drop_column('garmin_activities', 'max_power_watts')
    op.drop_column('garmin_activities', 'average_power_watts')
