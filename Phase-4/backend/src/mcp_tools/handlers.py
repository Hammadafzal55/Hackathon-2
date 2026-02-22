"""
MCP Tool Handlers
This module implements the handler functions for all MCP task tools.
Each handler performs the actual task operation and interacts with the database.
"""
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime

from src.models.task import Task, TaskCreate, TaskUpdate, TaskStatus
from src.database.database import get_async_session
from src.mcp_tools.schemas import (
    AddTaskRequest, AddTaskResponse,
    ListTasksRequest, ListTasksResponse,
    UpdateTaskRequest, UpdateTaskResponse,
    CompleteTaskRequest, CompleteTaskResponse,
    DeleteTaskRequest, DeleteTaskResponse
)
from src.mcp_tools.utils import verify_user_exists, validate_user_access, validate_priority, validate_status


async def get_database_session() -> AsyncSession:
    """
    Get an async database session for MCP tool operations.
    This ensures stateless operation with proper session management.

    Returns:
        AsyncSession: Database session
    """
    async_gen = get_async_session()
    session = await async_gen.__anext__()
    return session


async def add_task_handler(request: AddTaskRequest, session: Optional[AsyncSession] = None) -> AddTaskResponse:
    """
    Handler for the add_task MCP tool.
    Creates a new task for the authenticated user.

    Args:
        request: AddTaskRequest containing task details and user_id
        session: Optional database session (for testing)

    Returns:
        AddTaskResponse with created task information
    """
    from src.mcp_tools.utils import require_authentication, stateless_operation

    # Get database session (use injected session or create new one)
    session_provided = session is not None
    if not session_provided:
        session = await get_database_session()

    try:
        # Validate input
        validate_priority(request.priority)

        # Prepare task data
        task_data = {
            "title": request.title,
            "description": request.description,
            "priority": request.priority or 1,
            "user_id": request.user_id
        }

        # Handle due_date if provided
        if request.due_date:
            # Convert timezone-aware datetime to naive if needed
            due_date = request.due_date
            if hasattr(due_date, 'tzinfo') and due_date.tzinfo is not None:
                task_data['due_date'] = due_date.replace(tzinfo=None)
            else:
                task_data['due_date'] = due_date

        # Create task instance
        db_task = Task(**task_data)

        # Add to database
        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)

        # Convert task to dict for response
        task_dict = {
            "id": str(db_task.id),
            "title": db_task.title,
            "description": db_task.description,
            "status": db_task.status,
            "priority": db_task.priority,
            "due_date": db_task.due_date.isoformat() if db_task.due_date else None,
            "user_id": db_task.user_id,
            "created_at": db_task.created_at.isoformat(),
            "updated_at": db_task.updated_at.isoformat(),
            "completed_at": db_task.completed_at.isoformat() if db_task.completed_at else None
        }

        return AddTaskResponse(
            task_id=db_task.id,
            message="Task created successfully",
            task=task_dict
        )

    except Exception as e:
        await session.rollback()
        raise e
    finally:
        if not session_provided:
            await session.close()


async def list_tasks_handler(request: ListTasksRequest, session: Optional[AsyncSession] = None) -> ListTasksResponse:
    """
    Handler for the list_tasks MCP tool.
    Retrieves all tasks for the authenticated user with optional filtering.

    Args:
        request: ListTasksRequest containing user_id and optional filters
        session: Optional database session (for testing)

    Returns:
        ListTasksResponse with list of tasks
    """
    from src.mcp_tools.utils import require_authentication, stateless_operation

    # Get database session (use injected session or create new one)
    session_provided = session is not None
    if not session_provided:
        session = await get_database_session()

    try:
        # Build query for user's tasks
        statement = select(Task).where(Task.user_id == request.user_id)

        # Apply status filter if provided
        if request.status_filter:
            validate_status(request.status_filter)
            statement = statement.where(Task.status == request.status_filter)

        # Apply offset if provided
        if request.offset:
            statement = statement.offset(request.offset)

        # Apply limit if provided
        if request.limit:
            statement = statement.limit(request.limit)

        # Execute query
        result = await session.execute(statement)
        tasks = result.scalars().all()

        # Convert tasks to dict format
        tasks_list = []
        for task in tasks:
            task_dict = {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "user_id": task.user_id,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
            tasks_list.append(task_dict)

        # Get total count (without pagination)
        count_statement = select(Task).where(Task.user_id == request.user_id)
        if request.status_filter:
            count_statement = count_statement.where(Task.status == request.status_filter)

        count_result = await session.execute(count_statement)
        total_count = len(count_result.scalars().all())

        return ListTasksResponse(
            tasks=tasks_list,
            total_count=total_count
        )

    except Exception as e:
        raise e
    finally:
        if not session_provided:
            await session.close()


async def update_task_handler(request: UpdateTaskRequest, session: Optional[AsyncSession] = None) -> UpdateTaskResponse:
    """
    Handler for the update_task MCP tool.
    Updates an existing task for the authenticated user.

    Args:
        request: UpdateTaskRequest containing task_id, user_id, and fields to update
        session: Optional database session (for testing)

    Returns:
        UpdateTaskResponse with updated task information
    """
    from src.mcp_tools.utils import require_authentication, stateless_operation, validate_user_access
    from src.exceptions import TodoNotFoundException

    # Get database session (use injected session or create new one)
    session_provided = session is not None
    if not session_provided:
        session = await get_database_session()

    try:
        # Validate inputs
        if request.priority is not None:
            validate_priority(request.priority)
        if request.status is not None:
            validate_status(request.status)

        # Find the task
        statement = select(Task).where(Task.id == request.task_id)
        result = await session.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            raise TodoNotFoundException(str(request.task_id))

        # Verify user access
        await validate_user_access(db_task.user_id, request.user_id)

        # Update fields
        update_data = request.model_dump(exclude_unset=True, exclude={'user_id', 'task_id'})

        for field, value in update_data.items():
            if value is not None:
                # Handle timezone-aware datetime for due_date
                if field == 'due_date' and hasattr(value, 'tzinfo') and value.tzinfo is not None:
                    value = value.replace(tzinfo=None)
                setattr(db_task, field, value)

        # Commit changes
        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)

        # Convert task to dict for response
        task_dict = {
            "id": str(db_task.id),
            "title": db_task.title,
            "description": db_task.description,
            "status": db_task.status,
            "priority": db_task.priority,
            "due_date": db_task.due_date.isoformat() if db_task.due_date else None,
            "user_id": db_task.user_id,
            "created_at": db_task.created_at.isoformat(),
            "updated_at": db_task.updated_at.isoformat(),
            "completed_at": db_task.completed_at.isoformat() if db_task.completed_at else None
        }

        return UpdateTaskResponse(
            task_id=db_task.id,
            message="Task updated successfully",
            task=task_dict
        )

    except Exception as e:
        await session.rollback()
        raise e
    finally:
        if not session_provided:
            await session.close()


async def complete_task_handler(request: CompleteTaskRequest, session: Optional[AsyncSession] = None) -> CompleteTaskResponse:
    """
    Handler for the complete_task MCP tool.
    Toggles the completion status of a task.

    Args:
        request: CompleteTaskRequest containing task_id and user_id
        session: Optional database session (for testing)

    Returns:
        CompleteTaskResponse with updated task information
    """
    from src.mcp_tools.utils import require_authentication, stateless_operation, validate_user_access
    from src.exceptions import TodoNotFoundException

    # Get database session (use injected session or create new one)
    session_provided = session is not None
    if not session_provided:
        session = await get_database_session()

    try:
        # Find the task
        statement = select(Task).where(Task.id == request.task_id)
        result = await session.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            raise TodoNotFoundException(str(request.task_id))

        # Verify user access
        await validate_user_access(db_task.user_id, request.user_id)

        # Toggle completion status
        if request.complete:
            # Mark as completed
            db_task.status = TaskStatus.COMPLETED
            db_task.completed_at = datetime.utcnow()
        else:
            # Mark as not completed (revert to pending)
            db_task.status = TaskStatus.PENDING
            db_task.completed_at = None

        # Commit changes
        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)

        # Convert task to dict for response
        task_dict = {
            "id": str(db_task.id),
            "title": db_task.title,
            "description": db_task.description,
            "status": db_task.status,
            "priority": db_task.priority,
            "due_date": db_task.due_date.isoformat() if db_task.due_date else None,
            "user_id": db_task.user_id,
            "created_at": db_task.created_at.isoformat(),
            "updated_at": db_task.updated_at.isoformat(),
            "completed_at": db_task.completed_at.isoformat() if db_task.completed_at else None
        }

        return CompleteTaskResponse(
            task_id=db_task.id,
            message="Task completion status updated successfully",
            task=task_dict
        )

    except Exception as e:
        await session.rollback()
        raise e
    finally:
        if not session_provided:
            await session.close()


async def delete_task_handler(request: DeleteTaskRequest, session: Optional[AsyncSession] = None) -> DeleteTaskResponse:
    """
    Handler for the delete_task MCP tool.
    Deletes a task for the authenticated user.

    Args:
        request: DeleteTaskRequest containing task_id and user_id
        session: Optional database session (for testing)

    Returns:
        DeleteTaskResponse confirming deletion
    """
    from src.mcp_tools.utils import require_authentication, stateless_operation, validate_user_access
    from src.exceptions import TodoNotFoundException

    # Get database session (use injected session or create new one)
    session_provided = session is not None
    if not session_provided:
        session = await get_database_session()

    try:
        # Find the task
        statement = select(Task).where(Task.id == request.task_id)
        result = await session.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            raise TodoNotFoundException(str(request.task_id))

        # Verify user access
        await validate_user_access(db_task.user_id, request.user_id)

        # Delete the task
        task_id = db_task.id
        await session.delete(db_task)
        await session.commit()

        return DeleteTaskResponse(
            task_id=task_id,
            message="Task deleted successfully"
        )

    except Exception as e:
        await session.rollback()
        raise e
    finally:
        if not session_provided:
            await session.close()


# Export all handlers
__all__ = [
    'add_task_handler',
    'list_tasks_handler',
    'update_task_handler',
    'complete_task_handler',
    'delete_task_handler'
]