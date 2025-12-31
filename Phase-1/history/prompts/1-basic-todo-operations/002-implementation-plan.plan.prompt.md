---
id: 001
title: Implementation plan for todo app
stage: plan
date: 2025-12-29
surface: agent
model: claude-sonnet-4.5-20250929
feature: 1-basic-todo-operations
branch: main
user: User
command: /sp.plan
labels: ["plan", "implementation", "architecture"]
links:
  spec: ../spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/1-basic-todo-operations/plan.md
tests:
  - None
---

## Prompt

PLAN: Phase 1 – In-Memory Python Console Todo App

## CONTEXT
This plan is based on SPEC 1: TASK SPECIFICATIONS for Phase 1 Todo In-Memory Python Console App.
It defines sequence of steps, tasks, and agent responsibilities required to implement CLI todo app from scratch.

## OBJECTIVE
Break down specifications into an actionable plan that can be executed using Agentic Dev Stack workflow:
1. Write spec → spec-author
2. Design CLI workflow → cli-ux-designer
3. Implement in-memory Python code → python-impl

Ensure all steps are phase-compliant, deterministic, and testable.

## PLAN STEPS

1. **Setup Project Structure**
   - Create `/app` folder
   - Create `main.py` for CLI loop and command parsing
   - Create `tasks.py` for in-memory task storage and functions

2. **Define Task Data Structure**
   - Use Python `list` or `dict` to store tasks in memory
   - Each task includes: `title`, `description`, `status`

3. **Implement Add Task Function**
   - Function: `add_task(title, description)`
   - Validate non-empty title
   - Add task to in-memory list with default status `incomplete`

4. **Implement View Tasks Function**
   - Function: `view_tasks()`
   - Display tasks with index, title, description, status
   - Show friendly message when list is empty

5. **Implement Update Task Function**
   - Function: `update_task(task_id, title, description)`
   - Validate task exists and title not empty
   - Update specified fields in memory

6. **Implement Delete Task Function**
   - Function: `delete_task(task_id)`
   - Validate task exists
   - Remove task and reassign IDs

7. **Implement Mark Complete/Incomplete Function**
   - Function: `toggle_status(task_id)`
   - Validate task exists
   - Toggle status between `incomplete` and `complete`

8. **Integrate CLI Commands**
   - Map commands to functions: `add`, `view`, `update`, `delete`, `complete`
   - Include input prompts and validation
   - Handle invalid inputs gracefully

9. **Testing & Validation**
   - Test all operations for deterministic outputs
   - Ensure CLI flow matches designed workflow
   - Validate edge cases: empty title, invalid IDs, duplicate tasks

## AGENT & SKILL RULES
- spec-enforcer: Ensure plan strictly follows Phase 1 boundaries
- spec-author: Base plan on task specifications
- cli-ux-designer: Ensure CLI command flow and prompts are intuitive
- python-impl: Implement Python functions exactly per plan

## CONSTRAINTS
- Tasks stored in memory only
- Phase 1 only: restrict to Add, View, Update, Delete, Mark Complete
- No external storage, databases, or files
- Clean, modular Python code

## DEFINITION OF DONE
- CLI todo app fully functional for all 5 basic operations
- Input validation and edge cases handled

## Response snapshot

Created complete implementation plan for Phase 1 Todo In-Memory Python Console App with:

**Technical Context Defined**:
- Language: Python 3.8+ (standard library only)
- Storage: In-memory data structures (lists, dictionaries)
- Testing: unittest (Python standard library)
- Project Type: Single project structure
- Performance: 1000+ tasks in memory, <100ms command execution, <50MB memory
- Constraints: No file I/O, no databases, no external APIs, no third-party packages

**Constitution Check**: ✅ PASSED
- All 6 core principles validated
- No violations found
- All plans aligned with Phase 1 requirements

**Project Structure**:
- Single project with clear separation (src/models/, src/cli/)
- Tests mirror src structure
- README.md for documentation

**Data Model**:
- Task dataclass with task_id, title, description, status
- Validation rules for title (non-empty) and task_id (valid range)
- State transitions: incomplete ↔ complete
- In-memory storage using Python list with ID reassignment

**CLI Contracts**:
- 6 commands: add, view, update, delete, complete, help
- Clear syntax with positional and optional arguments
- Input validation contracts
- Error handling contracts with specific messages

**Implementation Phases (8)**:
1. Setup (project structure)
2. Foundational (data model, helpers)
3. User Story 1: Add Task (P1)
4. User Story 2: View Tasks (P1)
5. User Story 3: Update Task (P2)
6. User Story 4: Delete Task (P2)
7. User Story 5: Mark Complete/Incomplete (P2)
8. Polish (documentation, code review)

**Tasks (42 total)**:
- Phase 1-2: 7 foundational tasks
- Phase 3-7: 6 tasks per user story (5 stories)
- Phase 8: 7 polish tasks
- All tasks include [P] parallelization markers and [US] user story labels

**Quickstart Guide**:
- Setup instructions with no dependencies
- Usage examples for all commands
- Expected output formats for all operations

**Implementation Strategies**:
- MVP First (User Stories 1+2 only)
- Incremental Delivery (one story at a time)
- Parallel Team Strategy (multiple developers)

## Outcome

- ✅ Impact: Complete implementation plan ready for Python console todo app with clear tasks, architecture, and data model
- 🧪 Tests: None (planning phase)
- 📁 Files: specs/1-basic-todo-operations/plan.md
- 🔁 Next prompts: `/sp.tasks` to create testable task breakdown or `/sp.cli-design` to define CLI UX flows
- 🧠 Reflection: Plan comprehensively addresses all 5 user stories with 42 implementation tasks. Constitution check passed. Data model and CLI contracts defined. Ready for implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution Check - PASSED
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A - plan complete and validated
