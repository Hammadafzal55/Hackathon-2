"""
Routes for task/todo management in the Todo backend application.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, cast, text
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID
from datetime import datetime

from src.models.task import Task, TaskCreate, TaskUpdate, TaskRead
from src.models.reminder import Reminder
from src.database.database import get_async_session
from src.middleware.auth import get_current_user_id
from src.exceptions import TodoNotFoundException
from src.services.event_publisher import publish_task_event

# Set up logger for this module
logger = logging.getLogger(__name__)

router = APIRouter()


class TaskListResponse:
    """Paginated task list response."""
    def __init__(self, tasks: List[TaskRead], total_count: int):
        self.tasks = tasks
        self.total_count = total_count


@router.get("/tasks")
async def get_tasks(
    search: Optional[str] = Query(None, description="Search in title and description"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority (comma-separated)"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    due_before: Optional[str] = Query(None, description="Filter tasks due before date (ISO)"),
    due_after: Optional[str] = Query(None, description="Filter tasks due after date (ISO)"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_dir: Optional[str] = Query("desc", description="Sort direction: asc or desc"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Get tasks for the authenticated user with optional search, filter, and sort.
    """
    logger.info(f"Getting tasks for user {current_user_id} with search={search}, status={status}")

    try:
        statement = select(Task).where(Task.user_id == current_user_id)

        # Search filter (ILIKE on title/description)
        if search:
            search_term = f"%{search}%"
            from sqlalchemy import or_
            statement = statement.where(
                or_(
                    Task.title.ilike(search_term),
                    Task.description.ilike(search_term)
                )
            )

        # Status filter
        if status:
            statement = statement.where(Task.status == status)

        # Priority filter (comma-separated values)
        if priority:
            priorities = [int(p.strip()) for p in priority.split(',') if p.strip().isdigit()]
            if priorities:
                statement = statement.where(Task.priority.in_(priorities))

        # Tags filter (JSONB containment: task.tags @> ['tag1', 'tag2'])
        if tags:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            for tag in tag_list:
                statement = statement.where(
                    Task.tags.cast(JSONB).contains(cast([tag], JSONB))
                )

        # Due date filters
        if due_before:
            try:
                due_before_dt = datetime.fromisoformat(due_before.replace('Z', '+00:00'))
                statement = statement.where(Task.due_date <= due_before_dt.replace(tzinfo=None))
            except ValueError:
                pass

        if due_after:
            try:
                due_after_dt = datetime.fromisoformat(due_after.replace('Z', '+00:00'))
                statement = statement.where(Task.due_date >= due_after_dt.replace(tzinfo=None))
            except ValueError:
                pass

        # Count total matching tasks
        count_stmt = select(func.count()).select_from(statement.subquery())
        total_count = (await session.execute(count_stmt)).scalar_one()

        # Sort
        sort_column_map = {
            'created_at': Task.created_at,
            'updated_at': Task.updated_at,
            'due_date': Task.due_date,
            'priority': Task.priority,
            'title': Task.title,
            'status': Task.status,
        }
        sort_col = sort_column_map.get(sort_by or 'created_at', Task.created_at)
        if sort_dir == 'asc':
            statement = statement.order_by(sort_col.asc().nullslast())
        else:
            statement = statement.order_by(sort_col.desc().nullslast())

        # Pagination
        statement = statement.offset(offset).limit(limit)

        result = await session.execute(statement)
        tasks = result.scalars().all()

        logger.info(f"Retrieved {len(tasks)} tasks (total={total_count}) for user {current_user_id}")
        return {"tasks": [TaskRead.model_validate(t) for t in tasks], "total_count": total_count}

    except Exception as e:
        logger.error(f"Error retrieving tasks for user {current_user_id}: {str(e)}", exc_info=True)
        raise


@router.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> TaskRead:
    """
    Get a specific task by ID for the authenticated user.
    """
    logger.info(f"Getting task {task_id} for user {current_user_id}")

    try:
        statement = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
        result = await session.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            raise TodoNotFoundException(str(task_id))

        return TaskRead.model_validate(task)
    except TodoNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {str(e)}", exc_info=True)
        raise


@router.post("/tasks", response_model=TaskRead)
async def create_task(
    task: TaskCreate,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> TaskRead:
    """
    Create a new task for the authenticated user.
    """
    logger.info(f"Creating task for user {current_user_id}")

    try:
        task_data = task.model_dump(exclude={'reminders'})

        # Handle timezone-aware datetime fields
        if task_data.get('due_date'):
            due_date = task_data['due_date']
            if hasattr(due_date, 'tzinfo') and due_date.tzinfo is not None:
                task_data['due_date'] = due_date.replace(tzinfo=None)

        db_task = Task(**task_data, user_id=current_user_id)
        session.add(db_task)
        await session.flush()  # get db_task.id

        # Create reminders if provided
        if task.reminders:
            from src.services.reminder_service import create_task_reminders
            await create_task_reminders(session, db_task, task.reminders)

        await session.commit()
        await session.refresh(db_task)

        # Fire any reminders whose fire_at is already in the past (works without Dapr)
        if task.reminders:
            from src.services.reminder_service import check_due_reminders
            await check_due_reminders(session)

        # Publish event (non-blocking)
        await publish_task_event(
            event_type="task.created",
            task_id=str(db_task.id),
            user_id=str(current_user_id),
            has_recurrence=bool(db_task.recurrence_rule),
            has_reminders=bool(task.reminders),
        )

        logger.info(f"Created task {db_task.id} for user {current_user_id}")
        return TaskRead.model_validate(db_task)
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}", exc_info=True)
        raise


@router.put("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> TaskRead:
    """
    Update a specific task for the authenticated user.
    """
    logger.info(f"Updating task {task_id} for user {current_user_id}")

    try:
        statement = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
        result = await session.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            raise TodoNotFoundException(str(task_id))

        update_data = task_update.model_dump(exclude_unset=True, exclude={'reminders'})

        for field, value in update_data.items():
            if field == 'due_date' and value is not None:
                if hasattr(value, 'tzinfo') and value.tzinfo is not None:
                    value = value.replace(tzinfo=None)
            setattr(db_task, field, value)

        # Update reminders if provided
        if task_update.reminders is not None:
            # Delete existing pending reminders and recreate
            existing = await session.execute(
                select(Reminder).where(Reminder.task_id == task_id, Reminder.status == 'pending')
            )
            for r in existing.scalars().all():
                await session.delete(r)

            if task_update.reminders and db_task.due_date:
                from src.services.reminder_service import create_task_reminders
                await create_task_reminders(session, db_task, task_update.reminders)

        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)

        # Publish event (non-blocking)
        await publish_task_event(
            event_type="task.updated",
            task_id=str(task_id),
            user_id=str(current_user_id),
            changed_fields=list(update_data.keys()),
        )

        logger.info(f"Updated task {task_id} for user {current_user_id}")
        return TaskRead.model_validate(db_task)
    except TodoNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}", exc_info=True)
        raise


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Delete a specific task for the authenticated user.
    """
    logger.info(f"Deleting task {task_id} for user {current_user_id}")

    try:
        statement = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
        result = await session.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            raise TodoNotFoundException(str(task_id))

        await session.delete(db_task)
        await session.commit()

        # Publish event (non-blocking)
        await publish_task_event(
            event_type="task.deleted",
            task_id=str(task_id),
            user_id=str(current_user_id),
        )

        logger.info(f"Deleted task {task_id} for user {current_user_id}")
        return {"message": "Task deleted successfully"}
    except TodoNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}", exc_info=True)
        raise


@router.patch("/tasks/{task_id}/complete", response_model=TaskRead)
async def toggle_task_completion(
    task_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> TaskRead:
    """
    Toggle the completion status of a task for the authenticated user.
    """
    logger.info(f"Toggling completion for task {task_id} for user {current_user_id}")

    try:
        statement = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
        result = await session.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            raise TodoNotFoundException(str(task_id))

        from src.models.task import TaskStatus
        if db_task.status == TaskStatus.COMPLETED:
            db_task.status = TaskStatus.PENDING
            db_task.completed_at = None
        else:
            db_task.status = TaskStatus.COMPLETED
            db_task.completed_at = datetime.utcnow()

        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)

        await publish_task_event(
            event_type="task.completed" if db_task.status == TaskStatus.COMPLETED else "task.reopened",
            task_id=str(task_id),
            user_id=str(current_user_id),
        )

        logger.info(f"Toggled task {task_id} to {db_task.status} for user {current_user_id}")
        return TaskRead.model_validate(db_task)
    except TodoNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error toggling task {task_id}: {str(e)}", exc_info=True)
        raise
