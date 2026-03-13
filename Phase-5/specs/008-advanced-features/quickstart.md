# Quickstart: Advanced Features (008)

**Feature**: 008-advanced-features
**Date**: 2026-03-07

---

## What's Being Added

This feature adds to the existing FlowTodo application:
1. **Tags** on tasks (JSONB, chip UI)
2. **Recurring tasks** (auto-generated instances via Dapr cron)
3. **Due date reminders** (in-app notifications via Dapr cron)
4. **Search / Filter / Sort** on the task list (backend query params)
5. **Notifications panel** in the header
6. **Dapr sidecar** integration (pub/sub, cron bindings, state store, secrets)
7. **Enhanced UI** (priority badges, due date urgency colors, tag chips, notification bell)

---

## Prerequisites

- Existing Phase-5 environment running (backend + frontend)
- Docker installed (for running Redis locally for Dapr pub/sub)
- Dapr CLI installed: https://docs.dapr.io/getting-started/install-dapr-cli/
- Dapr initialized: `dapr init`

---

## Step 1: Database Migration

```bash
cd backend
source venv/bin/activate   # or: venv\Scripts\activate on Windows

# Run the new migration
alembic upgrade head
```

Verifies: `reminders` and `notifications` tables created; `tasks` table has `tags`, `recurrence_rule`, `recurrence_parent_id`, `next_occurrence` columns.

---

## Step 2: Install New Dependencies

```bash
cd backend
pip install dapr dapr-ext-fastapi
pip install -r requirements.txt
```

---

## Step 3: Update Backend .env

Add to `backend/.env`:

```env
# Dapr settings (local dev — Dapr sidecar manages these)
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001
PUBSUB_NAME=pubsub
TOPIC_TASK_EVENTS=task-events
```

No Kafka credentials needed for local dev (Redis Streams via Dapr).

---

## Step 4: Start Dapr Components (Local Redis)

```bash
# Start Redis (for Dapr pub/sub)
docker run -d --name redis -p 6379:6379 redis:alpine

# Verify Dapr is initialized
dapr --version
```

---

## Step 5: Run Backend with Dapr Sidecar

Instead of `uvicorn src.main:app`, run with Dapr:

```bash
cd backend
dapr run \
  --app-id flowtodo-backend \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --resources-path ./dapr/components \
  -- uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The Dapr sidecar will:
- Load `dapr/components/pubsub-redis.yaml` → Redis Streams pub/sub
- Load `dapr/components/statestore.yaml` → PostgreSQL state store
- Load `dapr/components/cron-reminders.yaml` → call `POST /cron/check-reminders` every 5 min
- Load `dapr/components/cron-recurrences.yaml` → call `POST /cron/generate-recurrences` every 5 min
- Register subscriptions by calling `GET /dapr/subscribe`

---

## Step 6: Run Frontend

```bash
cd frontend
npm run dev
```

No new env vars needed for the frontend (uses existing `NEXT_PUBLIC_API_BASE_URL`).

---

## Verify the Integration

### Tags
1. Create a task, add tags "work" and "urgent"
2. Task card shows tag chips
3. Filter by tag "work" → only tasks with "work" appear

### Search
1. Type in the search bar → task list filters in real time
2. Results match title, description, or tags

### Recurring Tasks
1. Create a task with recurrence "daily", set due_date to 1 minute from now
2. Wait 5 minutes (cron fires) → a new task instance appears automatically
3. New instance has the same title, next day due date

### Reminders / Notifications
1. Create a task with due_date = 10 minutes from now, add reminder "15 minutes before"
2. Wait (cron fires every 5 min) → notification appears in the bell icon
3. Click bell → see notification panel with message

### Priority Badges
- Tasks with priority 5 show red "Critical" badge
- Tasks with priority 1 show gray "Low" badge

---

## Running Without Dapr (Fallback)

The backend runs normally without Dapr — task CRUD, search, filter, sort, and tags all work. Only recurring task generation and reminder firing require Dapr cron. The backend gracefully skips pub/sub publish if Dapr sidecar is unavailable.

```bash
# Normal run (no recurring/reminder automation)
cd backend
uvicorn src.main:app --reload
```

---

## Dapr Component Files Location

```
backend/dapr/components/
├── pubsub-redis.yaml       # Local dev: Redis Streams
├── pubsub-kafka.yaml       # Cloud: Confluent Kafka (swap in)
├── statestore.yaml         # PostgreSQL state store
├── cron-reminders.yaml     # @every 5m → POST /cron/check-reminders
├── cron-recurrences.yaml   # @every 5m → POST /cron/generate-recurrences
└── secretstore.yaml        # Kubernetes secrets (cloud only)
```

---

## Troubleshooting

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| Dapr sidecar not starting | Redis not running | `docker start redis` |
| Cron not firing | Wrong component path | Check `--resources-path` in dapr run |
| Tags not persisting | Migration not run | `alembic upgrade head` |
| Notifications not appearing | Cron not running | Verify Dapr sidecar is active |
| Search returns no results | Empty search term | Ensure query param is non-empty |
