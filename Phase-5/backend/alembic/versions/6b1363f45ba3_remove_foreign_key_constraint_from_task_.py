"""Remove foreign key constraint from task user_id for testing

Revision ID: 6b1363f45ba3
Revises: 001
Create Date: 2026-01-15 12:21:05.747667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6b1363f45ba3'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the foreign key constraint from task table
    op.drop_constraint(op.f('task_user_id_fkey'), 'task', type_='foreignkey')
    # Drop the index that was created for the foreign key
    op.drop_index(op.f('ix_task_user_id'), table_name='task')


def downgrade() -> None:
    # Recreate the index for user_id
    op.create_index(op.f('ix_task_user_id'), 'task', ['user_id'])
    # Recreate the foreign key constraint
    op.create_foreign_key(op.f('task_user_id_fkey'), 'task', 'user', ['user_id'], ['id'])