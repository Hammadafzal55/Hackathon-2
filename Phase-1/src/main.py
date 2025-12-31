#!/usr/bin/env python3
"""
Todo In-Memory CLI - Main entry point.

A simple in-memory todo application for managing tasks via command line.
All data exists only for the duration of the Python process execution.

Usage:
    python src/main.py              Run interactive mode (default)
    python src/main.py --cli        Run in command-line mode
    python src/main.py <command>    Run a specific command

Commands (CLI mode):
    add <title> [--description <text>]  Add a new task
    view                                 View all tasks
    update <task_id> [--title] [--desc]  Update a task
    delete <task_id>                     Delete a task
    complete <task_id>                   Toggle task status
    help                                 Show this help message
"""

import sys
from pathlib import Path
from typing import List, Optional

# Add project root to sys.path for direct script execution
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.cli.handlers import cmd_add, cmd_view, cmd_update, cmd_delete, cmd_complete
from src.cli.interactive import run_interactive


# Command handlers dictionary
_commands = {
    "add": cmd_add,
    "view": cmd_view,
    "update": cmd_update,
    "delete": cmd_delete,
    "complete": cmd_complete,
}


def show_help() -> None:
    """Display usage information for all commands."""
    help_text = """
Todo In-Memory CLI - Manage your tasks in memory

Usage: python src/main.py <command> [options]

Commands:
  add <title> [--description <text>]    Add a new task
  view                                  View all tasks
  update <task_id> [--title] [--desc]   Update a task
  delete <task_id>                      Delete a task
  complete <task_id>                    Toggle task status
  help                                  Show this help message

Options:
  --description <text>    Task description (for add/update)
  --title <text>          Task title (for update)

Examples:
  python src/main.py add "Buy groceries"
  python src/main.py add "Walk dog" --description "Morning and evening"
  python src/main.py view
  python src/main.py update 1 --title "Buy groceries and fruits"
  python src/main.py complete 1
  python src/main.py delete 2
"""
    print(help_text.strip())


def main() -> None:
    """Main entry point for the Todo CLI application."""
    # Default to interactive mode if no arguments provided
    if len(sys.argv) < 2:
        run_interactive()
        return

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    # Handle help command
    if command in ("help", "--help", "-h"):
        show_help()
        return

    # Check if command exists
    if command not in _commands:
        print(f"Error: Unknown command '{command}'", file=sys.stderr)
        print("Run 'python src/main.py help' for usage.")
        sys.exit(1)

    # Execute the command handler
    try:
        _commands[command](args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
