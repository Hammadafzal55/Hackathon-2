"""
Interactive CLI interface for the todo application.

This module provides a menu-driven interactive interface where users
can manage tasks through a continuous loop with numbered menu options.
"""

import sys
from typing import Optional

from src.models.task import (
    add_task,
    view_tasks,
    update_task,
    delete_task,
    toggle_status,
    validate_title,
)


def clear_screen() -> None:
    """Clear the terminal screen."""
    print("\033[H\033[J", end="")


def print_header() -> None:
    """Print the application header."""
    # Terminal escape codes for colors (chalk-like)
    cyan = "\033[96m"
    yellow = "\033[93m"
    green = "\033[92m"
    reset = "\033[0m"
    bold = "\033[1m"

    print(f"{cyan}{'=' * 60}{reset}")
    print(f"{bold}{yellow}          📝 TODO IN-MEMORY CLI APPLICATION{reset}")
    print(f"{green}             Created by hammadafzal{reset}")
    print(f"{cyan}{'=' * 60}{reset}")
    print()


def print_menu() -> None:
    """Print the main menu options."""
    # Terminal escape codes
    blue = "\033[94m"
    reset = "\033[0m"
    bold = "\033[1m"

    print(f"{bold}What would you like to do?{reset}")
    print()
    print(f"  {blue}[1]{reset} ➕ Add Task")
    print(f"  {blue}[2]{reset} 📋 View Tasks")
    print(f"  {blue}[3]{reset} ✏️  Update Task")
    print(f"  {blue}[4]{reset} 🗑️  Delete Task")
    print(f"  {blue}[5]{reset} ✅ Mark Complete/Incomplete")
    print(f"  {blue}[6]{reset} 🚪 Exit")
    print()


def get_input(prompt: str) -> str:
    """Get user input with prompt."""
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return ""


def press_enter_to_continue() -> None:
    """Wait for user to press Enter."""
    input("\nPress Enter to continue...")


def handle_add_task() -> None:
    """Handle the Add Task menu option."""
    magenta = "\033[95m"
    reset = "\033[0m"
    print(f"\n{magenta}--- ➕ ADD NEW TASK ---{reset}\n")

    title = get_input("Enter task title: ")
    if not title:
        print(f"\n\033[91mError: Task title cannot be empty\033[0m")
        return

    description = get_input("Enter task description (press Enter to skip): ")

    try:
        task = add_task(title, description)
        print(f"\n\033[92m✓ Task added successfully (ID: {task.task_id})\033[0m")
    except ValueError as e:
        print(f"\n\033[91mError: {e}\033[0m")


def handle_view_tasks() -> None:
    """Handle the View Tasks menu option."""
    magenta = "\033[95m"
    reset = "\033[0m"
    print(f"\n{magenta}--- 📋 ALL TASKS ---{reset}\n")

    tasks = view_tasks()

    if not tasks:
        print("\033[93mNo tasks found. Add your first task to get started!\033[0m")
        return

    for task in tasks:
        status_icon = "\033[92m✓\033[0m" if task.status == "complete" else "\033[93m○\033[0m"
        status_color = "\033[92m" if task.status == "complete" else "\033[93m"
        print(f"  {status_icon} [\033[96m{task.task_id}\033[0m] {status_color}[{task.status}]{reset} {task.title}")
        if task.description:
            print(f"       \033[90mDescription: {task.description}\033[0m")

    print(f"\nTotal: \033[96m{len(tasks)}\033[0m task(s)")


def handle_update_task() -> None:
    """Handle the Update Task menu option."""
    magenta = "\033[95m"
    reset = "\033[0m"
    print(f"\n{magenta}--- ✏️  UPDATE TASK ---{reset}\n")

    # First show current tasks
    tasks = view_tasks()
    if not tasks:
        print("\033[93mNo tasks to update. Add a task first!\033[0m")
        return

    print("Current tasks:")
    for task in tasks:
        print(f"  [\033[96m{task.task_id}\033[0m] {task.title}")
    print()

    task_id_str = get_input("Enter task ID to update: ")
    if not task_id_str:
        print("\n\033[90mCancelled.\033[0m")
        return

    try:
        task_id = int(task_id_str)
    except ValueError:
        print(f"\n\033[91mError: Invalid task ID '{task_id_str}'. Must be a number.\033[0m")
        return

    print("\n\033[90mLeave blank to keep current value:\033[0m")
    new_title = get_input("New title: ")
    new_description = get_input("New description: ")

    # Determine what to update
    title_arg = new_title if new_title else None
    desc_arg = new_description if new_description else None

    if title_arg is None and desc_arg is None:
        print("\n\033[90mNo changes made.\033[0m")
        return

    try:
        update_task(task_id, title=title_arg, description=desc_arg)
        print(f"\n\033[92m✓ Task {task_id} updated successfully\033[0m")
    except (IndexError, ValueError) as e:
        print(f"\n\033[91mError: {e}\033[0m")


def handle_delete_task() -> None:
    """Handle the Delete Task menu option."""
    magenta = "\033[95m"
    reset = "\033[0m"
    print(f"\n{magenta}--- 🗑️  DELETE TASK ---{reset}\n")

    # First show current tasks
    tasks = view_tasks()
    if not tasks:
        print("\033[93mNo tasks to delete.\033[0m")
        return

    print("Current tasks:")
    for task in tasks:
        print(f"  [\033[96m{task.task_id}\033[0m] {task.title}")
    print()

    task_id_str = get_input("Enter task ID to delete: ")
    if not task_id_str:
        print("\n\033[90mCancelled.\033[0m")
        return

    try:
        task_id = int(task_id_str)
    except ValueError:
        print(f"\n\033[91mError: Invalid task ID '{task_id_str}'. Must be a number.\033[0m")
        return

    # Confirm deletion
    confirm = get_input(f"Are you sure you want to delete task {task_id}? (y/n): ")
    if confirm.lower() != 'y':
        print("\n\033[90mCancelled.\033[0m")
        return

    try:
        delete_task(task_id)
        print(f"\n\033[92m✓ Task {task_id} deleted successfully\033[0m")
    except IndexError as e:
        print(f"\n\033[91mError: {e}\033[0m")


def handle_toggle_status() -> None:
    """Handle the Mark Complete/Incomplete menu option."""
    magenta = "\033[95m"
    reset = "\033[0m"
    print(f"\n{magenta}--- ✅ MARK COMPLETE/INCOMPLETE ---{reset}\n")

    # First show current tasks
    tasks = view_tasks()
    if not tasks:
        print("\033[93mNo tasks to mark.\033[0m")
        return

    print("Current tasks:")
    for task in tasks:
        status_icon = "\033[92m✓\033[0m" if task.status == "complete" else "\033[93m○\033[0m"
        status_color = "\033[92m" if task.status == "complete" else "\033[93m"
        print(f"  {status_icon} [\033[96m{task.task_id}\033[0m] {status_color}[{task.status}]{reset} {task.title}")
    print()

    task_id_str = get_input("Enter task ID to toggle: ")
    if not task_id_str:
        print("\n\033[90mCancelled.\033[0m")
        return

    try:
        task_id = int(task_id_str)
    except ValueError:
        print(f"\n\033[91mError: Invalid task ID '{task_id_str}'. Must be a number.\033[0m")
        return

    try:
        task = toggle_status(task_id)
        status_color = "\033[92m" if task.status == "complete" else "\033[93m"
        print(f"\n\033[92m✓ Task {task_id} marked as {status_color}{task.status}\033[0m")
    except IndexError as e:
        print(f"\n\033[91mError: {e}\033[0m")


def run_interactive() -> None:
    """Run the interactive CLI loop."""
    clear_screen()
    print_header()
    print("\033[93mWelcome! This is an in-memory todo app.\033[0m")
    print("\033[90mAll tasks will be lost when you exit.\033[0m\n")

    while True:
        print(f"\033[96m{'-' * 60}\033[0m")
        print_menu()

        choice = get_input("Enter your choice (1-6): ")

        if choice == "1":
            handle_add_task()
            press_enter_to_continue()
            clear_screen()
            print_header()
        elif choice == "2":
            handle_view_tasks()
            press_enter_to_continue()
            clear_screen()
            print_header()
        elif choice == "3":
            handle_update_task()
            press_enter_to_continue()
            clear_screen()
            print_header()
        elif choice == "4":
            handle_delete_task()
            press_enter_to_continue()
            clear_screen()
            print_header()
        elif choice == "5":
            handle_toggle_status()
            press_enter_to_continue()
            clear_screen()
            print_header()
        elif choice == "6":
            print(f"\n\033[92mGoodbye! All tasks have been cleared.\033[0m")
            break
        else:
            print(f"\n\033[91mInvalid choice '{choice}'. Please enter 1-6.\033[0m")
            press_enter_to_continue()
            clear_screen()
            print_header()


if __name__ == "__main__":
    run_interactive()
