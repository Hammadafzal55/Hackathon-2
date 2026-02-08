---
description: "Task list for Todo Backend Service implementation"
---

# Tasks: Todo Backend Service

**Input**: Design documents from `/specs/001-todo-backend/`
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

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan in backend/
- [X] T002 Initialize Python project with FastAPI, SQLModel, asyncpg dependencies in backend/requirements.txt
- [X] T003 [P] Create backend/src directory structure (models, database, api/routes, services)
- [X] T004 [P] Create backend/tests directory structure (unit, integration)
- [X] T005 Create .env.example file with DATABASE_URL variable

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Setup database connection and session in backend/src/database/database.py
- [X] T007 [P] Create base SQLModel class in backend/src/database/base.py
- [X] T008 [P] Create database initialization script in backend/src/database/init.py
- [X] T009 [P] Configure Alembic for database migrations in backend/alembic/
- [X] T010 [P] Create initial migration for tasks and users tables in backend/alembic/versions/
- [X] T011 Create main FastAPI application in backend/src/main.py
- [X] T012 Configure environment variables management in backend/src/config.py
- [X] T013 Setup error handling infrastructure in backend/src/exceptions.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Create and Manage Personal Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to create, view, update, and delete personal tasks through a backend API with the ability to mark tasks as complete or incomplete and retrieve specific tasks by ID

**Independent Test**: Can be fully tested by making API calls to create a task, list all tasks, update a task, and delete a task, delivering the complete task management experience.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T014 [P] [US1] Contract test for task management endpoints in backend/tests/contract/test_tasks_contract.py
- [X] T015 [P] [US1] Integration test for full task lifecycle in backend/tests/integration/test_task_lifecycle.py

### Implementation for User Story 1

- [X] T016 [P] [US1] Create Task model in backend/src/models/task.py
- [X] T017 [P] [US1] Create User model in backend/src/models/user.py
- [X] T018 [US1] Implement TaskService in backend/src/services/task_service.py (depends on T016, T017)
- [X] T019 [US1] Implement POST /api/{user_id}/tasks endpoint in backend/src/api/routes/tasks.py
- [X] T020 [US1] Implement GET /api/{user_id}/tasks endpoint in backend/src/api/routes/tasks.py
- [X] T021 [US1] Implement GET /api/{user_id}/tasks/{id} endpoint in backend/src/api/routes/tasks.py
- [X] T022 [US1] Implement PUT /api/{user_id}/tasks/{id} endpoint in backend/src/api/routes/tasks.py
- [X] T023 [US1] Implement DELETE /api/{user_id}/tasks/{id} endpoint in backend/src/api/routes/tasks.py
- [X] T024 [US1] Implement PATCH /api/{user_id}/tasks/{id}/complete endpoint in backend/src/api/routes/tasks.py
- [X] T025 [US1] Add validation and error handling for all task endpoints
- [X] T026 [US1] Add logging for task operations

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Retrieve Individual Task Details (Priority: P2)

**Goal**: Enable users to retrieve detailed information about a specific task by its unique identifier

**Independent Test**: Can be fully tested by creating a task and retrieving its details, delivering the ability to access individual task information.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [X] T027 [P] [US2] Contract test for GET /api/{user_id}/tasks/{id} in backend/tests/contract/test_get_task_contract.py
- [X] T028 [P] [US2] Integration test for task retrieval in backend/tests/integration/test_get_task.py

### Implementation for User Story 2

- [X] T029 [P] [US2] Enhance Task model with additional detail fields in backend/src/models/task.py (depends on T016)
- [X] T030 [US2] Enhance TaskService with detailed retrieval methods in backend/src/services/task_service.py (depends on T018)
- [X] T031 [US2] Enhance GET /api/{user_id}/tasks/{id} endpoint to return full details in backend/src/api/routes/tasks.py (depends on T021)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Toggle Task Completion Status (Priority: P3)

**Goal**: Enable users to mark tasks as complete or incomplete to track their progress

**Independent Test**: Can be fully tested by creating a task, toggling its completion status, and verifying the change persists, delivering the core todo tracking functionality.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [X] T032 [P] [US3] Contract test for PATCH /api/{user_id}/tasks/{id}/complete in backend/tests/contract/test_toggle_completion_contract.py
- [X] T033 [P] [US3] Integration test for task completion toggle in backend/tests/integration/test_toggle_completion.py

### Implementation for User Story 3

- [X] T034 [P] [US3] Enhance TaskService with completion toggle methods in backend/src/services/task_service.py (depends on T018)
- [X] T035 [US3] Enhance PATCH /api/{user_id}/tasks/{id}/complete endpoint with proper state transition logic in backend/src/api/routes/tasks.py (depends on T024)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T036 [P] Documentation updates in backend/README.md
- [X] T037 Code cleanup and refactoring across all modules
- [X] T038 Performance optimization for database queries
- [X] T039 [P] Additional unit tests in backend/tests/unit/
- [X] T040 Security hardening and input validation
- [X] T041 Run quickstart.md validation to ensure setup instructions work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds upon US1 components but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Builds upon US1 components but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Database tables created before API endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for task management endpoints in backend/tests/contract/test_tasks_contract.py"
Task: "Integration test for full task lifecycle in backend/tests/integration/test_task_lifecycle.py"

# Launch all models for User Story 1 together:
Task: "Create Task model in backend/src/models/task_model.py"
Task: "Create User model in backend/src/models/user_model.py"
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
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence