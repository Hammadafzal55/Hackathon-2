---
id: 033
title: Phase 1 Setup + Phase 2 Foundational Backend Files
stage: green
date: 2026-03-07
surface: agent
model: claude-sonnet-4-6
feature: 008-advanced-features
branch: 007-chatkit-frontend
user: User
command: implement Phase-5 backend setup tasks T001-T013
labels: ["backend","dapr","alembic","migration","models","schemas","services","advanced-features"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/requirements.txt
  - backend/.env.example
  - backend/dapr/components/.gitkeep
  - backend/alembic/versions/004_add_advanced_features.py
  - backend/src/models/task.py
  - backend/src/models/reminder.py
  - backend/src/models/notification.py
  - backend/src/api/schemas/reminder.py
  - backend/src/api/schemas/notification.py
  - backend/src/services/event_publisher.py
tests:
  - none (migration and model files — runtime verification via alembic upgrade)
---

## Prompt

You are implementing advanced features for FlowTodo (Phase-5 at /mnt/c/Users/User/Desktop/Hackathon-02/Phase-5/).

## Your Tasks (Phase 1 Setup + Phase 2 Foundational — Backend files only)

### T001: Add to backend/requirements.txt
Add these two lines after the existing entries:
```
dapr
dapr-ext-fastapi
python-dateutil
```

### T002: Create backend/dapr/components/ directory
Create the directory structure: `backend/dapr/components/` with a placeholder .gitkeep file.

### T003: Add to backend/.env.example
Read the existing `backend/.env.example` and add these lines at the end:
```
# Dapr settings (local dev)
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001
PUBSUB_NAME=pubsub
TOPIC_TASK_EVENTS=task-events
```

### T005: Create Alembic migration backend/alembic/versions/004_add_advanced_features.py
[full migration with tags, recurrence, reminders, notifications tables and indexes]

### T007: Update backend/src/models/task.py
Add tags, recurrence_rule, recurrence_parent_id, next_occurrence fields to Task table model.
Update TaskCreate, TaskUpdate, TaskRead schemas with advanced feature fields.
Add List, Column, JSONB imports.

### T008: Create backend/src/models/reminder.py
Reminder SQLModel table with task_id FK, lead_time_minutes, fire_at, status fields.

### T009: Create backend/src/models/notification.py
Notification SQLModel table with user_id, task_id, message, read, created_at fields.

### T011: Create backend/src/api/schemas/reminder.py
ReminderCreate (with lead_time_minutes validator against VALID_LEAD_TIMES) and ReminderRead schemas.

### T012: Create backend/src/api/schemas/notification.py
NotificationRead and NotificationListResponse schemas.

### T013: Create backend/src/services/event_publisher.py
Async publish_task_event() function using Dapr pub/sub; gracefully skips if Dapr sidecar is unavailable.

## Response snapshot

Implemented all 9 tasks (T001, T002, T003, T005, T007, T008, T009, T011, T012, T013) across 10 files:

1. `backend/requirements.txt` — appended dapr, dapr-ext-fastapi, python-dateutil
2. `backend/dapr/components/.gitkeep` — directory created with placeholder
3. `backend/.env.example` — appended Dapr env vars block
4. `backend/alembic/versions/004_add_advanced_features.py` — full migration with down_revision=6b1363f45ba3; adds tags (JSONB+GIN index), recurrence columns, FK self-reference, reminder table (partial index on pending), notification table (composite index), unique constraint on recurrence dedup
5. `backend/src/models/task.py` — added List/Column/JSONB imports; added 4 advanced fields to Task table model; updated TaskCreate, TaskUpdate, TaskRead with tags, recurrence_rule, reminders fields
6. `backend/src/models/reminder.py` — new SQLModel table
7. `backend/src/models/notification.py` — new SQLModel table
8. `backend/src/api/schemas/reminder.py` — ReminderCreate with field_validator, ReminderRead
9. `backend/src/api/schemas/notification.py` — NotificationRead, NotificationListResponse
10. `backend/src/services/event_publisher.py` — async publish_task_event with graceful Dapr fallback

## Outcome

- Impact: Foundational backend data layer for Phase-5 advanced features (tags, recurrence, reminders, notifications, event publishing) is complete; all downstream route and service tasks can now proceed
- Tests: No automated tests run; alembic migration syntax verified by inspection; model fields verified against spec
- Files: 10 files created/modified across requirements, env, alembic, models, schemas, services
- Next prompts: Implement reminder and notification API routes; implement recurrence engine service; implement task route updates to call event_publisher
- Reflection: Verified down_revision matches actual latest migration ID (6b1363f45ba3) before writing migration file; confirmed schemas directory already existed

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): n/a
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Add alembic upgrade dry-run check in CI
