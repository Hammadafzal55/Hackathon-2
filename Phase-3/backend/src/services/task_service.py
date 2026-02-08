"""
Task service layer for the Todo backend application.
Handles all business logic for task operations with proper user data isolation.
"""

import logging
from typing import List, Optional
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from ..models.task import Task, TaskCreate, TaskUpdate, TaskRead
from ..models.user import User
from ..exceptions import TodoNotFoundException, UnauthorizedException, ValidationException

# Set up logger for this module
logger = logging.getLogger(__name__)


class TaskService:
    """
    Service class that handles all business logic for tasks.
    Ensures proper user data isolation and includes comprehensive error handling.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the TaskService with a database session.

        Args:
            session (AsyncSession): The async database session
        """
        self.session = session

    async def create_task(self, task_create: TaskCreate, user_id: UUID) -> TaskRead:
        """
        Create a new task for the specified user.

        Args:
            task_create (TaskCreate): Task creation data
            user_id (UUID): The ID of the user creating the task

        Returns:
            TaskRead: The created task

        Raises:
            ValidationException: If the task data is invalid
        """
        logger.info(f"Creating task for user {user_id} with title: {getattr(task_create, 'title', 'Unknown')}")

        try:
            # Validate the status field if provided
            if task_create.status:
                from ..models.task import TaskStatus
                valid_statuses = [
                    TaskStatus.PENDING,
                    TaskStatus.IN_PROGRESS,
                    TaskStatus.COMPLETED,
                    TaskStatus.CANCELLED
                ]
                if task_create.status not in valid_statuses:
                    raise ValidationException(f"Invalid status: {task_create.status}. Valid statuses are: {valid_statuses}")

            # Validate priority range
            if task_create.priority and (task_create.priority < 1 or task_create.priority > 5):
                raise ValidationException("Priority must be between 1 and 5")

            # Create the task instance
            db_task = Task.model_validate(task_create.model_dump())
            db_task.user_id = user_id  # Assign task to the specified user

            self.session.add(db_task)
            await self.session.commit()
            await self.session.refresh(db_task)

            logger.info(f"Successfully created task {db_task.id} for user {user_id}")
            return TaskRead.model_validate(db_task)

        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Integrity error while creating task for user {user_id}: {str(e)}", exc_info=True)
            raise ValidationException("Failed to create task due to data integrity issue")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Unexpected error while creating task for user {user_id}: {str(e)}", exc_info=True)
            raise ValidationException(f"Failed to create task: {str(e)}")

    async def get_user_tasks(self, user_id: UUID) -> List[TaskRead]:
        """
        Get all tasks for the specified user.

        Args:
            user_id (UUID): The ID of the user whose tasks to retrieve

        Returns:
            List[TaskRead]: List of tasks for the user
        """
        logger.info(f"Retrieving all tasks for user {user_id}")

        try:
            statement = select(Task).where(Task.user_id == user_id)
            result = await self.session.exec(statement)
            tasks = result.all()

            logger.info(f"Successfully retrieved {len(tasks)} tasks for user {user_id}")
            return [TaskRead.model_validate(task) for task in tasks]
        except Exception as e:
            logger.error(f"Error retrieving tasks for user {user_id}: {str(e)}", exc_info=True)
            raise

    async def get_task_by_id(self, task_id: UUID, user_id: UUID) -> TaskRead:
        """
        Get a specific task by ID for the specified user.

        Args:
            task_id (UUID): The ID of the task to retrieve
            user_id (UUID): The ID of the user requesting the task

        Returns:
            TaskRead: The requested task

        Raises:
            TodoNotFoundException: If the task doesn't exist or doesn't belong to the user
        """
        logger.info(f"Retrieving task {task_id} for user {user_id}")

        try:
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            result = await self.session.exec(statement)
            task = result.first()

            if not task:
                logger.warning(f"Task {task_id} not found for user {user_id}")
                raise TodoNotFoundException(str(task_id))

            logger.info(f"Successfully retrieved task {task_id} for user {user_id}")
            return TaskRead.model_validate(task)
        except TodoNotFoundException:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving task {task_id} for user {user_id}: {str(e)}", exc_info=True)
            raise

    async def update_task(self, task_id: UUID, task_update: TaskUpdate, user_id: UUID) -> TaskRead:
        """
        Update a specific task for the specified user.

        Args:
            task_id (UUID): The ID of the task to update
            task_update (TaskUpdate): Updated task data
            user_id (UUID): The ID of the user updating the task

        Returns:
            TaskRead: The updated task

        Raises:
            TodoNotFoundException: If the task doesn't exist or doesn't belong to the user
            ValidationException: If the update data is invalid
        """
        logger.info(f"Updating task {task_id} for user {user_id}")

        # First, get the existing task to verify it belongs to the user
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await self.session.exec(statement)
        db_task = result.first()

        if not db_task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise TodoNotFoundException(str(task_id))

        # Store original values for logging
        original_title = getattr(db_task, 'title', 'Unknown')
        original_status = getattr(db_task, 'status', 'Unknown')

        try:
            # Validate the status field if provided
            if task_update.status:
                from ..models.task import TaskStatus
                valid_statuses = [
                    TaskStatus.PENDING,
                    TaskStatus.IN_PROGRESS,
                    TaskStatus.COMPLETED,
                    TaskStatus.CANCELLED
                ]
                if task_update.status not in valid_statuses:
                    raise ValidationException(f"Invalid status: {task_update.status}. Valid statuses are: {valid_statuses}")

            # Validate priority range if provided
            if task_update.priority is not None and (task_update.priority < 1 or task_update.priority > 5):
                raise ValidationException("Priority must be between 1 and 5")

            # Update the task with the provided data
            update_data = task_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_task, field, value)

            await self.session.commit()
            await self.session.refresh(db_task)

            logger.info(f"Successfully updated task {task_id} for user {user_id}")
            return TaskRead.model_validate(db_task)

        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Integrity error while updating task {task_id} for user {user_id}: {str(e)}", exc_info=True)
            raise ValidationException("Failed to update task due to data integrity issue")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating task {task_id} for user {user_id}: {str(e)}", exc_info=True)
            raise ValidationException(f"Failed to update task: {str(e)}")

    async def delete_task(self, task_id: UUID, user_id: UUID) -> bool:
        """
        Delete a specific task for the specified user.

        Args:
            task_id (UUID): The ID of the task to delete
            user_id (UUID): The ID of the user deleting the task

        Returns:
            bool: True if the task was deleted, False if it didn't exist

        Raises:
            TodoNotFoundException: If the task doesn't exist or doesn't belong to the user
        """
        logger.info(f"Deleting task {task_id} for user {user_id}")

        # First, get the existing task to verify it belongs to the user
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await self.session.exec(statement)
        db_task = result.first()

        if not db_task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise TodoNotFoundException(str(task_id))

        # Store original values for logging
        original_title = getattr(db_task, 'title', 'Unknown')

        try:
            await self.session.delete(db_task)
            await self.session.commit()

            logger.info(f"Successfully deleted task {task_id} for user {user_id}")
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting task {task_id} for user {user_id}: {str(e)}", exc_info=True)
            raise

    async def toggle_task_completion(self, task_id: UUID, user_id: UUID) -> TaskRead:
        """
        Toggle the completion status of a task for the specified user.

        Args:
            task_id (UUID): The ID of the task to toggle
            user_id (UUID): The ID of the user toggling the task

        Returns:
            TaskRead: The updated task with toggled completion status

        Raises:
            TodoNotFoundException: If the task doesn't exist or doesn't belong to the user
        """
        logger.info(f"Toggling completion status for task {task_id} for user {user_id}")

        from ..models.task import TaskStatus

        # First, get the existing task to verify it belongs to the user
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await self.session.exec(statement)
        db_task = result.first()

        if not db_task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise TodoNotFoundException(str(task_id))

        # Store original status for logging
        original_status = db_task.status

        try:
            # Toggle between completed and pending states
            if db_task.status == TaskStatus.COMPLETED:
                db_task.status = TaskStatus.PENDING
                db_task.completed_at = None
            else:
                db_task.status = TaskStatus.COMPLETED
                # Update completed_at when marking as completed
                db_task.completed_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(db_task)

            logger.info(f"Successfully toggled completion status for task {task_id} from {original_status} to {db_task.status} for user {user_id}")
            return TaskRead.model_validate(db_task)

        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Integrity error while toggling completion status for task {task_id} for user {user_id}: {str(e)}", exc_info=True)
            raise ValidationException("Failed to toggle task completion due to data integrity issue")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error toggling completion status for task {task_id} for user {user_id}: {str(e)}", exc_info=True)
            raise ValidationException(f"Failed to toggle task completion: {str(e)}")