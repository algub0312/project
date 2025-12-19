"""add_x_y_coordinates_and_bigint_id

Revision ID: a1b2c3d4e5f6
Revises: 6a53b0c8c681
Create Date: 2025-11-29 08:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'cd89fb96d882'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add x and y columns
    op.add_column('desks', sa.Column('x', sa.Float(), nullable=True))
    op.add_column('desks', sa.Column('y', sa.Float(), nullable=True))
    
    # Alter id column to BigInteger
    op.alter_column('desks', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True,
               autoincrement=True)


def downgrade() -> None:
    # Remove x and y columns
    op.drop_column('desks', 'y')
    op.drop_column('desks', 'x')
    
    # Revert id column to Integer
    op.alter_column('desks', 'id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True,
               autoincrement=True)
