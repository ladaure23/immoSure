"""Add nom column to biens table

Revision ID: 003
Revises: 002
"""
from typing import Union
import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("biens", sa.Column("nom", sa.String(200), nullable=True))


def downgrade() -> None:
    op.drop_column("biens", "nom")
