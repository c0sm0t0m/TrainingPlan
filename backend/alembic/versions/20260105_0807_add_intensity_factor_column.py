"""add_intensity_factor_column

Revision ID: c15e6fa130d1
Revises: 2b1a048705cb
Create Date: 2026-01-05 08:07:59.473759+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c15e6fa130d1'
down_revision: Union[str, Sequence[str], None] = '2b1a048705cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add intensity_factor column to garmin_activities table
    op.add_column('garmin_activities', sa.Column('intensity_factor', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove intensity_factor column
    op.drop_column('garmin_activities', 'intensity_factor')
