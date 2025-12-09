"""Phantom migration to satisfy reference

Revision ID: 5b76b5618c4f
Revises: 
Create Date: 2024-11-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5b76b5618c4f'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Empty upgrade - this is just to satisfy the phantom reference
    pass

def downgrade():
    # Empty downgrade
    pass
