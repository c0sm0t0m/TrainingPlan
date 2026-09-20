"""add_garmin_hrv_table

Revision ID: 20260105_add_hrv
Revises: 20260105_0807_add_intensity_factor_column
Create Date: 2026-01-05 15:30:00.000000+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260105_add_hrv'
down_revision: Union[str, Sequence[str], None] = 'c15e6fa130d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create garmin_hrv table for storing daily HRV data."""
    op.create_table(
        'garmin_hrv',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('calendar_date', sa.Date(), nullable=False),
        
        # Daily HRV Summary Metrics
        sa.Column('weekly_avg', sa.Float(), nullable=True),
        sa.Column('last_night_avg', sa.Float(), nullable=True),  # PRIMARY RMSSD VALUE
        sa.Column('last_night_5min_high', sa.Float(), nullable=True),
        
        # Baseline Values
        sa.Column('baseline_low_upper', sa.Float(), nullable=True),
        sa.Column('baseline_balanced_low', sa.Float(), nullable=True),
        sa.Column('baseline_balanced_upper', sa.Float(), nullable=True),
        sa.Column('baseline_marker_value', sa.Float(), nullable=True),
        
        # Status & Feedback
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('feedback_phrase', sa.String(), nullable=True),
        sa.Column('create_timestamp', sa.DateTime(), nullable=True),
        
        # Sleep Window
        sa.Column('sleep_start_time_gmt', sa.DateTime(), nullable=True),
        sa.Column('sleep_end_time_gmt', sa.DateTime(), nullable=True),
        sa.Column('sleep_start_time_local', sa.DateTime(), nullable=True),
        sa.Column('sleep_end_time_local', sa.DateTime(), nullable=True),
        
        # Measurement Window
        sa.Column('start_time_gmt', sa.DateTime(), nullable=True),
        sa.Column('end_time_gmt', sa.DateTime(), nullable=True),
        sa.Column('start_time_local', sa.DateTime(), nullable=True),
        sa.Column('end_time_local', sa.DateTime(), nullable=True),
        
        # Time Series Data (JSON array of readings)
        sa.Column('hrv_readings', sa.JSON(), nullable=True),
        
        # Full raw response
        sa.Column('raw_data', sa.JSON(), nullable=True),
        
        # Metadata
        sa.Column('synced_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_garmin_hrv_id'), 'garmin_hrv', ['id'], unique=False)
    op.create_index(op.f('ix_garmin_hrv_calendar_date'), 'garmin_hrv', ['calendar_date'], unique=False)
    op.create_index('idx_user_date', 'garmin_hrv', ['user_id', 'calendar_date'], unique=True)


def downgrade() -> None:
    """Drop garmin_hrv table."""
    op.drop_index('idx_user_date', table_name='garmin_hrv')
    op.drop_index(op.f('ix_garmin_hrv_calendar_date'), table_name='garmin_hrv')
    op.drop_index(op.f('ix_garmin_hrv_id'), table_name='garmin_hrv')
    op.drop_table('garmin_hrv')
