"""add_activation_date_to_training_plans

Revision ID: a4252933590c
Revises: 11ce50666329
Create Date: 2026-01-06 13:43:31.000620+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4252933590c'
down_revision: Union[str, Sequence[str], None] = '11ce50666329'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add activation_date column to training_plans table
    op.add_column('training_plans', sa.Column('activation_date', sa.Date(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove activation_date column
    op.drop_column('training_plans', 'activation_date')
