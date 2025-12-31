# Tasks: Basic Todo Operations

**Input**: Design documents from `/specs/1-basic-todo-operations/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

<!--
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.

  The /sp.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/

  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment

  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize Python project with `uv init` in project root
- [x] T002 Create project directory structure (src/models/, src/cli/, tests/)
- [x] T003 [P] Create src/__init__.py to make src a package
- [x] T004 [P] Create src/models/__init__.py to make models a package
- [x] T005 [P] Create src/cli/__init__.py to make cli a package
- [x] T006 [P] Create tests/__init__.py to make tests a package
- [x] T007 Create src/main.py entry point file
- [x] T008 Create README.md with basic project information

- [x] T008a Install pytest for testing with `uv add pytest`

**Note**: pytest added as dependency for testing support

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Implement Task dataclass in src/models/task.py
- [x] T010 Implement global task list (_tasks) in src/models/task.py
- [x] T011 [P] Implement _next_id() helper function in src/models/task.py
- [x] T012 [P] Implement _reassign_ids() helper function in src/models/task.py
- [x] T013 Implement add_task() function with title validation in src/models/task.py
- [x] T014 Implement get_task() helper for ID lookup in src/models/task.py
- [x] T015 Configure basic CLI argument parsing in src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Task (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks with title and optional description

**Independent Test**: Add a task and verify it appears in view output with correct ID, title, description, status "incomplete"

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T016 [P] [US1] Unit test for validate_title() in tests/test_task.py
- [x] T017 [P] [US1] Unit test for add_task() in tests/test_task.py

### Implementation for User Story 1

- [x] T018 [US1] Implement validate_title() helper in src/models/task.py
- [x] T019 [US1] Add title validation to add_task() function
- [x] T020 [US1] Set default status to "incomplete" in add_task()
- [x] T021 [P] [US1] Implement cmd_add() CLI handler in src/cli/handlers.py
- [x] T022 [US1] Wire add command in src/main.py
- [x] T023 [US1] Add error handling for empty title in cmd_add()

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - View Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can see all tasks with index, title, description, status

**Independent Test**: Add multiple tasks, run view command, verify all tasks displayed correctly

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [x] T024 [P] [US2] Unit test for view_tasks() in tests/test_task.py
- [x] T025 [P] [US2] Unit test for empty list case in tests/test_task.py

### Implementation for User Story 2

- [x] T026 [US2] Implement view_tasks() function in src/models/task.py
- [x] T027 [US2] Handle empty list case in view_tasks()
- [x] T028 [US2] Format task output with index, status, title, description
- [x] T029 [P] [US2] Implement cmd_view() CLI handler in src/cli/handlers.py
- [x] T030 [US2] Wire view command in src/main.py
- [x] T031 [US2] Add friendly empty list message

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Update Task (Priority: P2)

**Goal**: Users can modify task title and/or description

**Independent Test**: Add a task, update its title/description, run view to verify changes reflected

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [x] T032 [P] [US3] Unit test for update_task() in tests/test_task.py
- [x] T033 [P] [US3] Unit test for task ID validation in tests/test_task.py

### Implementation for User Story 3

- [x] T034 [US3] Implement update_task() function in src/models/task.py
- [x] T035 [US3] Add task ID validation in update_task()
- [x] T036 [US3] Add title validation in update_task() when title updated
- [x] T037 [P] [US3] Implement cmd_update() CLI handler in src/cli/handlers.py
- [x] T038 [US3] Parse --title and --description flags in cmd_update()
- [x] T039 [US3] Wire update command in src/main.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Delete Task (Priority: P2)

**Goal**: Users can remove tasks from list with automatic ID reassignment

**Independent Test**: Add multiple tasks, delete one, verify task removed and IDs reassigned

### Tests for User Story 4 (OPTIONAL - only if tests requested) ⚠️

- [x] T040 [P] [US4] Unit test for delete_task() in tests/test_task.py
- [x] T041 [P] [US4] Unit test for ID reassignment after deletion in tests/test_task.py

### Implementation for User Story 4

- [x] T042 [US4] Implement delete_task() function in src/models/task.py
- [x] T043 [US4] Add task ID validation in delete_task()
- [x] T044 [US4] Call _reassign_ids() after deletion in delete_task()
- [x] T045 [P] [US4] Implement cmd_delete() CLI handler in src/cli/handlers.py
- [x] T046 [US4] Wire delete command in src/main.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: User Story 5 - Mark Complete/Incomplete (Priority: P2)

**Goal**: Users can toggle task status between "incomplete" and "complete"

**Independent Test**: Add a task, mark it complete, view to verify status change, mark it incomplete again

### Tests for User Story 5 (OPTIONAL - only if tests requested) ⚠️

- [x] T047 [P] [US5] Unit test for toggle_status() in tests/test_task.py
- [x] T048 [P] [US5] Unit test for status toggle logic in tests/test_task.py

### Implementation for User Story 5

- [x] T049 [US5] Implement toggle_status() function in src/models/task.py
- [x] T050 [US5] Add task ID validation in toggle_status()
- [x] T051 [US5] Implement status toggle logic (incomplete <-> complete)
- [x] T052 [P] [US5] Implement cmd_complete() CLI handler in src/cli/handlers.py
- [x] T053 [US5] Wire complete command in src/main.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T054 [P] Implement show_help() command to display usage information
- [x] T055 Update README.md with complete setup and usage examples
- [x] T056 Add comprehensive error messages for all invalid operations
- [x] T057 Implement consistent output formatting across all commands
- [x] T058 [P] Review code against all constitution principles
- [x] T059 Ensure all type hints are present
- [x] T060 Verify all docstrings are complete
- [x] T061 Run quickstart.md validation

---

[Add more user story phases as needed, following by same pattern]

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed sequentially (P1 → P2) or in parallel if staffed
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Model functions before CLI handlers
- CLI handlers before command wiring in main.py
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T005, T006)
- T011, T012 can run in parallel (both in task.py helper functions)
- T021, T029 (US1 & US2 CLI handlers) can run in parallel after foundational
- T037, T045, T052 (US3, US4, US5 CLI handlers) can run in parallel after P1 stories complete
- T054, T058 (Polish tasks) can run in parallel
- All tests for a user story marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Unit test for validate_title() in tests/test_task.py"
Task: "Unit test for add_task() in tests/test_task.py"

# Launch CLI handler and model together:
Task: "Implement cmd_add() CLI handler in src/cli/handlers.py"
Task: "Add title validation to add_task() function"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Polish → Final demo

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
3. After P1 complete:
   - Developer A: User Story 3
   - Developer B: User Story 4
4. Developer A or B: User Story 5
5. Team: Polish together

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are optional - only include if explicitly requested in specification
- Verify tests fail before implementing (if tests included)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
