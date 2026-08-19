"""Add first_name, last_name, timestamps to users table

Revision ID: add_user_names_001
Revises: 
Create Date: 2026-08-19

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "add_user_names_001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("first_name", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("updated_at", sa.DateTime(), nullable=True))

    # Backfill timestamps for existing rows
    op.execute("UPDATE users SET created_at = NOW(), updated_at = NOW() WHERE created_at IS NULL")

    # Make timestamps non-nullable after backfill
    op.alter_column("users", "created_at", nullable=False)
    op.alter_column("users", "updated_at", nullable=False)


def downgrade() -> None:
    op.drop_column("users", "updated_at")
    op.drop_column("users", "created_at")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
