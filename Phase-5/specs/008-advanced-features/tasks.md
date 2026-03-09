# Tasks: Advanced Features — Recurring Tasks, Reminders, Tags, Search/Filter/Sort & Dapr

**Input**: Design documents from `/specs/008-advanced-features/`
**Prerequisites**: plan.md ✅ · spec.md ✅ · research.md ✅ · data-model.md ✅ · contracts/ ✅ · quickstart.md ✅

**Organization**: Tasks grouped by user story for independent implementation and testing.
**Total Tasks**: 68 | **Phases**: 8

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[Story]**: User story label (US1–US5)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install new dependencies, create Dapr component directories, update config files.

- [X] T001 Add `dapr` and `dapr-ext-fastapi` to `backend/requirements.txt`
- [X] T002 [P] Create directory `backend/dapr/components/` for Dapr component YAML files
- [X] T003 [P] Add Dapr env vars (`DAPR_HTTP_PORT`, `PUBSUB_NAME`, `TOPIC_TASK_EVENTS`) to `backend/.env.example`
- [X] T004 [P] Create `frontend/src/types/notification.ts` with `NotificationRead` interface

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database migration, new models, updated schemas, and router registration — MUST complete before any user story work.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Create Alembic migration `backend/alembic/versions/004_add_advanced_features.py` — adds `tags JSONB`, `recurrence_rule JSONB`, `recurrence_parent_id UUID`, `next_occurrence TIMESTAMP` columns to `tasks`; creates `reminders` and `notifications` tables; adds GIN index on `tasks.tags`; adds partial index on `reminders(fire_at) WHERE status='pending'`; adds unique constraint `(recurrence_parent_id, due_date)`; adds index `notifications(user_id, read, created_at DESC)`
- [X] T006 Run migration: `alembic upgrade head` in `backend/` — verify all columns and tables exist
- [X] T007 [P] Update `backend/src/models/task.py` — add fields: `tags: List[str]` (JSONB, default `[]`), `recurrence_rule: Optional[dict]` (JSONB, nullable), `recurrence_parent_id: Optional[UUID]` (FK self-ref, nullable), `next_occurrence: Optional[datetime]` (nullable)
- [X] T008 [P] Create `backend/src/models/reminder.py` — `Reminder` SQLModel with fields: `id (UUID PK)`, `task_id (UUID FK → tasks.id CASCADE)`, `lead_time_minutes (int)`, `fire_at (datetime)`, `status (str, default 'pending')`, `created_at (datetime)`
- [X] T009 [P] Create `backend/src/models/notification.py` — `Notification` SQLModel with fields: `id (UUID PK)`, `user_id (str)`, `task_id (Optional[UUID])`, `message (str)`, `read (bool, default False)`, `created_at (datetime)`
- [X] T010 Update `backend/src/api/schemas/task.py` (or equivalent) — add `tags: List[str]`, `recurrence_rule: Optional[RecurrenceRule]`, `next_occurrence: Optional[datetime]`, `reminders: List[ReminderRead]` to `TaskRead`; add `tags`, `recurrence_rule`, `reminders: List[ReminderCreate]` to `TaskCreate` and `TaskUpdate`
- [X] T011 [P] Create `backend/src/api/schemas/reminder.py` — `ReminderCreate` (lead_time_minutes: int, validated to enum [15,60,180,1440,2880]), `ReminderRead` (id, task_id, lead_time_minutes, fire_at, status, created_at)
- [X] T012 [P] Create `backend/src/api/schemas/notification.py` — `NotificationRead` (id, user_id, task_id, message, read, created_at); `NotificationListResponse` (notifications, total_count, unread_count)
- [X] T013 Create `backend/src/services/event_publisher.py` — `publish_task_event(event_type, task_id, user_id, changed_fields, has_recurrence, has_reminders)` using `dapr.clients.DaprClient`; wraps in try/except and logs warning (not error) if Dapr sidecar unavailable — ensures backend starts without Dapr
- [X] T014 Update `backend/src/main.py` — import and `include_router` for: `reminders`, `notifications`, `dapr_events` (new routers to be created in subsequent phases)

**Checkpoint**: Run `alembic upgrade head` → all tables and columns exist. Backend starts without errors. Dapr import does not crash if sidecar absent.

---

## Phase 3: User Story 1 — Create a Recurring Task (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks with a recurrence schedule; new instances auto-generate every 5 minutes via Dapr cron binding.

**Independent Test**: Create a task with `recurrence_rule: {pattern: "daily", interval: 1, end_condition: "never"}` and `due_date` = 5 minutes ago via API. Wait for cron handler invocation → verify a new Task row appears in DB with `recurrence_parent_id` set and `due_date` incremented by 1 day.

### Backend — US1

- [X] T015 [US1] Create `backend/src/services/recurrence_service.py` — implement `compute_next_occurrence(pattern, interval, current_due_date) → datetime` using `dateutil.relativedelta` (handles 31st-of-month edge); implement `generate_due_recurrences(session) → int` that queries tasks where `recurrence_rule IS NOT NULL AND next_occurrence <= NOW()`, creates new Task rows via `INSERT ... ON CONFLICT (recurrence_parent_id, due_date) DO NOTHING`, updates parent `next_occurrence`, returns count of instances created
- [X] T016 [US1] Update `backend/src/api/routes/tasks.py` — `POST /api/tasks`: accept `recurrence_rule` and `reminders` in request body; after task creation compute `next_occurrence` if recurrence_rule present; create `Reminder` rows for each reminder in `reminders[]` (validate `fire_at = due_date - lead_time_minutes` is in the future); call `publish_task_event("task.created", ...)`
- [X] T017 [US1] Update `backend/src/api/routes/tasks.py` — `PUT /api/tasks/{id}`: accept updated `recurrence_rule`; recompute `next_occurrence` if recurrence_rule changed; call `publish_task_event("task.updated", ...)`
- [X] T018 [US1] Create `backend/src/api/routes/dapr_events.py` — implement `POST /cron/generate-recurrences`: calls `recurrence_service.generate_due_recurrences(session)`, returns `{"generated": count}`; implement `GET /dapr/subscribe` returning subscription list (skeleton for now — full pub/sub consumer added in US5)
- [X] T019 [P] [US1] Create Dapr component file `backend/dapr/components/cron-recurrences.yaml` — `type: bindings.cron`, `schedule: "@every 5m"`, `name: cron-recurrences`

### Frontend — US1

- [X] T020 [P] [US1] Update `frontend/src/types/task.ts` — add `recurrence_rule?: RecurrenceRule | null`, `next_occurrence?: string | null`, `recurrence_parent_id?: string | null`, `tags: string[]`, `reminders?: ReminderRead[]` to `Task` and `TaskCreate` interfaces; add `RecurrenceRule` and `ReminderRead` interfaces
- [X] T021 [US1] Create `frontend/src/components/Tasks/RecurrenceForm.tsx` — renders: toggle "Repeat this task", pattern selector (Daily/Weekly/Monthly/Yearly), interval input ("every N"), end condition radio (Never / After N times / By date) with conditional inputs; props: `value: RecurrenceRule | null`, `onChange(rule: RecurrenceRule | null)`
- [X] T022 [US1] Update `frontend/src/components/TaskForm/TaskForm.tsx` (or `TaskForm.tsx`) — add `RecurrenceForm` below due date field; wire recurrence_rule into form state; include in `TaskCreate` / `TaskUpdate` payload sent to API
- [X] T023 [US1] Update `frontend/src/components/TaskCard/TaskCard.tsx` (or `TaskItem.tsx`) — add recurrence indicator: if `task.recurrence_rule`, show 🔄 icon + pattern label (e.g. "Daily") as a small badge bottom-right of card
- [X] T024 [US1] Update `frontend/src/lib/api.ts` — ensure `createTask` and `updateTask` pass `recurrence_rule` and `reminders` fields in request body

**Checkpoint**: Create a task with "Weekly" recurrence via the UI form. Task card shows 🔄 Weekly. After cron fires (or manually hitting `POST /cron/generate-recurrences`), a new task row appears in the task list with next week's due date.

---

## Phase 4: User Story 2 — Receive a Due Date Reminder (Priority: P1)

**Goal**: Users set reminder lead times on tasks; when the reminder time arrives, an in-app notification appears in the header bell icon within the next poll cycle (≤ 30 seconds).

**Independent Test**: Create task with `due_date` = 2 minutes from now, reminder `lead_time_minutes = 15` (fires immediately since fire_at = due_date - 15 min = past). Manually call `POST /cron/check-reminders` → verify a `notifications` row is created with correct message. Open frontend → notification bell shows badge count 1 within 30 seconds.

### Backend — US2

- [X] T025 [US2] Create `backend/src/services/reminder_service.py` — implement `check_due_reminders(session) → int`: queries `reminders WHERE status='pending' AND fire_at <= NOW()`; for each: creates `Notification(user_id=task.user_id, task_id=reminder.task_id, message=f"Reminder: '{task.title}' is due in {label}")` and updates `reminder.status = 'sent'`; uses `UPDATE ... WHERE status='pending'` for idempotency (only first updater wins); returns count processed
- [X] T026 [US2] Update `backend/src/api/routes/dapr_events.py` — add `POST /cron/check-reminders`: calls `reminder_service.check_due_reminders(session)`, returns `{"processed": count}`
- [X] T027 [US2] Create `backend/src/api/routes/reminders.py` — `GET /api/tasks/{task_id}/reminders` (list reminders, auth-checked via task ownership); `POST /api/tasks/{task_id}/reminders` (create reminder: validate task has due_date, validate fire_at is in the future, create Reminder row); `DELETE /api/reminders/{reminder_id}` (delete specific reminder, ownership via task)
- [X] T028 [US2] Create `backend/src/api/routes/notifications.py` — `GET /api/notifications?unread=true&limit=20&offset=0` (returns NotificationListResponse); `PATCH /api/notifications/{id}/read` (set read=True); `POST /api/notifications/mark-all-read` (UPDATE WHERE user_id=current AND read=False)
- [X] T029 [P] [US2] Create Dapr component file `backend/dapr/components/cron-reminders.yaml` — `type: bindings.cron`, `schedule: "@every 5m"`, `name: cron-reminders`
- [X] T030 [P] [US2] Create `backend/dapr/components/pubsub-redis.yaml` — `type: pubsub.redis`, `name: pubsub`, host `redis:6379`, consumerGroup `flowtodo-consumers`, processingTimeout 30s, maxRetries 3
- [X] T031 [P] [US2] Create `backend/dapr/components/pubsub-kafka.yaml` — `type: pubsub.kafka`, `name: pubsub`, brokers from `secretKeyRef`, SASL_SSL, saslMechanism PLAIN, consumerGroup `flowtodo-consumers` (cloud swap-in for Redis)
- [X] T032 [US2] Update `backend/src/api/routes/tasks.py` — `DELETE /api/tasks/{id}` and `PATCH /api/tasks/{id}/complete`: after task deleted or completed, run `UPDATE reminders SET status='cancelled' WHERE task_id=? AND status='pending'`

### Frontend — US2

- [X] T033 [P] [US2] Create `frontend/src/types/notification.ts` — `NotificationRead` interface: `{ id, user_id, task_id, message, read, created_at }` and `NotificationListResponse: { notifications, total_count, unread_count }`
- [X] T034 [US2] Update `frontend/src/lib/api.ts` — add methods: `getNotifications(unread?, limit?, offset?)`, `markNotificationRead(id)`, `markAllNotificationsRead()`, `getTaskReminders(taskId)`, `addReminder(taskId, lead_time_minutes)`, `deleteReminder(reminderId)`
- [X] T035 [US2] Create `frontend/src/hooks/useNotifications.ts` — polls `GET /api/notifications?unread=true` every 30 seconds; returns `{ notifications, unreadCount, markRead, markAllRead, refresh }`; clears interval on unmount
- [X] T036 [US2] Create `frontend/src/components/Notifications/NotificationBell.tsx` — bell SVG icon; red badge showing `unreadCount` (hidden when 0); click toggles `NotificationPanel`; uses `useNotifications` hook
- [X] T037 [US2] Create `frontend/src/components/Notifications/NotificationPanel.tsx` — dropdown panel (absolute positioned, z-50); lists notifications with task name, message, time-ago; "Mark all read" button; individual notification click → `markRead(id)` + navigate to task if task_id present; empty state "No notifications"
- [X] T038 [US2] Update `frontend/src/components/Header/Header.tsx` — import and render `<NotificationBell />` in header right section (next to user menu, before sign-out)
- [X] T039 [US2] Update `frontend/src/components/TaskForm/TaskForm.tsx` — add reminder selector section (shown only when due_date is set): checkboxes for "15 min before", "1 hour before", "3 hours before", "1 day before", "2 days before"; pass selected `reminders[]` in task create/update payload

**Checkpoint**: Create task with due date + reminder. Bell icon appears in header. After cron fires (or manual POST to `/cron/check-reminders`), unread badge appears on bell. Click bell → panel shows reminder message.

---

## Phase 5: User Story 3 — Organize Tasks with Tags (Priority: P2)

**Goal**: Users add/remove free-text tags on tasks; tags appear as chips on task cards; filter by tag is functional.

**Independent Test**: Create task with tags `["work", "urgent"]`. Task card shows two chips. Use tag filter to show "work" → only tasks with "work" tag appear.

### Backend — US3

- [X] T040 [US3] Create `backend/src/api/routes/tags.py` — `GET /api/tags`: queries `SELECT DISTINCT jsonb_array_elements_text(tags) FROM tasks WHERE user_id = current_user_id ORDER BY 1`; returns `{"tags": ["personal", "urgent", "work", ...]}`
- [X] T041 [US3] Update `backend/src/api/routes/tasks.py` — `GET /api/tasks`: add `tags` query param (comma-separated); for each tag, add filter `Task.tags.cast(JSONB).contains([tag])`; ensure `POST /api/tasks` and `PUT /api/tasks/{id}` deduplicate tags before saving (use `list(dict.fromkeys(tags))`)
- [X] T042 [US3] Register `tags` router in `backend/src/main.py` — `app.include_router(tags.router, prefix="/api", tags=["tags"])`

### Frontend — US3

- [X] T043 [P] [US3] Create `frontend/src/hooks/useTags.ts` — fetches `GET /api/tags` on mount; returns `{ tags: string[], loading, error }`
- [X] T044 [US3] Create `frontend/src/components/Tasks/TagInput.tsx` — chip-style tag input: text input with autocomplete dropdown from `useTags()`; Enter/comma to confirm tag; × button to remove chip; deduplicates on add; props: `value: string[]`, `onChange(tags: string[])`
- [X] T045 [US3] Update `frontend/src/components/TaskForm/TaskForm.tsx` — add `<TagInput />` below description field; wire to form state; included in create/update payload
- [X] T046 [US3] Update `frontend/src/components/TaskCard/TaskCard.tsx` (or `TaskItem.tsx`) — render `task.tags` as colored chip pills (`bg-white/10 border border-white/20 text-xs rounded-full px-2 py-0.5`); show first 3 tags inline, "+N more" badge if overflow; empty tags = show nothing

**Checkpoint**: Create a task with tags "work" and "urgent" via UI. Task card shows both chips. Refresh page → tags still present. Filter by "work" → list narrows correctly.

---

## Phase 6: User Story 4 — Search, Filter, and Sort Tasks (Priority: P2)

**Goal**: Task list has a search bar, collapsible filter panel, and sort control; all three work together and are applied server-side.

**Independent Test**: Create 10 tasks with mixed priorities, statuses, tags, and due dates. Search "grocery" → only matching tasks show. Apply priority=High filter → further narrows. Sort by due date asc → ordered correctly. Clear all → full list restored.

### Backend — US4

- [X] T047 [US4] Update `backend/src/api/routes/tasks.py` — `GET /api/tasks`: add query params `search: str = ""`, `status: str = ""`, `priority: str = ""`, `due_before: Optional[datetime]`, `due_after: Optional[datetime]`, `sort_by: str = "created_at"`, `sort_dir: str = "desc"`, `limit: int = 50`, `offset: int = 0`; build dynamic SQLAlchemy `select(Task).where(...)` with: ILIKE on title + description if search provided; tags JSONB containment for each tag; status IN list; priority IN list; due_date range; ORDER BY chosen field + direction; return `{"tasks": [...], "total_count": N}`
- [X] T048 [US4] Update `backend/src/api/schemas/task.py` — update `GET /api/tasks` response to return paginated shape `{"tasks": List[TaskRead], "total_count": int}` instead of bare array (breaking change — update frontend api.ts accordingly)

### Frontend — US4

- [X] T049 [P] [US4] Create `frontend/src/components/Tasks/SearchBar.tsx` — controlled text input with magnifier icon; debounces onChange 300ms before propagating; clear (×) button when non-empty; props: `value: string`, `onChange(query: string)`
- [X] T050 [P] [US4] Create `frontend/src/components/Tasks/FilterPanel.tsx` — collapsible panel (toggle button shows active filter count badge): status multi-select (pending/in_progress/completed/cancelled), priority multi-select (Low/Medium/High/Very High/Critical), tag multi-select (from useTags), due date range (date-before + date-after inputs); renders active filter chips strip below the bar; "Clear all" button; props: `filters: FilterState`, `onChange(filters: FilterState)`
- [X] T051 [P] [US4] Create `frontend/src/components/Tasks/SortControl.tsx` — dropdown to select `sort_by` (Due Date / Priority / Created / Title) with direction toggle (↑ asc / ↓ desc) button; props: `sortBy: string`, `sortDir: "asc"|"desc"`, `onChange(sortBy, sortDir)`
- [X] T052 [US4] Update `frontend/src/hooks/useTasks.ts` — accept `SearchFilterSort` params object (`search, status[], priority[], tags[], due_before, due_after, sort_by, sort_dir`); pass as query string to `GET /api/tasks`; re-fetch when any param changes; handle new paginated response shape
- [X] T053 [US4] Update `frontend/src/components/TaskList.tsx` (or Tasks page component) — add `SearchBar`, `FilterPanel`, `SortControl` above the task list; manage combined filter state with `useState`; pass to `useTasks` hook; render active filter chips from FilterPanel
- [X] T054 [US4] Update `frontend/app/tasks/page.tsx` — ensure search/filter/sort state is managed at page level and passed down; no navigation required (all within tasks page)
- [X] T055 [US4] Update `frontend/src/components/TaskCard/TaskCard.tsx` — add **priority badge**: map priority 1→5 to label+color (`Low`=gray, `Medium`=blue, `High`=amber, `Very High`=orange, `Critical`=red); render as small rounded badge; add **due date urgency colour**: `overdue`=text-red-400, `today`=text-orange-400, `tomorrow`=text-amber-400, `this week`=text-yellow-400, `future/none`=text-gray-400

**Checkpoint**: Task list shows search bar + filter toggle + sort dropdown. Search "work" → list narrows. Add priority filter High+Critical → further narrows. Sort by Due Date asc → ordered. Clear all → full list. Priority badge and due date colours correct on all cards.

---

## Phase 7: User Story 5 — Task Events Processed Reliably (Priority: P3)

**Goal**: Every task mutation publishes a `task-events` message to Dapr pub/sub; a consumer subscribes and logs/processes it; cron handlers are idempotent and recover from temporary outages.

**Independent Test**: Create a task via API → verify `task-events` message published (check Dapr logs). Manually POST to `/cron/check-reminders` twice back-to-back → verify only one notification created per reminder (idempotency).

### Backend — US5

- [X] T056 [US5] Update `backend/src/api/routes/tasks.py` — ensure `publish_task_event()` is called after every mutation: `POST /api/tasks` → `task.created`; `PUT /api/tasks/{id}` → `task.updated`; `PATCH /api/tasks/{id}/complete` → `task.completed`; `DELETE /api/tasks/{id}` → `task.deleted`
- [X] T057 [US5] Update `backend/src/api/routes/dapr_events.py` — implement `GET /dapr/subscribe` returning full subscription list `[{"pubsubname": "pubsub", "topic": "task-events", "routes": {"default": "/task-events"}}]`; implement `POST /task-events` consumer: validates CloudEvent envelope, extracts `data`, logs event, returns `{"status": "SUCCESS"}` (HTTP 200); handler is idempotent (safe to call multiple times)
- [X] T058 [P] [US5] Create `backend/dapr/components/statestore.yaml` — `type: state.postgresql`, `name: statestore`, `connectionString` from `secretKeyRef`
- [X] T059 [P] [US5] Create `backend/dapr/components/secretstore.yaml` — `type: secretstores.kubernetes`, `name: secretstore` (cloud only; local uses env vars directly)

**Checkpoint**: Run backend with `dapr run --resources-path ./dapr/components`. Create a task → Dapr sidecar logs show `task-events` message published. POST `/cron/check-reminders` twice → notifications table has exactly one row per reminder.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: MCP tool update, error handling hardening, quickstart validation.

- [X] T060 Update `backend/src/mcp_tools/handlers.py` — `list_tasks_handler`: add optional `tags: List[str]`, `search: str`, `status_filter` params and pass to DB query — AI chat agent benefits from same search/filter capabilities as the REST API
- [X] T061 Update `backend/src/services/ai_agent.py` — update `list_tasks` function_tool signature to accept `tags: str = ""` and `search: str = ""` parameters; pass to handler
- [X] T062 [P] Add graceful Dapr fallback logging in `backend/src/services/event_publisher.py` — ensure `try/except` logs `WARNING: Dapr unavailable, event not published` instead of raising; verify backend starts cleanly without Dapr sidecar
- [X] T063 [P] Update `backend/dapr/components/` — add `dapr run` example command to `backend/README.md` (or create it): `dapr run --app-id flowtodo-backend --app-port 8000 --dapr-http-port 3500 --resources-path ./dapr/components -- uvicorn src.main:app --reload`
- [X] T064 [P] Update `frontend/src/lib/api.ts` — update `fetchTasks` to handle new paginated response shape `{tasks: Task[], total_count: number}` (from T048 breaking change)
- [X] T065 Validate all UI flows against `specs/008-advanced-features/quickstart.md` — create task with recurrence + tags + reminder via UI; verify all visual elements appear (🔄 badge, tag chips, priority badge, due date colour, notification bell); document any discrepancies
- [X] T066 [P] Update `todo-chatbot/values.yaml` Helm chart — add Redis deployment spec and update backend env vars with Dapr sidecar annotation comments for future Minikube deployment

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    └─→ Phase 2 (Foundational) ← BLOCKS ALL STORIES
            ├─→ Phase 3 (US1: Recurring Tasks)   — P1, start first
            ├─→ Phase 4 (US2: Reminders)          — P1, can parallel with US1
            ├─→ Phase 5 (US3: Tags)               — P2, after foundational
            ├─→ Phase 6 (US4: Search/Filter/Sort) — P2, after foundational
            └─→ Phase 7 (US5: Event Architecture) — P3, after US1+US2 tasks exist
                    └─→ Phase 8 (Polish)
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|-----------|------------------|
| US1 Recurring Tasks | Phase 2 complete | US2 (backend separate), US3, US4 |
| US2 Reminders | Phase 2 complete | US1 (backend separate), US3, US4 |
| US3 Tags | Phase 2 complete | US4, US1 frontend, US2 frontend |
| US4 Search/Filter/Sort | Phase 2 complete, T047-T048 | US3 frontend |
| US5 Event Architecture | T056 (task routes publish events) | — |

### Within Each User Story

```
Backend tasks → Frontend types → API client → Hooks → Components → Integration
Models → Services → Routes → UI
```

---

## Parallel Execution Examples

### Phase 2 Foundational (parallel opportunities)

```
Parallel group A:
  T007 Update Task model (task.py)
  T008 Create Reminder model (reminder.py)
  T009 Create Notification model (notification.py)
  T011 Create reminder schemas
  T012 Create notification schemas

Sequential:
  T005 → T006 (migration must run before models are usable in tests)
  T013 Event publisher (depends on dapr installed via T001)
  T014 Register routers (depends on routers existing — done in later phases)
```

### Phase 3 US1 Recurring Tasks (parallel opportunities)

```
Parallel group (backend + frontend simultaneously):
  T015 recurrence_service.py
  T019 cron-recurrences.yaml
  T020 Update task.ts types (frontend)

Sequential after T015:
  T016 → T017 → T018 (route updates depend on service)
  T021 → T022 → T023 → T024 (form depends on component)
```

### Phase 4 US2 Reminders (parallel opportunities)

```
Parallel:
  T029 cron-reminders.yaml
  T030 pubsub-redis.yaml
  T031 pubsub-kafka.yaml
  T033 notification.ts types (frontend)

Parallel backend group:
  T025 reminder_service.py
  T027 reminders routes
  T028 notifications routes

Parallel frontend group (after T034 api.ts):
  T035 useNotifications hook
  T036 NotificationBell
  T037 NotificationPanel
```

### Phase 6 US4 Search/Filter/Sort (parallel opportunities)

```
Parallel frontend components (all different files):
  T049 SearchBar.tsx
  T050 FilterPanel.tsx
  T051 SortControl.tsx
  T055 TaskCard priority badges + due date colours
```

---

## Implementation Strategy

### MVP First (US1 + US2 — both P1)

1. Complete Phase 1: Setup (T001–T004)
2. Complete Phase 2: Foundational (T005–T014) — run migration first
3. Complete Phase 3: US1 Recurring Tasks
4. Complete Phase 4: US2 Reminders + Notifications
5. **STOP and VALIDATE**: Recurring tasks auto-generate, reminders create notifications, bell shows badge
6. Deploy/demo — core advanced features working

### Incremental Delivery

1. Setup + Foundational → DB ready
2. US1 + US2 → Recurring tasks + Reminders (P1 complete)
3. US3 → Tags (P2 increment)
4. US4 → Search/Filter/Sort (P2 increment — biggest UI improvement)
5. US5 → Event architecture hardened
6. Polish → AI chat agent enhanced, Helm updated

### Parallel Team Strategy

With frontend and backend developers working concurrently:
- **Backend dev**: T005 → T006 → T007-T013 (Phase 2) → T015-T018 (US1 backend) → T025-T032 (US2 backend)
- **Frontend dev**: T001, T003, T004 (setup) → T020-T024 (US1 frontend) → T033-T039 (US2 frontend)
- After Phase 2 backend complete: frontend dev can run migrations and test API while building components

---

## Task Count Summary

| Phase | Tasks | Parallelizable |
|-------|-------|---------------|
| Phase 1: Setup | 4 | 3 |
| Phase 2: Foundational | 10 | 5 |
| Phase 3: US1 Recurring | 10 | 4 |
| Phase 4: US2 Reminders | 15 | 8 |
| Phase 5: US3 Tags | 7 | 2 |
| Phase 6: US4 Search/Filter/Sort | 9 | 5 |
| Phase 7: US5 Event Architecture | 4 | 2 |
| Phase 8: Polish | 7 | 4 |
| **Total** | **66** | **33** |

---

## Notes

- `[P]` tasks write to different files with no shared in-progress dependencies — safe to run concurrently
- Run `alembic upgrade head` (T006) before testing any route
- Run backend with `dapr run ...` for cron handlers to fire; standard `uvicorn` works for everything else
- Dapr publish is a graceful no-op if sidecar absent — backend never crashes without Dapr
- Kafka (`pubsub-kafka.yaml`) is the cloud deployment swap for `pubsub-redis.yaml` — only one is active at a time
- Commit after each checkpoint to isolate rollback scope
- Recurrence idempotency enforced by DB unique constraint — safe to hit cron handler multiple times
