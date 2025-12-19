"""remove redundant ids from related tables

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2025-11-30 12:56:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # desk_config: Remove id column, make desk_id primary key
    op.drop_constraint('desk_config_pkey', 'desk_config', type_='primary')
    op.drop_column('desk_config', 'id')
    op.create_primary_key('desk_config_pkey', 'desk_config', ['desk_id'])
    
    # desk_state: Remove id column, make desk_id primary key
    op.drop_constraint('desk_state_pkey', 'desk_state', type_='primary')
    op.drop_column('desk_state', 'id')
    op.create_primary_key('desk_state_pkey', 'desk_state', ['desk_id'])
    
    # desk_usage: Remove id column, make desk_id primary key
    op.drop_constraint('desk_usage_pkey', 'desk_usage', type_='primary')
    op.drop_column('desk_usage', 'id')
    op.create_primary_key('desk_usage_pkey', 'desk_usage', ['desk_id'])


def downgrade() -> None:
    # Reverse for desk_usage
    op.drop_constraint('desk_usage_pkey', 'desk_usage', type_='primary')
    op.add_column('desk_usage', sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.create_primary_key('desk_usage_pkey', 'desk_usage', ['id'])
    
    # Reverse for desk_state
    op.drop_constraint('desk_state_pkey', 'desk_state', type_='primary')
    op.add_column('desk_state', sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.create_primary_key('desk_state_pkey', 'desk_state', ['id'])
    
    # Reverse for desk_config
    op.drop_constraint('desk_config_pkey', 'desk_config', type_='primary')
    op.add_column('desk_config', sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.create_primary_key('desk_config_pkey', 'desk_config', ['id'])
