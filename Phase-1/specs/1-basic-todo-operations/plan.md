# Implementation Plan: Basic Todo Operations

**Branch**: `main` | **Date**: 2025-12-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/1-basic-todo-operations/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/plan-template.md` for the base template.

## Summary

Implement an in-memory Python console todo application with 5 core operations: Add Task, View Tasks, Update Task, Delete Task, and Mark Complete/Incomplete. The application stores tasks only in memory (no persistence) and uses only Python standard library with no external dependencies. All user interaction occurs via command-line interface.

## Technical Context

**Language/Version**: Python 3.8+ (standard library only)
**Primary Dependencies**: None (Python standard library only)
**Storage**: In-memory data structures (lists, dictionaries)
**Testing**: unittest (Python standard library)
**Target Platform**: Console/CLI only
**Project Type**: single
**Performance Goals**: Support 1000+ tasks in memory, command execution under 100ms typical, under 50MB memory for 1000 tasks
**Constraints**: No file I/O, no databases, no external APIs, no third-party packages
**Scale/Scope**: In-memory task list for single user session, maximum 5 core operations only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: In-Memory Only (NON-NEGOTIABLE)
- ✅ PASS: All task storage uses Python lists/dictionaries in memory only
- ✅ PASS: No file I/O, databases, or external APIs
- ✅ PASS: Tasks exist only for duration of Python process execution
- Rationale: Using in-memory data structures aligns with Phase 1 scope

### Principle II: Phase 1 Scope Boundary (NON-NEGOTIABLE)
- ✅ PASS: Restricted to 5 core operations (Add, View, Update, Delete, Mark Complete)
- ✅ PASS: No additional features (search, categories, priorities, etc.)
- ✅ PASS: Out-of-scope items explicitly documented
- Rationale: All planned features match specification and constitution

### Principle III: Zero External Dependencies (NON-NEGOTIABLE)
- ✅ PASS: Using only Python standard library (sys, argparse, typing, unittest)
- ✅ PASS: No third-party packages or frameworks
- ✅ PASS: No external APIs or services
- Rationale: Standard library ensures portability and meets constitution requirement

### Principle IV: Console/CLI Interface (NON-NEGOTIABLE)
- ✅ PASS: All user interaction via command line using `python main.py <command> [args]`
- ✅ PASS: Standard input/output for communication
- ✅ PASS: Error messages to stderr
- Rationale: CLI-only interface matches Phase 1 requirements

### Principle V: Modular and Testable (NON-NEGOTIABLE)
- ✅ PASS: Model logic separated from CLI handlers (src/models/, src/cli/)
- ✅ PASS: Functions are small and focused
- ✅ PASS: Type hints for all function signatures
- ✅ PASS: Comprehensive docstrings for all public functions
- ✅ PASS: Unit tests for all model operations (Red-Green-Refactor cycle)
- Rationale: Clean separation enables testing and maintainability

### Principle VI: Demo-Ready Quality (NON-NEGOTIABLE)
- ✅ PASS: Clear naming conventions (lowercase_with_underscores)
- ✅ PASS: Consistent code formatting
- ✅ PASS: Helpful error messages guide users
- ✅ PASS: Documentation (README.md) with setup and usage instructions
- Rationale: Code quality suitable for demonstration

**Constitution Check Result**: ✅ PASSED - No violations found

## Project Structure

### Documentation (this feature)

```text
specs/1-basic-todo-operations/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (not needed - no unknowns)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   └── task.py          # Task data model and operations
├── cli/
│   └── handlers.py       # CLI command handlers
└── main.py                # Application entry point

tests/
├── test_task.py           # Unit tests for task model
├── test_cli_handlers.py   # Unit tests for CLI handlers
└── test_integration.py    # Integration tests (if needed)

README.md                   # Setup and usage instructions
```

**Structure Decision**: Single project structure with clear separation of concerns (models/ for business logic, cli/ for command handling). All code uses Python standard library only. Tests mirror src structure for clear mapping.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | All principles satisfied - no violations |

## Phase 0: Research

*No unknowns in Technical Context - all decisions are clear from specification and constitution.*

### Research Findings

**No research required** - all technology choices are specified by constitution:
- Python 3.8+ (standard library only) - explicitly required
- In-memory storage with lists/dictionaries - explicitly required
- unittest for testing - standard Python library choice
- CLI interface via sys/argparse - explicitly required

### Decisions

| Decision | Rationale | Alternatives Considered |
|-----------|------------|-------------------------|
| Python list for task storage | Simple, efficient for sequential access, meets in-memory requirement | Dictionary (would complicate ID management), custom class (unnecessary complexity for Phase 1) |
| argparse for command parsing | Built-in Python module, no dependencies, standard practice | sys.argv (more manual), Click (external dependency - violates constitution) |
| unittest for testing | Built-in Python module, no dependencies, standard practice | pytest (external dependency - violates constitution) |

## Phase 1: Data Model

### Entity: Task

```python
@dataclass
class Task:
    """Represents a single todo item in the in-memory list."""
    task_id: int          # Unique sequential identifier (1, 2, 3, ...)
    title: str             # Task name (mandatory, non-empty)
    description: str       # Additional details (optional, can be empty string)
    status: str            # Either "incomplete" or "complete"
```

### Validation Rules

| Field | Rule | Error Message |
|--------|-------|---------------|
| title | Non-empty and not whitespace-only | "Error: Task title cannot be empty" |
| task_id | Must be valid index (1 to len(tasks)) | "Error: Task with ID {task_id} not found" |

### State Transitions

```
[Task Created] -> [incomplete] (initial state)
[incomplete] <-> [complete] (toggle operation)
[Task Deleted] -> (removed from memory)
```

### In-Memory Storage Structure

```python
# Global task list (stored in module scope)
_tasks: List[Task] = []

# Helper functions for ID management
def _next_id() -> int:
    """Returns the next available task ID (current length + 1)."""
    return len(_tasks) + 1

def _reassign_ids() -> None:
    """Reassign sequential IDs to all tasks after deletion."""
    for idx, task in enumerate(_tasks, start=1):
        task.task_id = idx
```

**Design Rationale**: Using a Python list maintains insertion order and enables O(1) access by index after deletion. ID reassignment after deletion ensures consistent 1-to-N indexing as required by specification.

## Phase 1: CLI Contracts

### Command Definitions

| Command | Syntax | Function | Description |
|----------|--------|-----------|-------------|
| add | `python main.py add <title> [--description <text>]` | add_task() | Create new task with title and optional description |
| view | `python main.py view` | view_tasks() | Display all tasks with index, title, description, status |
| update | `python main.py update <task_id> [--title <text>] [--description <text>]` | update_task() | Modify task title and/or description |
| delete | `python main.py delete <task_id>` | delete_task() | Remove task from list and reassign IDs |
| complete | `python main.py complete <task_id>` | toggle_status() | Toggle task status between incomplete and complete |
| help | `python main.py help` | show_help() | Display usage information |

### Input Validation

| Command | Required Arguments | Optional Arguments | Validation |
|----------|-------------------|-------------------|-------------|
| add | title (positional) | --description (optional) | title must be non-empty |
| view | None | None | None |
| update | task_id (positional) | --title, --description | task_id must exist, title must be non-empty if provided |
| delete | task_id (positional) | None | task_id must exist |
| complete | task_id (positional) | None | task_id must exist |
| help | None | None | None |

### Error Handling Contract

| Error Type | Condition | Message | Recovery |
|-----------|-----------|----------|-----------|
| ValueError | Empty title | "Error: Task title cannot be empty" | User provides non-empty title |
| IndexError | Invalid task_id | "Error: Task with ID {task_id} not found" | User provides valid task_id |
| General | Invalid command | "Error: Unknown command '{command}'. Run 'python main.py help' for usage." | User runs help command |

## Phase 1: Quickstart Guide

### Setup

```bash
# Navigate to project root
cd Phase-1/

# Create directory structure
mkdir -p src/models src/cli tests

# No dependencies required (Python standard library only)

# Run application
python src/main.py
```

### Usage Examples

```bash
# Add a task
python src/main.py add "Buy groceries" --description "Milk, eggs, bread"

# View all tasks
python src/main.py view

# Update a task
python src/main.py update 1 --title "Buy groceries and fruits"

# Mark task as complete
python src/main.py complete 1

# Delete a task
python src/main.py delete 2

# Show help
python src/main.py help
```

### Expected Output Format

```
# View output with tasks:
Tasks:
[1] [incomplete] Buy groceries
  Description: Milk, eggs, bread
[2] [complete] Walk dog
  Description:

# Empty list output:
No tasks found. Add your first task to get started!

# Error output:
Error: Task with ID 10 not found

# Success output:
Task added successfully (ID: 1)
Task 1 marked as complete
Task 2 deleted successfully
```

## Implementation Phases

### Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] Create directory structure (src/models/, src/cli/, tests/)
- [ ] Create entry point (src/main.py)
- [ ] Create task model file (src/models/task.py)
- [ ] Create CLI handlers file (src/cli/handlers.py)
- [ ] Create README.md with setup and usage instructions

### Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data model that ALL operations depend on

**⚠️ CRITICAL**: No operation work can begin until this phase is complete

- [ ] T001 Implement Task dataclass in src/models/task.py
- [ ] T002 Implement global task list (_tasks) in src/models/task.py
- [ ] T003 Implement _next_id() helper function in src/models/task.py
- [ ] T004 Implement _reassign_ids() helper function in src/models/task.py
- [ ] T005 Implement add_task() function with validation
- [ ] T006 Implement get_task() helper for ID lookup
- [ ] T007 Configure basic CLI argument parsing in src/main.py

**Checkpoint**: Data model ready - operation implementation can now begin

### Phase 3: User Story 1 - Add Task (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks with title and optional description

**Independent Test**: Add a task and verify it appears in view output with correct ID, title, description, status "incomplete"

### Implementation for User Story 1

- [ ] T008 [US1] Implement validate_title() helper in src/models/task.py
- [ ] T009 [US1] Add title validation to add_task() function
- [ ] T010 [US1] Set default status to "incomplete" in add_task()
- [ ] T011 [US1] Implement cmd_add() CLI handler in src/cli/handlers.py
- [ ] T012 [US1] Wire add command in src/main.py
- [ ] T013 [US1] Add error handling for empty title in cmd_add()

**Checkpoint**: Add operation complete and functional

### Phase 4: User Story 2 - View Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can see all tasks with index, title, description, status

**Independent Test**: Add multiple tasks, run view command, verify all tasks displayed correctly

### Implementation for User Story 2

- [ ] T014 [US2] Implement view_tasks() function in src/models/task.py
- [ ] T015 [US2] Handle empty list case in view_tasks()
- [ ] T016 [US2] Format task output with index, status, title, description
- [ ] T017 [US2] Implement cmd_view() CLI handler in src/cli/handlers.py
- [ ] T018 [US2] Wire view command in src/main.py
- [ ] T019 [US2] Add friendly empty list message

**Checkpoint**: View operation complete and functional

### Phase 5: User Story 3 - Update Task (Priority: P2)

**Goal**: Users can modify task title and/or description

**Independent Test**: Add a task, update its title/description, run view to verify changes reflected

### Implementation for User Story 3

- [ ] T020 [US3] Implement update_task() function in src/models/task.py
- [ ] T021 [US3] Add task ID validation in update_task()
- [ ] T022 [US3] Add title validation in update_task() when title updated
- [ ] T023 [US3] Implement cmd_update() CLI handler in src/cli/handlers.py
- [ ] T024 [US3] Parse --title and --description flags in cmd_update()
- [ ] T025 [US3] Wire update command in src/main.py

**Checkpoint**: Update operation complete and functional

### Phase 6: User Story 4 - Delete Task (Priority: P2)

**Goal**: Users can remove tasks from list with automatic ID reassignment

**Independent Test**: Add multiple tasks, delete one, verify task removed and IDs reassigned

### Implementation for User Story 4

- [ ] T026 [US4] Implement delete_task() function in src/models/task.py
- [ ] T027 [US4] Add task ID validation in delete_task()
- [ ] T028 [US4] Call _reassign_ids() after deletion in delete_task()
- [ ] T029 [US4] Implement cmd_delete() CLI handler in src/cli/handlers.py
- [ ] T030 [US4] Wire delete command in src/main.py

**Checkpoint**: Delete operation complete and functional

### Phase 7: User Story 5 - Mark Complete/Incomplete (Priority: P2)

**Goal**: Users can toggle task status between "incomplete" and "complete"

**Independent Test**: Add a task, mark it complete, view to verify status change, mark it incomplete again

### Implementation for User Story 5

- [ ] T031 [US5] Implement toggle_status() function in src/models/task.py
- [ ] T032 [US5] Add task ID validation in toggle_status()
- [ ] T033 [US5] Implement status toggle logic (incomplete <-> complete)
- [ ] T034 [US5] Implement cmd_complete() CLI handler in src/cli/handlers.py
- [ ] T035 [US5] Wire complete command in src/main.py

**Checkpoint**: Toggle status operation complete and functional

### Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T036 Implement show_help() command to display usage information
- [ ] T037 Update README.md with complete setup and usage examples
- [ ] T038 Add comprehensive error messages for all invalid operations
- [ ] T039 Implement consistent output formatting across all commands
- [ ] T040 Review code against all constitution principles
- [ ] T041 Ensure all type hints are present
- [ ] T042 Verify all docstrings are complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed sequentially (P1 → P2) or in parallel if staffed
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Core model functions before CLI handlers
- CLI handlers before command wiring in main.py
- Error handling after core logic

### Parallel Opportunities

- T001, T002, T003, T004 can run in parallel (different parts of Task model)
- T011, T017 (US1 & US2 CLI handlers) can run in parallel after foundational
- T023, T029, T034 (US3, US4, US5 CLI handlers) can run in parallel after P1 stories complete

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Add Task)
4. Complete Phase 4: User Story 2 (View Tasks)
5. **STOP and VALIDATE**: Test Add and View operations independently
6. Demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Demo (MVP core!)
3. Add User Story 2 → Test independently → Demo (MVP complete!)
4. Add User Story 3 → Test independently → Demo
5. Add User Story 4 → Test independently → Demo
6. Add User Story 5 → Test independently → Demo
7. Polish → Final demo

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Add)
   - Developer B: User Story 2 (View)
3. After P1 complete:
   - Developer A: User Story 3 (Update)
   - Developer B: User Story 4 (Delete)
4. Developer A or B: User Story 5 (Complete)
5. Team: Polish together

---

## Notes

- All code uses Python standard library only - no dependencies
- In-memory storage means data is lost on process restart - expected behavior
- Task IDs are 1-indexed for user-friendly display
- After deletion, all task IDs are reassigned to maintain sequential 1-to-N indexing
- Duplicate task titles are allowed (tasks identified by ID, not title)
- Type hints required for all function signatures
- Docstrings required for all public functions
- Unit tests should be written before implementation (Red-Green-Refactor cycle)
