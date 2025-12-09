"""Second phantom migration to satisfy reference

Revision ID: 0a7e8259edce
Revises: 5b76b5618c4f
Create Date: 2024-11-12 12:00:01.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0a7e8259edce'
down_revision = '5b76b5618c4f'
branch_labels = None
depends_on = None

def upgrade():
    # Empty upgrade - this is just to satisfy the phantom reference
    pass

def downgrade():
    # Empty downgrade
    pass
