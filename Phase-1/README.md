# Todo In-Memory CLI

A simple in-memory todo application with an interactive menu-driven interface.

## Overview

This is a **Phase 1** implementation of a todo application. All task data exists only in memory during the Python process execution - restarting the application clears all tasks.

## Features

- **Add** tasks with title and optional description
- **View** all tasks with their status
- **Update** task title or description
- **Delete** tasks from the list
- **Mark Complete/Incomplete** toggle task status

## Requirements

- Python 3.13+
- uv package manager

## Installation

```bash
# Clone or navigate to the project
cd Phase-1/

# Install the package
uv pip install -e .
```

## Usage

### Interactive Mode (Recommended)

```bash
uv run todo
```

This launches an interactive menu:

```
==================================================
        TODO IN-MEMORY CLI APPLICATION
==================================================

Welcome! This is an in-memory todo app.
All tasks will be lost when you exit.

--------------------------------------------------
What would you like to do?

  [1] Add Task
  [2] View Tasks
  [3] Update Task
  [4] Delete Task
  [5] Mark Complete/Incomplete
  [6] Exit

Enter your choice (1-6):
```

### Command Mode (Alternative)

```bash
# Add a task
uv run todo add "Buy groceries" --description "Milk, eggs, bread"

# View all tasks
uv run todo view

# Update a task
uv run todo update 1 --title "Buy groceries and fruits"

# Mark task as complete
uv run todo complete 1

# Delete a task
uv run todo delete 2

# Show help
uv run todo help
```

## Running Tests

```bash
uv run pytest -v
```

## Project Structure

```
Phase-1/
├── src/
│   ├── main.py              # Application entry point
│   ├── models/              # Data models and business logic
│   │   └── task.py          # Task model and operations
│   └── cli/                 # CLI command handlers
│       ├── handlers.py      # Command handlers
│       └── interactive.py   # Interactive menu interface
├── tests/                   # Unit tests (53 tests)
├── specs/                   # Feature specifications
└── README.md                # This file
```

## License

MIT
