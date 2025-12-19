"""update foreign keys to bigint

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-29 15:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update desk_config.desk_id to BigInteger
    op.alter_column('desk_config', 'desk_id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False)
    
    # Update desk_state.desk_id to BigInteger
    op.alter_column('desk_state', 'desk_id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False)
    
    # Update desk_usage.desk_id to BigInteger
    op.alter_column('desk_usage', 'desk_id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False)
    
    # Update desk_errors.desk_id to BigInteger
    op.alter_column('desk_errors', 'desk_id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False)


def downgrade() -> None:
    # Revert desk_errors.desk_id to Integer
    op.alter_column('desk_errors', 'desk_id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    
    # Revert desk_usage.desk_id to Integer
    op.alter_column('desk_usage', 'desk_id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    
    # Revert desk_state.desk_id to Integer
    op.alter_column('desk_state', 'desk_id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    
    # Revert desk_config.desk_id to Integer
    op.alter_column('desk_config', 'desk_id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False)
