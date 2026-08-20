"""add is_first_login to users

Revision ID: 2e8910a54f12
Revises: 1d095b5239f3
Create Date: 2026-08-17 10:36:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '2e8910a54f12'
down_revision: str | Sequence[str] | None = '1d095b5239f3'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('is_first_login', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    op.add_column('users', sa.Column('station', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('role', sa.String(length=50), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')
    op.drop_column('users', 'station')
    op.drop_column('users', 'is_first_login')
