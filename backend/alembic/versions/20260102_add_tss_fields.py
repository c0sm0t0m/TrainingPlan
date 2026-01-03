"""add tss fields

Revision ID: 20260102_add_tss
Revises: 20260102_add_power_fields
Create Date: 2026-01-02 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260102_add_tss'
down_revision = '20260102_add_power_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add TSS fields to workouts and garmin_activities tables"""
    # Add tss field to workouts table
    op.add_column('workouts', sa.Column('tss', sa.Integer(), nullable=True))
    
    # Add calculated_tss field to garmin_activities table
    op.add_column('garmin_activities', sa.Column('calculated_tss', sa.Float(), nullable=True))


def downgrade() -> None:
    """Remove TSS fields"""
    # Remove tss field from workouts table
    op.drop_column('workouts', 'tss')
    
    # Remove calculated_tss field from garmin_activities table
    op.drop_column('garmin_activities', 'calculated_tss')
