"""
Models package - Contains data models and business logic.

This package provides the Task model and all task-related operations.
"""

from src.models.task import (
    Task,
    add_task,
    get_task,
    view_tasks,
    update_task,
    delete_task,
    toggle_status,
    validate_title,
    clear_tasks,
)
