"""
CLI command handlers for the todo application.

This module provides command handler functions that process CLI arguments
and delegate to the appropriate model functions.
"""

import sys
from typing import List

from src.models.task import (
    Task,
    add_task,
    view_tasks,
    update_task,
    delete_task,
    toggle_status,
)


def cmd_add(args: List[str]) -> None:
    """
    Handle the 'add' command - create a new task.

    Usage: add <title> [--description <text>]

    Args:
        args: Command arguments (title and optional --description flag)

    Raises:
        ValueError: If title is missing or empty
    """
    if not args:
        raise ValueError("Task title is required. Usage: add <title> [--description <text>]")

    # Parse arguments
    title = None
    description = ""
    i = 0

    while i < len(args):
        if args[i] in ("--description", "-d"):
            if i + 1 < len(args):
                description = args[i + 1]
                i += 2
            else:
                raise ValueError("--description requires a value")
        elif title is None:
            title = args[i]
            i += 1
        else:
            # Additional positional arguments are appended to title
            title = f"{title} {args[i]}"
            i += 1

    if not title:
        raise ValueError("Task title is required. Usage: add <title> [--description <text>]")

    # Add the task
    task = add_task(title, description)
    print(f"Task added successfully (ID: {task.task_id})")


def cmd_view(args: List[str]) -> None:
    """
    Handle the 'view' command - display all tasks.

    Usage: view

    Args:
        args: Command arguments (unused)
    """
    tasks = view_tasks()

    if not tasks:
        print("No tasks found. Add your first task to get started!")
        return

    print("\nTasks:")
    for task in tasks:
        status_display = f"[{task.status}]"
        print(f"[{task.task_id}] {status_display} {task.title}")
        if task.description:
            print(f"  Description: {task.description}")
        else:
            print(f"  Description:")
    print()


def cmd_update(args: List[str]) -> None:
    """
    Handle the 'update' command - modify a task.

    Usage: update <task_id> [--title <text>] [--description <text>]

    Args:
        args: Command arguments (task_id and optional flags)

    Raises:
        ValueError: If task_id is missing or invalid
        IndexError: If task_id doesn't exist
    """
    if not args:
        raise ValueError("Task ID is required. Usage: update <task_id> [--title <text>] [--description <text>]")

    # Parse task_id
    try:
        task_id = int(args[0])
    except ValueError:
        raise ValueError(f"Invalid task ID '{args[0]}'. Task ID must be a number.")

    # Parse optional flags
    title = None
    description = None
    i = 1

    while i < len(args):
        if args[i] in ("--title", "-t"):
            if i + 1 < len(args):
                title = args[i + 1]
                i += 2
            else:
                raise ValueError("--title requires a value")
        elif args[i] in ("--description", "-d"):
            if i + 1 < len(args):
                description = args[i + 1]
                i += 2
            else:
                raise ValueError("--description requires a value")
        else:
            raise ValueError(f"Unknown option '{args[i]}'. Use --title or --description.")

    if title is None and description is None:
        raise ValueError("At least one of --title or --description must be specified")

    # Update the task
    task = update_task(task_id, title=title, description=description)
    print(f"Task {task_id} updated successfully")


def cmd_delete(args: List[str]) -> None:
    """
    Handle the 'delete' command - remove a task.

    Usage: delete <task_id>

    Args:
        args: Command arguments (task_id)

    Raises:
        ValueError: If task_id is missing or invalid
        IndexError: If task_id doesn't exist
    """
    if not args:
        raise ValueError("Task ID is required. Usage: delete <task_id>")

    # Parse task_id
    try:
        task_id = int(args[0])
    except ValueError:
        raise ValueError(f"Invalid task ID '{args[0]}'. Task ID must be a number.")

    # Delete the task
    delete_task(task_id)
    print(f"Task {task_id} deleted successfully")


def cmd_complete(args: List[str]) -> None:
    """
    Handle the 'complete' command - toggle task status.

    Usage: complete <task_id>

    Args:
        args: Command arguments (task_id)

    Raises:
        ValueError: If task_id is missing or invalid
        IndexError: If task_id doesn't exist
    """
    if not args:
        raise ValueError("Task ID is required. Usage: complete <task_id>")

    # Parse task_id
    try:
        task_id = int(args[0])
    except ValueError:
        raise ValueError(f"Invalid task ID '{args[0]}'. Task ID must be a number.")

    # Toggle the status
    task = toggle_status(task_id)
    print(f"Task {task_id} marked as {task.status}")
