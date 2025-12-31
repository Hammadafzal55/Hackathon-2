"""
Task model and operations for the in-memory todo application.

This module provides the Task dataclass and all task-related operations
including add, view, update, delete, and status toggle functionality.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Task:
    """
    Represents a single todo item in the in-memory list.

    Attributes:
        task_id: Unique sequential identifier (1, 2, 3, ...)
        title: Task name (mandatory, non-empty)
        description: Additional details (optional, can be empty string)
        status: Current task state, either "incomplete" or "complete"
    """
    task_id: int
    title: str
    description: str
    status: str


# Global in-memory task storage
_tasks: List[Task] = []


def _next_id() -> int:
    """
    Calculate the next available task ID.

    Returns:
        Next sequential task ID (len(_tasks) + 1)
    """
    return len(_tasks) + 1


def _reassign_ids() -> None:
    """
    Reassign sequential IDs to all tasks after deletion.

    Ensures task IDs remain sequential (1, 2, 3, ..., N) after
    any task is removed from the list.
    """
    for idx, task in enumerate(_tasks, start=1):
        task.task_id = idx


def validate_title(title: str) -> None:
    """
    Validate that task title is non-empty and not whitespace-only.

    Args:
        title: Task title to validate

    Raises:
        ValueError: If title is empty or whitespace-only
    """
    if not title or not title.strip():
        raise ValueError("Task title cannot be empty")


def get_task(task_id: int) -> Task:
    """
    Retrieve a task by its ID.

    Args:
        task_id: Task ID to retrieve (1-indexed)

    Returns:
        Task object with the specified ID

    Raises:
        IndexError: If task_id is not found or out of range
    """
    if task_id < 1 or task_id > len(_tasks):
        raise IndexError(f"Task with ID {task_id} not found")
    return _tasks[task_id - 1]


def add_task(title: str, description: str = "") -> Task:
    """
    Add a new task to the in-memory list.

    Args:
        title: Task name (mandatory, non-empty)
        description: Additional task details (optional, defaults to empty string)

    Returns:
        The newly created Task object

    Raises:
        ValueError: If title is empty or whitespace-only
    """
    validate_title(title)

    task = Task(
        task_id=_next_id(),
        title=title.strip(),
        description=description.strip() if description else "",
        status="incomplete"
    )
    _tasks.append(task)
    return task


def view_tasks() -> List[Task]:
    """
    Get all tasks in the in-memory list.

    Returns:
        List of all Task objects (may be empty)
    """
    return _tasks.copy()


def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Task:
    """
    Update an existing task's title and/or description.

    Args:
        task_id: ID of the task to update (1-indexed)
        title: New title (optional, if provided must be non-empty)
        description: New description (optional)

    Returns:
        The updated Task object

    Raises:
        IndexError: If task_id is not found
        ValueError: If title is provided but empty/whitespace-only
    """
    task = get_task(task_id)

    if title is not None:
        validate_title(title)
        task.title = title.strip()

    if description is not None:
        task.description = description.strip()

    return task


def delete_task(task_id: int) -> Task:
    """
    Delete a task from the in-memory list.

    After deletion, all remaining tasks are reindexed to maintain
    sequential 1-to-N IDs.

    Args:
        task_id: ID of the task to delete (1-indexed)

    Returns:
        The deleted Task object

    Raises:
        IndexError: If task_id is not found
    """
    task = get_task(task_id)
    _tasks.remove(task)
    _reassign_ids()
    return task


def toggle_status(task_id: int) -> Task:
    """
    Toggle a task's status between "incomplete" and "complete".

    Args:
        task_id: ID of the task to toggle (1-indexed)

    Returns:
        The updated Task object with toggled status

    Raises:
        IndexError: If task_id is not found
    """
    task = get_task(task_id)

    if task.status == "incomplete":
        task.status = "complete"
    else:
        task.status = "incomplete"

    return task


def clear_tasks() -> None:
    """
    Clear all tasks from the in-memory list.

    This is primarily useful for testing purposes.
    """
    _tasks.clear()
