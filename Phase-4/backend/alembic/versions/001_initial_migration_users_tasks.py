"""Initial migration for users and tasks tables

Revision ID: 001
Revises:
Create Date: 2026-01-14 10:00:00.000000

"""
from typing import Sequence, Union
from datetime import datetime
import uuid

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table('user',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow),
    )

    # Create indexes for user table
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)

    # Create tasks table
    op.create_table('task',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('status', sa.String(length=20), default='pending'),
        sa.Column('priority', sa.Integer(), default=1),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('completed_at', sa.DateTime(), nullable=True),

        # Foreign key constraint
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    )

    # Create indexes for task table
    op.create_index(op.f('ix_task_user_id'), 'task', ['user_id'])
    op.create_index(op.f('ix_task_status'), 'task', ['status'])


def downgrade() -> None:
    # Drop tasks table first (due to foreign key dependency)
    op.drop_index(op.f('ix_task_status'), table_name='task')
    op.drop_index(op.f('ix_task_user_id'), table_name='task')
    op.drop_table('task')

    # Drop users table
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')