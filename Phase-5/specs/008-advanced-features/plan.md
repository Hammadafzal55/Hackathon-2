# Implementation Plan: Advanced Features — Recurring Tasks, Reminders, Tags, Search/Filter/Sort & Dapr

**Branch**: `008-advanced-features` | **Date**: 2026-03-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-advanced-features/spec.md`

---

## Summary

Extend the existing FlowTodo task management application with five capability areas:
1. **Tags** — JSONB array on tasks, chip UI, autocomplete, tag filter
2. **Search / Filter / Sort** — server-side query params on `GET /api/tasks`; real-time client-side debounce
3. **Recurring Tasks** — `recurrence_rule` JSONB on tasks; Dapr cron binding auto-generates instances every 5 minutes
4. **Reminders & Notifications** — `reminders` and `notifications` tables; Dapr cron checks due reminders every 5 minutes; frontend polls every 30 seconds
5. **Dapr Integration** — sidecar for pub/sub (Redis Streams / Kafka), cron bindings, state store, secrets; `task-events` topic published on every mutation
6. **UI Enhancement** — priority badges, due date urgency colours, tag chips, recurrence indicator, notification bell with panel, search/filter/sort controls

---

## Technical Context

**Language/Version**: Python 3.11 (backend) · TypeScript / Next.js 16 (frontend)
**Primary Dependencies**: FastAPI, SQLModel, asyncpg, Alembic, dapr-python-sdk, dapr-ext-fastapi · Next.js 16, React 19, Tailwind CSS 4
**Storage**: Neon Serverless PostgreSQL (existing) · Redis (Dapr pub/sub local) · PostgreSQL (Dapr state store)
**Testing**: pytest + pytest-asyncio (backend) · Jest / React Testing Library (frontend)
**Target Platform**: Linux server (backend) · Vercel (frontend) · Minikube / GKE-AKS (Kubernetes)
**Performance Goals**: Search < 1 s for 10k tasks · Filter/sort < 500 ms · Reminders fire within 5 min of target
**Constraints**: 4 GB DDR3 RAM (local — Dapr + Redis only, no Kafka locally) · Stateless FastAPI (no in-memory session state) · At-least-once event delivery with idempotency

---

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| Agent-first development | ✅ PASS | All code via Claude Code tools |
| Stateless architecture | ✅ PASS | No in-memory state; cron handlers are stateless; event consumers read/write DB only |
| Tool-driven AI behavior | ✅ PASS | MCP tools updated to include tag/recurrence fields |
| Natural language interface | ✅ PASS | AI chat agent can now filter/sort tasks via updated `list_tasks` tool |
| Reliability and persistence | ✅ PASS | All events, reminders, notifications persisted to PostgreSQL |
| Security and authentication | ✅ PASS | All new endpoints require JWT auth; notifications/reminders scoped by user_id |

**Complexity justification** (Dapr sidecar addition):

| Addition | Why Needed | Simpler Alternative Rejected Because |
|----------|-----------|--------------------------------------|
| Dapr sidecar | Required by spec (FR-031); provides pub/sub, cron, state, secrets | APScheduler: ties scheduling to single process, violates stateless principle |
| Redis (local) | Dapr pub/sub component needs a broker | Kafka locally: exceeds 4 GB RAM constraint |
| `reminders` table | Needed for scheduled notification delivery | In-memory queue: lost on restart, violates reliability principle |
| `notifications` table | Needed for persistent unread notification history (FR-011) | Session-only: notifications lost on page refresh |

---

## Project Structure

### Documentation (this feature)

```
specs/008-advanced-features/
├── plan.md              ← this file
├── spec.md
├── research.md          ← Phase 0 complete
├── data-model.md        ← Phase 1 complete
├── quickstart.md        ← Phase 1 complete
├── contracts/
│   ├── tasks-api.yaml           ← enhanced tasks API
│   ├── notifications-api.yaml   ← new notifications API
│   └── dapr-subscriptions.yaml ← Dapr pub/sub + cron contracts
├── checklists/
│   └── requirements.md
└── tasks.md             ← Phase 2 output (sp.tasks command)
```

### Source Code

```
backend/
├── src/
│   ├── models/
│   │   ├── task.py           MODIFY — add tags, recurrence_rule, recurrence_parent_id, next_occurrence
│   │   ├── reminder.py       CREATE — Reminder SQLModel
│   │   └── notification.py   CREATE — Notification SQLModel
│   ├── api/
│   │   ├── routes/
│   │   │   ├── tasks.py          MODIFY — add search/filter/sort query params; publish task-events
│   │   │   ├── reminders.py      CREATE — list/add/delete reminders per task
│   │   │   ├── notifications.py  CREATE — list/read/mark-all-read notifications
│   │   │   └── dapr_events.py    CREATE — GET /dapr/subscribe, POST /task-events, POST /cron/*
│   │   └── schemas/
│   │       ├── task.py       MODIFY — add tags, recurrence_rule, reminders fields
│   │       ├── reminder.py   CREATE — ReminderCreate, ReminderRead
│   │       └── notification.py CREATE — NotificationRead
│   ├── services/
│   │   ├── event_publisher.py    CREATE — publish_task_event() via Dapr SDK
│   │   ├── reminder_service.py   CREATE — check_due_reminders() called by cron handler
│   │   └── recurrence_service.py CREATE — generate_recurrences() called by cron handler
│   └── main.py               MODIFY — include new routers
├── dapr/
│   └── components/
│       ├── pubsub-redis.yaml     CREATE — Redis Streams pub/sub (local/dev)
│       ├── pubsub-kafka.yaml     CREATE — Confluent Kafka pub/sub (cloud)
│       ├── statestore.yaml       CREATE — PostgreSQL state store
│       ├── cron-reminders.yaml   CREATE — @every 5m binding
│       ├── cron-recurrences.yaml CREATE — @every 5m binding
│       └── secretstore.yaml      CREATE — Kubernetes secretstore (cloud)
├── alembic/
│   └── versions/
│       └── 004_add_advanced_features.py  CREATE — migration for tags, reminders, notifications
└── requirements.txt          MODIFY — add dapr, dapr-ext-fastapi

frontend/
├── src/
│   ├── components/
│   │   ├── Tasks/
│   │   │   ├── TaskCard.tsx       MODIFY — add tags chips, priority badge, due date colour, recurrence icon
│   │   │   ├── TaskForm.tsx       MODIFY — add tag input, recurrence fields, reminder checkboxes
│   │   │   ├── TaskList.tsx       MODIFY — add SearchBar, FilterPanel, SortControl above list
│   │   │   ├── SearchBar.tsx      CREATE — debounced search input
│   │   │   ├── FilterPanel.tsx    CREATE — status/priority/tag/date range filters with active chips
│   │   │   ├── SortControl.tsx    CREATE — sort field + direction dropdown
│   │   │   └── TagInput.tsx       CREATE — chip tag input with autocomplete
│   │   └── Notifications/
│   │       ├── NotificationBell.tsx  CREATE — bell icon + unread badge in header
│   │       └── NotificationPanel.tsx CREATE — dropdown list of notifications, mark-read actions
│   ├── Header/
│   │   └── Header.tsx             MODIFY — add NotificationBell component
│   ├── hooks/
│   │   ├── useTasks.ts            MODIFY — add search/filter/sort params
│   │   ├── useNotifications.ts    CREATE — polls /api/notifications every 30s
│   │   └── useTags.ts             CREATE — fetches /api/tags for autocomplete
│   ├── types/
│   │   ├── task.ts                MODIFY — add tags, recurrence_rule, reminders, next_occurrence
│   │   └── notification.ts        CREATE — NotificationRead type
│   └── lib/
│       └── api.ts                 MODIFY — add notification, reminder, tag API methods
└── app/
    └── tasks/
        └── page.tsx               MODIFY — pass filter/sort state to TaskList
```

---

## Phase 0: Research — Complete

All decisions resolved. See [research.md](research.md).

**Key decisions:**
- Tags: JSONB array on tasks table (no join table)
- Pub/sub: Redis Streams local, Kafka (Confluent) cloud — Dapr component swap
- Cron: Two separate `bindings.cron` components, both `@every 5m`
- Notifications: 30-second HTTP poll from Next.js (stateless, no SSE/WebSocket)
- Search: Backend ILIKE + JSONB `@>` operator — no separate search engine
- Recurrence idempotency: `UNIQUE (recurrence_parent_id, due_date)` constraint

---

## Phase 1: Design — Complete

### Data Model

See [data-model.md](data-model.md) for full schema.

**Summary of DB changes:**
- `tasks`: +4 columns (`tags JSONB`, `recurrence_rule JSONB`, `recurrence_parent_id UUID`, `next_occurrence TIMESTAMP`)
- `reminders`: NEW table (task_id FK CASCADE, lead_time_minutes, fire_at, status)
- `notifications`: NEW table (user_id, task_id, message, read, created_at)
- New indexes: GIN on tags, partial index on pending reminders, unique constraint for recurrence dedup

### API Contracts

See [contracts/tasks-api.yaml](contracts/tasks-api.yaml) and [contracts/notifications-api.yaml](contracts/notifications-api.yaml).

**New/modified endpoints:**

| Method | Path | Change |
|--------|------|--------|
| GET | /api/tasks | + search, status, priority, tags, due_before, due_after, sort_by, sort_dir params |
| POST | /api/tasks | + tags[], recurrence_rule, reminders[] fields |
| PUT | /api/tasks/{id} | + tags[], recurrence_rule fields |
| GET | /api/tasks/{id}/reminders | NEW |
| POST | /api/tasks/{id}/reminders | NEW |
| DELETE | /api/reminders/{id} | NEW |
| GET | /api/tags | NEW — user tag autocomplete |
| GET | /api/notifications | NEW |
| PATCH | /api/notifications/{id}/read | NEW |
| POST | /api/notifications/mark-all-read | NEW |
| GET | /dapr/subscribe | NEW — Dapr subscription registry |
| POST | /task-events | NEW — pub/sub consumer |
| POST | /cron/check-reminders | NEW — Dapr cron binding handler |
| POST | /cron/generate-recurrences | NEW — Dapr cron binding handler |

### Dapr Components

See [contracts/dapr-subscriptions.yaml](contracts/dapr-subscriptions.yaml).

### Quickstart

See [quickstart.md](quickstart.md) for local dev setup with Dapr.

---

## Phase 2: Implementation Architecture

### Backend Implementation Order

1. **Migration** (`004_add_advanced_features.py`) — must run first, unlocks all other work
2. **Models** — Reminder, Notification SQLModel classes + updated Task
3. **Schemas** — Pydantic request/response schemas for new fields
4. **Event Publisher** — `publish_task_event()` using dapr-python-sdk, graceful no-op if Dapr unavailable
5. **Task routes** — Search/filter/sort query params + publish event after each mutation
6. **Reminder routes** — CRUD on reminders; validate due_date exists; validate fire_at not in past
7. **Notification routes** — list with unread filter, mark-read, mark-all-read
8. **Dapr routes** — `/dapr/subscribe`, `/task-events`, `/cron/check-reminders`, `/cron/generate-recurrences`
9. **Services** — `reminder_service.py` (find due reminders → create notifications), `recurrence_service.py` (compute next date → create task instances)
10. **Dapr component YAMLs** — all 6 files in `dapr/components/`
11. **MCP tool update** — update `list_tasks` tool to accept tags/search/filter params so AI chat agent benefits

### Frontend Implementation Order

1. **Types** — update `task.ts`, create `notification.ts`
2. **API client** — add notification, reminder, tag methods to `api.ts`
3. **TagInput** — chip input with autocomplete suggestions from `/api/tags`
4. **TaskForm** — add TagInput, recurrence toggle+selector, reminder checkboxes
5. **TaskCard** — priority badge (color + label), due date urgency colour, tag chips, recurrence icon (🔄)
6. **SearchBar** — debounced input (300ms), clears to show full list on empty
7. **FilterPanel** — status multiselect, priority multiselect, tag multiselect, due date range pickers; "active" chip strip; clear-all button
8. **SortControl** — dropdown for sort_by + sort_dir toggle
9. **TaskList** — integrate SearchBar + FilterPanel + SortControl; pass combined query state to `useTasks` hook
10. **useTasks hook** — add search/filter/sort params, re-fetch on change
11. **useNotifications hook** — poll `/api/notifications?unread=true` every 30s, store unread count
12. **NotificationBell** — badge with unread count in Header
13. **NotificationPanel** — dropdown list, "Mark all read" action, individual dismiss
14. **Header** — add NotificationBell

### UI Design Decisions

**Priority Badges** (TaskCard):
```
priority 1 → [Low]        gray-500    bg-gray-100
priority 2 → [Medium]     blue-500    bg-blue-100
priority 3 → [High]       amber-500   bg-amber-100
priority 4 → [Very High]  orange-500  bg-orange-100
priority 5 → [Critical]   red-500     bg-red-100
```

**Due Date Urgency Colours** (TaskCard):
```
overdue          → text-red-500   (past due_date)
due today        → text-orange-400
due tomorrow     → text-amber-400
due this week    → text-yellow-400
future / no date → text-gray-400
```

**Tag Chips** (TaskCard):
```
Displayed as small rounded pills: bg-white/10 border border-white/20 text-xs
Max 3 shown inline, "+N more" overflow label
```

**Recurrence Indicator** (TaskCard):
```
Small 🔄 icon + pattern label (e.g. "Daily") bottom-right of card
```

**Notification Bell** (Header):
```
Bell icon — shows red badge with unread count (hidden when 0)
Click → NotificationPanel dropdown slides in from top-right
```

**Search + Filter Bar** (above TaskList):
```
[ 🔍 Search tasks...                    ] [ Filters ▼ ] [ Sort: Due Date ↑ ]
                                                          ↓ (when filters active)
[ work × ] [ priority:High × ] [ due:this-week × ]  [ Clear all ]
```

**Active filter chips** shown below the search bar when filters are active.

---

## Architectural Decision Record Suggestion

📋 Architectural decision detected: **Dapr as distributed runtime layer (pub/sub + cron + state + secrets)** — Document reasoning and tradeoffs?
Run `/sp.adr dapr-as-distributed-runtime`

📋 Architectural decision detected: **Redis Streams (local) / Kafka (cloud) as pub/sub broker via Dapr abstraction** — Document reasoning and tradeoffs?
Run `/sp.adr pubsub-broker-selection`

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Dapr sidecar startup failures block the backend | High | Implement graceful fallback — backend starts and serves requests; event publishing skipped if Dapr unavailable |
| Cron fires twice simultaneously (duplicate reminders) | Medium | `UPDATE reminders SET status='sent' WHERE id=? AND status='pending'` — only first update wins |
| Recurrence dedup failure | Medium | `INSERT ... ON CONFLICT (recurrence_parent_id, due_date) DO NOTHING` |
| Monthly edge dates (31st of month) | Low | Use `dateutil.relativedelta` for correct date arithmetic; falls back to last day of month |
| Search performance at 10k tasks | Low | GIN index on tags + standard B-tree indexes on title (via ILIKE) — verified sufficient at spec scale |
