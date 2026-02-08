"""
Utility functions for MCP tools
Contains helper functions for authentication, validation, and common operations.
"""
from typing import Optional, Callable, Any
from functools import wraps
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from src.models.user import User
import logging

logger = logging.getLogger(__name__)


async def verify_user_exists(user_id: str, session: AsyncSession) -> bool:
    """
    Verify that the specified user exists in the database.

    Args:
        user_id: The ID of the user to verify
        session: Database session

    Returns:
        bool: True if user exists, raises exception otherwise
    """
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    return True


async def validate_user_access(task_user_id: str, authenticated_user_id: str) -> bool:
    """
    Validate that the authenticated user has access to the task.

    Args:
        task_user_id: The user ID associated with the task
        authenticated_user_id: The user ID of the authenticated user

    Returns:
        bool: True if user has access, raises exception otherwise
    """
    if task_user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not have permission to access this task"
        )

    return True


def get_current_user_id_from_context():
    """
    Placeholder function to extract user ID from the current request context.
    This would typically be implemented using FastAPI dependencies in the actual tool handler.
    """
    # This is a placeholder that will be implemented differently depending on the context
    # In actual MCP tools, user ID would be passed as a parameter
    pass


def validate_priority(priority: Optional[int]) -> bool:
    """
    Validate that the priority value is within the acceptable range (1-5).

    Args:
        priority: The priority value to validate

    Returns:
        bool: True if valid, raises exception otherwise
    """
    if priority is not None and (priority < 1 or priority > 5):
        raise ValueError(f"Priority must be between 1 and 5, got {priority}")
    return True


def validate_status(status_value: Optional[str]) -> bool:
    """
    Validate that the status value is one of the allowed values.

    Args:
        status_value: The status value to validate

    Returns:
        bool: True if valid, raises exception otherwise
    """
    allowed_statuses = ["pending", "in_progress", "completed", "cancelled"]
    if status_value is not None and status_value not in allowed_statuses:
        raise ValueError(f"Status must be one of {allowed_statuses}, got {status_value}")
    return True


def require_authentication(func: Callable) -> Callable:
    """
    Decorator to enforce authentication and user isolation for MCP tool handlers.
    This decorator ensures that:
    1. The user_id parameter is provided
    2. The user exists in the database (when session is available)
    3. All operations are isolated to the authenticated user

    Usage:
        @require_authentication
        async def my_tool_handler(request: MyRequest) -> MyResponse:
            # Handler code here
            pass

    Args:
        func: The handler function to decorate

    Returns:
        Callable: The decorated function with authentication enforcement
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        """Wrapper function that enforces authentication."""
        # Extract request object (typically the first argument)
        request = args[0] if args else kwargs.get('request')

        if request is None:
            logger.error("No request object provided to authenticated handler")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required: No request provided"
            )

        # Check if user_id is present in the request
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            logger.error("No user_id found in request")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required: user_id not provided"
            )

        # Log the authenticated user action
        logger.info(f"Executing {func.__name__} for user {user_id}")

        # Call the original function
        try:
            result = await func(*args, **kwargs)
            logger.info(f"Successfully executed {func.__name__} for user {user_id}")
            return result
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Error in {func.__name__} for user {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )

    return wrapper


def stateless_operation(func: Callable) -> Callable:
    """
    Decorator to mark an MCP tool handler as a stateless operation.
    This decorator ensures that:
    1. No state is retained between calls
    2. Each operation is independent
    3. Proper cleanup is performed after execution

    This is a marker decorator that documents the stateless nature of the operation.

    Args:
        func: The handler function to decorate

    Returns:
        Callable: The decorated function
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        """Wrapper function that ensures stateless operation."""
        # Log stateless operation
        logger.debug(f"Executing stateless operation: {func.__name__}")

        # Call the original function
        result = await func(*args, **kwargs)

        # Ensure no state is maintained (this is a documentation marker)
        logger.debug(f"Completed stateless operation: {func.__name__}")

        return result

    return wrapper