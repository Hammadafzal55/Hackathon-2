---
description: Implement modular, testable Python console-based features for in-memory todo app operations. Follows specifications and CLI UX designs to create clean, readable code with clear separation of concerns.
handoffs:
  - label: Create Pull Request
    agent: sp.git.commit_pr
    prompt: Commit the implemented code and create a PR
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**Goal**: Implement high-quality, modular Python code for the Phase 1 in-memory console todo app based on specifications and CLI UX designs.

**Phase**: Implementation stage - AFTER `sp.plan` and CLI design are complete
**Scope**: Python console application code, in-memory data structures, CLI command implementations

**When to use this skill**:
- Feature requires Python code for console application
- Specification (`spec.md`) is complete
- CLI UX design (if applicable) is complete
- Tasks (`tasks.md`) are defined from `sp.tasks`
- Implementing todo app features (add, list, complete, delete, etc.)

**When NOT to use this skill**:
- During specification or CLI design phases (design first, then implement)
- For web applications, GUIs, or APIs (this is console-only)
- When prerequisites are incomplete (spec, plan, CLI design)
- For non-Python implementations

## Execution Flow

### 1. Prerequisites Check

Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly` to verify:
- `FEATURE_DIR`
- `FEATURE_SPEC`
- `IMPL_PLAN` (from `sp.plan`)
- `TASKS` (from `sp.tasks`)

If any prerequisites missing, error with clear guidance:
- "Run `/sp.specify` to create the specification"
- "Run `/sp.plan` to create the implementation plan"
- "Run `/sp.tasks` to create testable tasks"
- "Run `/sp.cli-design` if CLI commands are involved"

### 2. Load and Analyze Requirements

Read all relevant artifacts:

**A) Specification** (`FEATURE_SPEC`):
- Functional requirements
- Data model (entities, attributes)
- User stories and workflows
- Success criteria

**B) Implementation Plan** (`IMPL_PLAN`):
- Architecture decisions
- Module structure
- Design patterns
- Dependencies and constraints

**C) Tasks** (`TASKS`):
- Testable implementation tasks
- Acceptance criteria for each task
- Dependency ordering

**D) CLI UX Design** (if `cli-ux-design.md` exists):
- Command specifications
- Input validation rules
- Output formats
- Help text

### 3. Review Existing Code Structure

Check the current codebase:
- Existing Python modules
- Code style and patterns
- Testing framework and conventions
- Entry point (main script)

### 4. Plan Implementation Approach

Based on the tasks and plan, determine:
- **Module organization** - how to structure the code
- **Data structures** - in-memory representation
- **Functions/classes** - what to implement
- **Order of implementation** - dependency-aware sequence

### 5. Implement - Task by Task

For each task in `TASKS.md` (in dependency order):

**A) Create or Update Module**:

```python
"""
[Module description]
"""

# Imports
from typing import List, Optional, Dict, Any
import sys

# Constants (if applicable)

# Classes (if applicable)
class Task:
    """Represent a task in the in-memory todo list."""
    def __init__(self, task_id: int, description: str, status: str = "todo"):
        """
        Initialize a Task.

        Args:
            task_id: Unique identifier for the task
            description: Task description
            status: Task status (default: "todo")
        """
        self.task_id = task_id
        self.description = description
        self.status = status

    def complete(self) -> None:
        """Mark the task as complete."""
        self.status = "done"

    def __repr__(self) -> str:
        return f"Task(id={self.task_id}, description='{self.description}', status='{self.status}')"
```

**B) Implement Core Functions**:

```python
def add_task(tasks: List[Task], description: str, **kwargs) -> Task:
    """
    Add a new task to the in-memory list.

    Args:
        tasks: List of existing tasks
        description: Task description
        **kwargs: Additional task attributes (priority, etc.)

    Returns:
        The newly created Task object

    Raises:
        ValueError: If description is empty or invalid
    """
    # Input validation
    if not description or not description.strip():
        raise ValueError("Task description cannot be empty")

    # Generate task ID (1-indexed)
    task_id = len(tasks) + 1

    # Create task
    task = Task(task_id=task_id, description=description, **kwargs)

    # Add to list
    tasks.append(task)

    return task


def list_tasks(tasks: List[Task], filter_status: Optional[str] = None) -> List[Task]:
    """
    List tasks, optionally filtered by status.

    Args:
        tasks: List of tasks
        filter_status: Optional status filter ("todo", "done", "all")

    Returns:
        Filtered list of tasks
    """
    if filter_status is None or filter_status == "all":
        return tasks

    return [task for task in tasks if task.status == filter_status]


def complete_task(tasks: List[Task], task_id: int) -> Optional[Task]:
    """
    Mark a task as complete.

    Args:
        tasks: List of tasks
        task_id: ID of task to complete

    Returns:
        The completed task, or None if not found
    """
    for task in tasks:
        if task.task_id == task_id:
            task.complete()
            return task
    return None


def delete_task(tasks: List[Task], task_id: int) -> Optional[Task]:
    """
    Delete a task from the list.

    Args:
        tasks: List of tasks
        task_id: ID of task to delete

    Returns:
        The deleted task, or None if not found
    """
    for i, task in enumerate(tasks):
        if task.task_id == task_id:
            return tasks.pop(i)
    return None
```

**C) Implement CLI Command Handlers**:

```python
def cmd_add(args: List[str]) -> None:
    """
    Handle the 'add' command.

    Usage: todo add <task-description> [--priority <level>]

    Args:
        args: Command arguments
    """
    if not args:
        print("Error: Task description is required.")
        print("Usage: todo add <task-description> [--priority <level>]")
        return

    # Parse description (everything before flags)
    description_parts = []
    i = 0
    while i < len(args) and not args[i].startswith("--"):
        description_parts.append(args[i])
        i += 1

    description = " ".join(description_parts)

    # Parse optional flags
    kwargs = {}
    while i < len(args):
        if args[i] == "--priority" and i + 1 < len(args):
            kwargs["priority"] = args[i + 1]
            i += 2

    # Add task
    try:
        task = add_task(GLOBAL_TASKS, description, **kwargs)
        print(f"Task added successfully (ID: {task.task_id})")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_list(args: List[str]) -> None:
    """
    Handle the 'list' command.

    Usage: todo list [--filter <status>]

    Args:
        args: Command arguments
    """
    filter_status = "all"

    if "--filter" in args:
        idx = args.index("--filter")
        if idx + 1 < len(args):
            filter_status = args[idx + 1]
            if filter_status not in ["todo", "done", "all"]:
                print("Error: Invalid filter. Use: todo, done, or all")
                return

    tasks = list_tasks(GLOBAL_TASKS, filter_status=filter_status)

    if not tasks:
        print("No tasks found.")
    else:
        print("\nTasks:")
        for task in tasks:
            status_symbol = "✓" if task.status == "done" else " "
            print(f"  [{task.task_id}] [{status_symbol}] {task.description}")
```

**D) Implement Main Entry Point**:

```python
# Global state (in-memory)
GLOBAL_TASKS: List[Task] = []


def main():
    """Main entry point for the todo CLI application."""
    if len(sys.argv) < 2:
        print("Usage: todo <command> [options]")
        print("Commands: add, list, complete, delete, help")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    # Command routing
    if command == "add":
        cmd_add(args)
    elif command == "list":
        cmd_list(args)
    elif command == "complete":
        cmd_complete(args)
    elif command == "delete":
        cmd_delete(args)
    elif command in ["help", "--help", "-h"]:
        cmd_help(args)
    else:
        print(f"Error: Unknown command '{command}'")
        print("Run 'todo help' for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**E) Write Unit Tests**:

```python
import unittest
from todo import Task, add_task, list_tasks, complete_task, delete_task


class TestTaskModel(unittest.TestCase):
    """Test cases for the Task model."""

    def test_task_creation(self):
        """Test creating a task."""
        task = Task(task_id=1, description="Test task")
        self.assertEqual(task.task_id, 1)
        self.assertEqual(task.description, "Test task")
        self.assertEqual(task.status, "todo")

    def test_task_completion(self):
        """Test marking a task as complete."""
        task = Task(task_id=1, description="Test task")
        task.complete()
        self.assertEqual(task.status, "done")


class TestTaskOperations(unittest.TestCase):
    """Test cases for task operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.tasks: List[Task] = []

    def test_add_task(self):
        """Test adding a task."""
        task = add_task(self.tasks, "Buy groceries")
        self.assertEqual(len(self.tasks), 1)
        self.assertEqual(task.task_id, 1)
        self.assertEqual(task.description, "Buy groceries")

    def test_add_task_empty_description(self):
        """Test adding a task with empty description raises error."""
        with self.assertRaises(ValueError):
            add_task(self.tasks, "")

    def test_list_tasks_all(self):
        """Test listing all tasks."""
        add_task(self.tasks, "Task 1")
        add_task(self.tasks, "Task 2")
        add_task(self.tasks, "Task 3")
        self.assertEqual(len(list_tasks(self.tasks)), 3)

    def test_list_tasks_filter(self):
        """Test filtering tasks by status."""
        task1 = add_task(self.tasks, "Task 1")
        task2 = add_task(self.tasks, "Task 2")
        task2.complete()

        todo_tasks = list_tasks(self.tasks, filter_status="todo")
        done_tasks = list_tasks(self.tasks, filter_status="done")

        self.assertEqual(len(todo_tasks), 1)
        self.assertEqual(len(done_tasks), 1)
        self.assertEqual(todo_tasks[0].task_id, 1)
        self.assertEqual(done_tasks[0].task_id, 2)

    def test_complete_task(self):
        """Test completing a task."""
        task = add_task(self.tasks, "Test task")
        result = complete_task(self.tasks, task.task_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.status, "done")

    def test_complete_task_not_found(self):
        """Test completing a non-existent task."""
        result = complete_task(self.tasks, 999)
        self.assertIsNone(result)

    def test_delete_task(self):
        """Test deleting a task."""
        task = add_task(self.tasks, "Test task")
        result = delete_task(self.tasks, task.task_id)
        self.assertIsNotNone(result)
        self.assertEqual(len(self.tasks), 0)

    def test_delete_task_not_found(self):
        """Test deleting a non-existent task."""
        add_task(self.tasks, "Task 1")
        result = delete_task(self.tasks, 999)
        self.assertIsNone(result)
        self.assertEqual(len(self.tasks), 1)


if __name__ == "__main__":
    unittest.main()
```

### 6. Code Quality Standards

**Follow these principles**:

- **Modularity**: Each function does one thing well
- **Type hints**: Use Python type hints for all function signatures
- **Docstrings**: Comprehensive docstrings for all public functions
- **Error handling**: Clear error messages with specific reasons
- **Separation of concerns**: Model logic separate from CLI logic
- **Testability**: Code should be easily testable
- **Readability**: Clear variable names, consistent formatting

**Code references**:
- Cite modified files with file:line format in docstrings/comments
- Reference spec requirements: "Implements spec.md:Functional Requirements#1"
- Reference CLI design: "Follows cli-ux-design.md:Commands#add"

### 7. Testing

After implementing each task:

1. **Write unit tests**:
   - Test all public functions
   - Include edge cases and error paths
   - Use descriptive test names

2. **Run tests**:
   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```

3. **Fix any failures**:
   - Debug and fix test failures
   - Ensure all acceptance criteria pass

4. **Manual CLI testing** (optional but recommended):
   ```bash
   python main.py add "Buy groceries"
   python main.py list
   python main.py complete 1
   python main.py list --filter done
   ```

### 8. Validation

Validate the implementation:

- [ ] All tasks from `tasks.md` are completed
- [ ] All unit tests pass
- [ ] Code follows project style guidelines
- [ ] Docstrings are complete
- [ ] Error handling is comprehensive
- [ ] CLI commands work as designed
- [ ] Type hints are present
- [ ] No implementation details leaked into spec (spec unchanged)

### 9. Completion Report

Report:
- Number of tasks completed
- Files created/modified
- Test results (pass/fail counts)
- Modules implemented
- Next recommended command (likely `/sp.git.commit_pr` to commit and create PR)

## Behavior Rules

- **Implement ONE task at a time** - complete and test before moving to next
- **Write tests BEFORE or WITH code** - test-driven approach preferred
- **Follow the plan** - implement according to `plan.md` architecture
- **Respect CLI design** - follow `cli-ux-design.md` exactly
- **Keep code modular** - functions should be small and focused
- **Document thoroughly** - docstrings, type hints, inline comments
- **Test everything** - unit tests for all functions, especially edge cases
- **Console-only** - in-memory data structures, no persistence or external APIs

## Reusable Intelligence

This skill produces **reusable patterns** for Python console applications:

**Data model patterns**:
- In-memory lists/dictionaries for data storage
- Clear entity models with attributes and methods
- State management through simple operations

**CLI patterns**:
- Command routing in main()
- Argument parsing
- Output formatting
- Error message patterns

**Testing patterns**:
- Unit test structure with setUp/tearDown
- Test naming conventions
- Edge case coverage

**Code organization**:
- Separation of model, CLI, and tests
- Type hints throughout
- Comprehensive docstrings

These patterns can be reused for similar in-memory console applications:
- Task managers
- Contact lists
- Inventory trackers
- Any CLI-based data management tool

---

**PHR Creation**: After completing the main request, create a PHR using agent-native tools following the implementation stage routing to `history/prompts/<feature-name>/`.
