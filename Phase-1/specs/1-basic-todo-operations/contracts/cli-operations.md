# CLI Operations Contract: Basic Todo App

**Feature**: 1-basic-todo-operations
**Date**: 2025-12-29
**Purpose**: Define command-line interface contracts for all operations

## Overview

This document specifies the complete CLI interface contract for the Phase 1 Todo In-Memory Python Console App.

### Running the Application

**Interactive Mode (Default)**:
```bash
uv run todo
```
This launches the interactive menu-driven interface.

**Command Mode (Alternative)**:
```bash
uv run todo <command> [options]
```

## Interactive Menu Interface

When running `uv run todo` without arguments, the application displays:

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

Users select options by entering the corresponding number.

---

## Command Contracts

### 1. Add Task

**Command**: `add`

**Purpose**: Create a new task in the in-memory task list

**Syntax**:
```bash
uv run todo add <title> [--description <text>]
```

**Arguments**:

| Positional | Type | Required | Description | Validation |
|------------|------|----------|-------------|------------|
| title | string | YES | Task name | Non-empty, non-whitespace |

**Options**:

| Flag | Type | Required | Description | Validation |
|------|------|----------|-------------|------------|
| --description | string | NO | Additional task details | None (can be empty string) |

**Input Validation**:
- title must be non-empty after stripping whitespace
- If title is empty: Error `Error: Task title cannot be empty`

**Success Output**:
```
Task added successfully (ID: <task_id>)
```

**Error Output**:
```
Error: Task title cannot be empty
```

**Examples**:
```bash
# Basic add
uv run todo add "Buy groceries"
# Output: Task added successfully (ID: 1)

# Add with description
uv run todo add "Walk dog" --description "Morning and evening"
# Output: Task added successfully (ID: 2)

# Add with empty description
uv run todo add "Pay bills" --description ""
# Output: Task added successfully (ID: 3)

# Invalid: empty title
uv run todo add "   "
# Output: Error: Task title cannot be empty
```

---

### 2. View Tasks

**Command**: `view`

**Purpose**: Display all tasks in the in-memory task list

**Syntax**:
```bash
uv run todo view
```

**Arguments**: None

**Options**: None

**Input Validation**: None

**Success Output (with tasks)**:
```
Tasks:
[1] [incomplete] Buy groceries
  Description: Milk, eggs, bread

[2] [complete] Walk dog
  Description: Morning and evening

[3] [incomplete] Pay bills
  Description: Rent, utilities, internet
```

**Success Output (empty list)**:
```
No tasks found. Add your first task to get started!
```

**Error Output**: None (always succeeds)

**Examples**:
```bash
# View with tasks
uv run todo view
# Output: (list of tasks as shown above)

# View empty list
uv run todo view
# Output: No tasks found. Add your first task to get started!
```

---

### 3. Update Task

**Command**: `update`

**Purpose**: Modify an existing task's title and/or description

**Syntax**:
```bash
uv run todo update <task_id> [--title <text>] [--description <text>]
```

**Arguments**:

| Positional | Type | Required | Description | Validation |
|------------|------|----------|-------------|------------|
| task_id | integer | YES | Task to update | Must exist (1 to N) |

**Options**:

| Flag | Type | Required | Description | Validation |
|------|------|----------|-------------|------------|
| --title | string | NO | New task title | Non-empty if provided |
| --description | string | NO | New task description | None (can be empty string) |

**Constraint**: At least one of `--title` or `--description` must be provided

**Input Validation**:
- task_id must be a valid integer within existing task range
- If task_id invalid: Error `Error: Task with ID {task_id} not found`
- If --title provided and empty: Error `Error: Task title cannot be empty`
- If neither --title nor --description provided: Error `Error: At least one of --title or --description must be specified`

**Success Output**:
```
Task {task_id} updated successfully
```

**Error Output**:
```
Error: Task with ID {task_id} not found
Error: Task title cannot be empty
Error: At least one of --title or --description must be specified
```

**Examples**:
```bash
# Update title only
uv run todo update 1 --title "Buy groceries and fruits"
# Output: Task 1 updated successfully

# Update description only
uv run todo update 1 --description "Milk, eggs, bread, apples, bananas"
# Output: Task 1 updated successfully

# Update both
uv run todo update 1 --title "Weekly shopping" --description "All groceries for the week"
# Output: Task 1 updated successfully

# Invalid: non-existent task
uv run todo update 99 --title "New title"
# Output: Error: Task with ID 99 not found

# Invalid: empty title
uv run todo update 1 --title "   "
# Output: Error: Task title cannot be empty

# Invalid: no options
uv run todo update 1
# Output: Error: At least one of --title or --description must be specified
```

---

### 4. Delete Task

**Command**: `delete`

**Purpose**: Remove a task from the in-memory task list

**Syntax**:
```bash
uv run todo delete <task_id>
```

**Arguments**:

| Positional | Type | Required | Description | Validation |
|------------|------|----------|-------------|------------|
| task_id | integer | YES | Task to delete | Must exist (1 to N) |

**Options**: None

**Input Validation**:
- task_id must be a valid integer within existing task range
- If task_id invalid: Error `Error: Task with ID {task_id} not found`

**Success Output**:
```
Task {task_id} deleted successfully
```

**Error Output**:
```
Error: Task with ID {task_id} not found
```

**Side Effect**: After deletion, all remaining tasks are reindexed to maintain sequential 1-to-N IDs

**Examples**:
```bash
# Delete task 3
uv run todo delete 3
# Output: Task 3 deleted successfully

# Invalid: non-existent task
uv run todo delete 99
# Output: Error: Task with ID 99 not found
```

---

### 5. Toggle Task Status

**Command**: `complete`

**Purpose**: Toggle a task's status between "incomplete" and "complete"

**Syntax**:
```bash
uv run todo complete <task_id>
```

**Arguments**:

| Positional | Type | Required | Description | Validation |
|------------|------|----------|-------------|------------|
| task_id | integer | YES | Task to toggle | Must exist (1 to N) |

**Options**: None

**Input Validation**:
- task_id must be a valid integer within existing task range
- If task_id invalid: Error `Error: Task with ID {task_id} not found`

**Success Output (to complete)**:
```
Task {task_id} marked as complete
```

**Success Output (to incomplete)**:
```
Task {task_id} marked as incomplete
```

**Error Output**:
```
Error: Task with ID {task_id} not found
```

**Examples**:
```bash
# Mark task incomplete as complete
uv run todo complete 1
# Output: Task 1 marked as complete

# Mark task complete as incomplete (toggle back)
uv run todo complete 1
# Output: Task 1 marked as incomplete

# Invalid: non-existent task
uv run todo complete 99
# Output: Error: Task with ID 99 found
```

---

### 6. Help

**Command**: `help`

**Purpose**: Display usage information for all commands

**Syntax**:
```bash
uv run todo help
```

**Arguments**: None

**Options**: None

**Input Validation**: None

**Success Output**:
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

**Error Output**: None (always succeeds)

---

## Global Error Handling

### Unknown Command

**Trigger**: User provides a command not in the valid command set

**Output**:
```
Error: Unknown command '{command}'
Run 'uv run todo help' for usage.
```

### Invalid Arguments

**Trigger**: User provides incorrect number or type of arguments

**Output**:
```
Error: Invalid arguments for '{command}'
Run 'uv run todo help' for usage.
```

### No Command Provided

**Trigger**: User runs without specifying a command

**Output**:
```
Error: No command provided
Run 'uv run todo help' for usage.
```

## Output Format Specifications

### Task Display Format

```
[<task_id>] [<status>] <title>
  Description: <description>
```

- task_id: Integer in square brackets
- status: String in square brackets ("incomplete" or "complete")
- title: Task name
- description: Indented on next line, preceded by "Description: ", empty if no description

### Status Display

| Status Value | Display Text |
|-------------|--------------|
| incomplete | [incomplete] |
| complete | [complete] |

### Empty List Message

```
No tasks found. Add your first task to get started!
```

## Command Summary

| Command | Purpose | Required Args | Optional Args |
|----------|---------|---------------|---------------|
| add | Create task | title | --description |
| view | Display tasks | None | None |
| update | Modify task | task_id | --title, --description |
| delete | Remove task | task_id | None |
| complete | Toggle status | task_id | None |
| help | Show help | None | None |

## Compliance

✅ All CLI contracts comply with constitution:
- I. In-Memory Only: No persistence commands
- II. Phase 1 Scope: Only 5 core operations
- III. Zero External Dependencies: Uses argparse (standard library)
- IV. Console/CLI Interface: All commands via command line
- V. Modular and Testable: Clear input/output contracts
- VI. Demo-Ready Quality: Helpful error messages and examples

## Notes

- All commands use `uv run todo` prefix
- Task IDs are 1-indexed for user-friendly display
- After deletion, IDs are renumbered (side effect documented)
- Error messages are consistent format: "Error: <message>"
- Success messages confirm action taken
- Help command provides comprehensive usage information
