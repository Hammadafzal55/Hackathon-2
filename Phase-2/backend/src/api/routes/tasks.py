"""
Routes for task/todo management in the Todo backend application.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.models.task import Task, TaskCreate, TaskUpdate, TaskRead
from src.models.user import User
from src.database.database import get_async_session
from src.middleware.auth import get_current_user_id
from src.exceptions import TodoNotFoundException, UnauthorizedException

# Set up logger for this module
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/tasks", response_model=List[TaskRead])
async def get_tasks(
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> List[TaskRead]:
    """
    Get all tasks for the authenticated user.

    Args:
        current_user_id (UUID): The ID of the authenticated user (from token)
        session (AsyncSession): Database session

    Returns:
        List[TaskRead]: List of tasks for the authenticated user
    """
    logger.info(f"Incoming request to get tasks for authenticated user_id: {current_user_id}")

    try:
        statement = select(Task).where(Task.user_id == current_user_id)
        result = await session.execute(statement)
        tasks = result.scalars().all()
        logger.info(f"Successfully retrieved {len(tasks)} tasks for user_id: {current_user_id}")
        return tasks
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

    Args:
        task_id (UUID): The ID of the task to retrieve
        current_user_id (UUID): The ID of the authenticated user (from token)
        session (AsyncSession): Database session

    Returns:
        TaskRead: The requested task
    """
    logger.info(f"Incoming request to get task {task_id} for authenticated user_id: {current_user_id}")

    try:
        # Verify the task belongs to the authenticated user
        statement = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
        result = await session.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            logger.warning(f"Task {task_id} not found for user {current_user_id}")
            raise TodoNotFoundException(str(task_id))

        logger.info(f"Successfully retrieved task {task_id} for user {current_user_id}")
        return task
    except TodoNotFoundException:
        logger.warning(f"Task {task_id} not found for user {current_user_id}")
        raise
    except Exception as e:
        logger.error(f"Error retrieving task {task_id} for user {current_user_id}: {str(e)}", exc_info=True)
        raise


@router.post("/tasks", response_model=TaskRead)
async def create_task(
    task: TaskCreate,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> TaskRead:
    """
    Create a new task for the authenticated user.

    Args:
        task (TaskCreate): Task creation data
        current_user_id (UUID): The ID of the authenticated user (from token)
        session (AsyncSession): Database session

    Returns:
        TaskRead: The created task
    """
    logger.info(f"Incoming request to create task for authenticated user_id: {current_user_id}")

    try:
        # Prepare task data from the request body
        task_data = task.model_dump()

        # Handle timezone-aware datetime fields by converting to naive if needed
        if task_data.get('due_date'):
            due_date = task_data['due_date']
            if hasattr(due_date, 'tzinfo') and due_date.tzinfo is not None:
                task_data['due_date'] = due_date.replace(tzinfo=None)

        # Create task instance with data from the request body
        db_task = Task(
            **task_data,
            user_id=current_user_id  # Assign the user_id from the authenticated user
        )
        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)
        logger.info(f"Successfully created task {db_task.id} for user {current_user_id}")
        return db_task
    except Exception as e:
        logger.error(f"Error creating task for user {current_user_id}: {str(e)}", exc_info=True)
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

    Args:
        task_id (UUID): The ID of the task to update
        task_update (TaskUpdate): Updated task data
        current_user_id (UUID): The ID of the authenticated user (from token)
        session (AsyncSession): Database session

    Returns:
        TaskRead: The updated task
    """
    logger.info(f"Incoming request to update task {task_id} for authenticated user_id: {current_user_id}")

    try:
        # Verify the task belongs to the authenticated user
        statement = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
        result = await session.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            logger.warning(f"Task {task_id} not found for user {current_user_id}")
            raise TodoNotFoundException(str(task_id))

        # Store original values for logging
        original_title = getattr(db_task, 'title', 'Unknown')

        # Update the task with the provided data
        update_data = task_update.model_dump(exclude_unset=True)

        # Handle timezone-aware datetime fields by converting to naive if needed
        for field, value in update_data.items():
            if field == 'due_date' and value is not None:
                # Convert timezone-aware datetime to naive
                if hasattr(value, 'tzinfo') and value.tzinfo is not None:
                    value = value.replace(tzinfo=None)
            setattr(db_task, field, value)

        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)

        logger.info(f"Successfully updated task {task_id} for user {current_user_id}")
        return db_task
    except TodoNotFoundException:
        logger.warning(f"Task {task_id} not found for user {current_user_id}")
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id} for user {current_user_id}: {str(e)}", exc_info=True)
        raise


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Delete a specific task for the authenticated user.

    Args:
        task_id (UUID): The ID of the task to delete
        current_user_id (UUID): The ID of the authenticated user (from token)
        session (AsyncSession): Database session

    Returns:
        dict: Success message
    """
    logger.info(f"Incoming request to delete task {task_id} for authenticated user_id: {current_user_id}")

    try:
        # Verify the task belongs to the authenticated user
        statement = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
        result = await session.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            logger.warning(f"Task {task_id} not found for user {current_user_id}")
            raise TodoNotFoundException(str(task_id))

        # Store original values for logging
        original_title = getattr(db_task, 'title', 'Unknown')

        await session.delete(db_task)
        await session.commit()

        logger.info(f"Successfully deleted task {task_id} for user {current_user_id}")
        return {"message": "Task deleted successfully"}
    except TodoNotFoundException:
        logger.warning(f"Task {task_id} not found for user {current_user_id}")
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id} for user {current_user_id}: {str(e)}", exc_info=True)
        raise


@router.patch("/tasks/{task_id}/complete", response_model=TaskRead)
async def toggle_task_completion(
    task_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> TaskRead:
    """
    Toggle the completion status of a task for the authenticated user.

    Args:
        task_id (UUID): The ID of the task to toggle
        current_user_id (UUID): The ID of the authenticated user (from token)
        session (AsyncSession): Database session

    Returns:
        TaskRead: The updated task with toggled completion status
    """
    logger.info(f"Incoming request to toggle completion status for task {task_id} for authenticated user_id: {current_user_id}")

    try:
        # Verify the task belongs to the authenticated user
        statement = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
        result = await session.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            logger.warning(f"Task {task_id} not found for user {current_user_id}")
            raise TodoNotFoundException(str(task_id))

        # Store original status for logging
        original_status = db_task.status

        # Toggle the completion status
        from src.models.task import TaskStatus
        if db_task.status == TaskStatus.COMPLETED:
            db_task.status = TaskStatus.PENDING
            db_task.completed_at = None
        else:
            db_task.status = TaskStatus.COMPLETED
            from datetime import datetime
            db_task.completed_at = datetime.utcnow()

        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)

        logger.info(f"Successfully toggled completion status for task {task_id} from {original_status} to {db_task.status} for user {current_user_id}")
        return db_task
    except TodoNotFoundException:
        logger.warning(f"Task {task_id} not found for user {current_user_id}")
        raise
    except Exception as e:
        logger.error(f"Error toggling completion status for task {task_id} for user {current_user_id}: {str(e)}", exc_info=True)
        raise