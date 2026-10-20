"""Add weight_kg to users for W/kg bike analysis

Revision ID: 20261017_weight
Revises: 20261004_cal
Create Date: 2026-10-17

"""
from alembic import op
import sqlalchemy as sa


revision = "20261017_weight"
down_revision = "20261004_cal"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("weight_kg", sa.Float(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("weight_kg")
