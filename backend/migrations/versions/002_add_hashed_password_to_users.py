"""Add hashed_password column to users table.

Revision ID: 002_add_hashed_password
Revises: 001_initial_schema
Create Date: 2026-05-29
"""

from collections.abc import Sequence

from alembic import op

revision: str = "002_add_hashed_password"
down_revision: str | None = "001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add hashed_password column to users."""
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255)")


def downgrade() -> None:
    """Remove hashed_password column from users."""
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS hashed_password")
