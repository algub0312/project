"""Merge phantom branches

Revision ID: 92fb164e2b4b
Revises: 0a7e8259edce, 4e0f8c917225
Create Date: 2025-11-12 16:09:37.401383

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92fb164e2b4b'
down_revision: Union[str, Sequence[str], None] = ('0a7e8259edce', '4e0f8c917225')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
