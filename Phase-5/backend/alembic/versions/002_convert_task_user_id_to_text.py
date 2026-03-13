"""Convert task.user_id from UUID to TEXT to match Better Auth string IDs

Revision ID: 002
Revises: 6b1363f45ba3
Create Date: 2026-01-23 11:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '6b1363f45ba3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add a temporary text column to hold the converted values
    op.add_column('task', sa.Column('user_id_temp', sa.Text(), nullable=True))

    # Copy existing UUID values to the new text column as strings
    op.execute("UPDATE task SET user_id_temp = user_id::TEXT")

    # Drop the old UUID column
    op.drop_column('task', 'user_id')

    # Rename the temporary column to user_id
    op.alter_column('task', 'user_id_temp', new_column_name='user_id')

    # Update the column to ensure it's properly typed as TEXT and NOT NULL
    op.alter_column('task', 'user_id', type_=sa.Text(), nullable=False)

    # Recreate the index on the new text column
    op.create_index('ix_task_user_id', 'task', ['user_id'])


def downgrade() -> None:
    # For downgrade, we'll reverse the process
    # Add a temporary UUID column
    op.add_column('task', sa.Column('user_id_temp', postgresql.UUID(as_uuid=True), nullable=True))

    # Copy text values back to UUID (this may fail if values are not valid UUIDs)
    # For demonstration, we'll assume the original UUIDs were preserved in some way
    # In practice, this downgrade may not be perfectly reversible if original UUIDs are lost
    op.execute("""
        UPDATE task
        SET user_id_temp = user_id::UUID
        WHERE user_id ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    """)

    # Drop the old TEXT column
    op.drop_column('task', 'user_id')

    # Rename the temporary column back to user_id
    op.alter_column('task', 'user_id_temp', new_column_name='user_id')

    # Update the column to ensure it's properly typed as UUID and NOT NULL
    op.alter_column('task', 'user_id', type_=postgresql.UUID(as_uuid=True), nullable=False)

    # Recreate the index on the UUID column
    op.create_index('ix_task_user_id', 'task', ['user_id'])