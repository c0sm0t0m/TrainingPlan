"""add_structured_workout_json_column

Revision ID: 11ce50666329
Revises: 3ad68a2e7b47
Create Date: 2026-01-06 08:34:18.016438+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11ce50666329'
down_revision: Union[str, Sequence[str], None] = '3ad68a2e7b47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('workouts', sa.Column('structured_workout_json', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('workouts', 'structured_workout_json')
