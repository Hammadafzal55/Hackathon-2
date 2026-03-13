"""Add advanced features: tags, recurrence, reminders, notifications

Revision ID: 004
Revises: 002
Create Date: 2026-03-07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to tasks table
    op.add_column('task', sa.Column('tags', JSONB, nullable=False, server_default='[]'))
    op.add_column('task', sa.Column('recurrence_rule', JSONB, nullable=True))
    op.add_column('task', sa.Column('recurrence_parent_id', UUID(as_uuid=True), nullable=True))
    op.add_column('task', sa.Column('next_occurrence', sa.DateTime(), nullable=True))

    # Add FK constraint for recurrence_parent_id self-reference
    op.create_foreign_key(
        'fk_task_recurrence_parent',
        'task', 'task',
        ['recurrence_parent_id'], ['id'],
        ondelete='SET NULL'
    )

    # GIN index on tags for fast containment queries
    op.create_index('ix_task_tags_gin', 'task', ['tags'], postgresql_using='gin')

    # Index on next_occurrence for cron queries
    op.create_index('ix_task_next_occurrence', 'task', ['next_occurrence'])

    # Create reminders table
    op.create_table(
        'reminder',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('task_id', UUID(as_uuid=True), sa.ForeignKey('task.id', ondelete='CASCADE'), nullable=False),
        sa.Column('lead_time_minutes', sa.Integer(), nullable=False),
        sa.Column('fire_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Partial index on pending reminders for efficient cron queries
    op.create_index(
        'ix_reminder_fire_at_pending',
        'reminder',
        ['fire_at'],
        postgresql_where=sa.text("status = 'pending'")
    )

    # Create notifications table
    op.create_table(
        'notification',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('task_id', UUID(as_uuid=True), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Index for notification queries by user
    op.create_index(
        'ix_notification_user_read_created',
        'notification',
        ['user_id', 'read', 'created_at']
    )

    # Unique constraint for recurrence dedup
    op.create_unique_constraint(
        'uq_task_recurrence_parent_due_date',
        'task',
        ['recurrence_parent_id', 'due_date']
    )


def downgrade() -> None:
    op.drop_constraint('uq_task_recurrence_parent_due_date', 'task', type_='unique')
    op.drop_index('ix_notification_user_read_created', table_name='notification')
    op.drop_table('notification')
    op.drop_index('ix_reminder_fire_at_pending', table_name='reminder')
    op.drop_table('reminder')
    op.drop_index('ix_task_next_occurrence', table_name='task')
    op.drop_index('ix_task_tags_gin', table_name='task')
    op.drop_constraint('fk_task_recurrence_parent', 'task', type_='foreignkey')
    op.drop_column('task', 'next_occurrence')
    op.drop_column('task', 'recurrence_parent_id')
    op.drop_column('task', 'recurrence_rule')
    op.drop_column('task', 'tags')
