# Quickstart Guide: Phase 1 Todo App

**Feature**: 1-Basic-Todo-Operations
**Date**: 2025-12-29
**Purpose**: Get the in-memory Python console todo app running quickly

## Prerequisites

- Python 3.13 or higher installed
- uv package manager installed
- Terminal or command-line access

## Installation

### 1. Clone or Navigate to Repository

```bash
# If cloning from version control
git clone <repository-url>
cd Phase-1/

# Or if already in project directory
cd Phase-1/
```

### 2. Create Project Structure

```bash
# Create source directories
mkdir -p src/models src/cli tests
```

### 3. Verify Python Version

```bash
python --version
# Should output: Python 3.8.0 or higher
```

## Running the Application

### Install the Package

```bash
# Install in editable mode (first time only)
uv pip install -e .
```

### Interactive Mode (Recommended)

```bash
# Launch the interactive menu
uv run todo
```

This displays a menu-driven interface:

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
uv run todo <command> [options]
```

## Commands Reference

| Command | Syntax | Description |
|----------|--------|-------------|
| `add` | `uv run todo add <title> [--description <text>]` | Create a new task |
| `view` | `uv run todo view` | Display all tasks |
| `update` | `uv run todo update <task_id> [--title <text>] [--description <text>]` | Modify task |
| `delete` | `uv run todo delete <task_id>` | Remove a task |
| `complete` | `uv run todo complete <task_id>` | Toggle task status |
| `help` | `uv run todo help` | Show usage information |

## Usage Examples

### Adding Tasks

```bash
# Add a task with title only
uv run todo add "Buy groceries"

# Add a task with title and description
uv run todo add "Buy groceries" --description "Milk, eggs, bread"

# Add a task with empty description
uv run todo add "Walk dog" --description ""
```

**Expected Output**:
```
Task added successfully (ID: 1)
```

### Viewing Tasks

```bash
# View all tasks
uv run todo view
```

**Expected Output (with tasks)**:
```
Tasks:
[1] [incomplete] Buy groceries
  Description: Milk, eggs, bread
[2] [complete] Walk dog
  Description:

[3] [incomplete] Pay bills
  Description: Rent, utilities, internet
```

**Expected Output (empty list)**:
```
No tasks found. Add your first task to get started!
```

### Updating Tasks

```bash
# Update task title
uv run todo update 1 --title "Buy groceries and fruits"

# Update task description
uv run todo update 1 --description "Milk, eggs, bread, apples, bananas"

# Update both title and description
uv run todo update 1 --title "Weekly shopping" --description "All groceries for the week"
```

**Expected Output**:
```
Task 1 updated successfully
```

### Deleting Tasks

```bash
# Delete a task by ID
uv run todo delete 2
```

**Expected Output**:
```
Task 2 deleted successfully
```

**Note**: After deletion, task IDs are renumbered to maintain 1-to-N sequential indexing.

### Marking Tasks Complete/Incomplete

```bash
# Mark a task as complete
uv run todo complete 1

# Mark a task as incomplete again (toggle)
uv run todo complete 1
```

**Expected Output**:
```
Task 1 marked as complete
# or
Task 1 marked as incomplete
```

### Getting Help

```bash
# Show help information
uv run todo help
```

**Expected Output**:
```
Todo In-Memory CLI - Manage your tasks in memory

Usage: uv run todo <command> [options]

Commands:
  add <title> [--description <text>]    Add a new task
  view                                  View all tasks
  update <task_id> [--title] [--desc]    Update a task
  delete <task_id>                       Delete a task
  complete <task_id>                     Toggle task status
  help                                   Show this help message

Options:
  --description <text>    Task description (for add/update)
  --title <text>          Task title (for update)

Examples:
  uv run todo add "Buy groceries"
  uv run todo view
  uv run todo complete 1
```

## Common Workflows

### Daily Task Management

```bash
# 1. Add new tasks
uv run todo add "Review pull requests"
uv run todo add "Write documentation" --description "Update README with new features"
uv run todo add "Debug failing tests"

# 2. View your task list
uv run todo view

# 3. Mark tasks as you complete them
uv run todo complete 1

# 4. Delete completed tasks
uv run todo delete 1
```

### Task Correction Workflow

```bash
# 1. Add a task (typo intended)
uv run todo add "By grocerries"

# 2. View tasks and notice the typo
uv run todo view

# 3. Update the task with correct spelling
uv run todo update 1 --title "Buy groceries"
```

## Error Handling

### Common Errors and Solutions

| Error | Cause | Solution |
|--------|--------|----------|
| `Error: Task title cannot be empty` | Empty or whitespace-only title | Provide a non-empty title |
| `Error: Task with ID 5 not found` | Task ID doesn't exist | Run `view` to see valid IDs |
| `Error: Unknown command 'xyz'` | Invalid command | Run `help` to see valid commands |
| `unrecognized arguments` | Invalid option syntax | Check command help for correct syntax |

## Testing

### Run Unit Tests

```bash
# Run all tests with pytest
uv run pytest

# Run all tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_task.py

# Run specific test class
uv run pytest tests/test_task.py::TestAddTask

# Run specific test
uv run pytest tests/test_task.py::TestAddTask::test_add_task_with_title_only
```

## Demo Checklist

Before demonstrating the application, ensure:

- [ ] Python version is 3.8+
- [ ] All commands work as documented
- [ ] Error messages are clear and helpful
- [ ] Task IDs reassign correctly after deletion
- [ ] Empty list shows friendly message
- [ ] Status toggle works both ways

## Troubleshooting

### Application Won't Start

1. Check Python version: `python --version`
2. Verify you're in project root directory
3. Ensure `src/main.py` exists

### Commands Not Recognized

1. Verify command spelling
2. Run `uv run todo help` to see valid commands
3. Check for extra spaces in command

### Data Not Persisting

This is expected behavior! Phase 1 uses in-memory storage only:
- Tasks exist only for the duration of the Python process
- Restarting the application clears all tasks
- No file I/O, databases, or persistence mechanisms

## Notes

- All data is stored in memory and lost on application restart
- Task IDs are 1-indexed (start from 1, not 0)
- Duplicate task titles are allowed (tasks identified by ID)
- All commands use positional arguments where appropriate
- No external dependencies required - Python standard library only

## Next Steps

After completing this quickstart:

1. Review [data-model.md](./data-model.md) for detailed data structures
2. Review [plan.md](./plan.md) for implementation phases
3. Run tests: `uv run pytest -v`
4. Demonstrate all 5 core operations
5. Ready for Phase 2: CLI UX design and implementation
