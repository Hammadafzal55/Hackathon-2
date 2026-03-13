# Data Model: Advanced Features (008)

**Feature**: 008-advanced-features
**Phase**: 1 — Design
**Date**: 2026-03-07

---

## Database Changes Overview

| Change | Type | Table |
|--------|------|-------|
| Add `tags` column | ALTER | tasks |
| Add `recurrence_rule` column | ALTER | tasks |
| Add `recurrence_parent_id` column | ALTER | tasks |
| Add `next_occurrence` column | ALTER | tasks |
| Create `reminders` table | CREATE | reminders |
| Create `notifications` table | CREATE | notifications |
| Add GIN index on `tasks.tags` | INDEX | tasks |
| Add index on `reminders.fire_at` | INDEX | reminders |
| Add index on `notifications.user_id` | INDEX | notifications |

---

## Entity: Task (MODIFIED)

**Table**: `tasks`

### New Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `tags` | JSONB | No | `'[]'` | Array of tag strings. e.g. `["work", "urgent"]` |
| `recurrence_rule` | JSONB | Yes | `NULL` | Recurrence config. See schema below. |
| `recurrence_parent_id` | UUID | Yes | `NULL` | FK to parent task if this is a generated instance |
| `next_occurrence` | TIMESTAMP | Yes | `NULL` | Next scheduled instance date for recurring tasks |

### Recurrence Rule Schema (JSONB)

```json
{
  "pattern": "daily | weekly | monthly | yearly",
  "interval": 1,
  "end_condition": "never | after_n | by_date",
  "end_after_n": null,
  "end_by_date": null
}
```

| Field | Values | Description |
|-------|--------|-------------|
| `pattern` | daily, weekly, monthly, yearly | How often the task repeats |
| `interval` | integer ≥ 1 | Every N occurrences of the pattern (e.g. every 2 weeks) |
| `end_condition` | never, after_n, by_date | When to stop generating instances |
| `end_after_n` | integer or null | Stop after N total instances (when end_condition = after_n) |
| `end_by_date` | ISO date string or null | Stop after this date (when end_condition = by_date) |

### New Indexes

```sql
-- GIN index for JSONB tag containment queries
CREATE INDEX idx_tasks_tags_gin ON tasks USING GIN (tags);

-- Index for recurrence queries
CREATE INDEX idx_tasks_next_occurrence ON tasks (user_id, next_occurrence)
  WHERE recurrence_rule IS NOT NULL AND next_occurrence IS NOT NULL;

-- Index for recurrence parent lookups
CREATE INDEX idx_tasks_recurrence_parent ON tasks (recurrence_parent_id)
  WHERE recurrence_parent_id IS NOT NULL;
```

### Unique Constraint (idempotency)

```sql
-- Prevents duplicate recurrence instances
CREATE UNIQUE INDEX idx_tasks_recurrence_dedup
  ON tasks (recurrence_parent_id, due_date)
  WHERE recurrence_parent_id IS NOT NULL;
```

### Existing Columns (unchanged)

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | unchanged |
| `user_id` | TEXT | unchanged |
| `title` | VARCHAR | unchanged |
| `description` | VARCHAR | unchanged |
| `status` | VARCHAR | pending/in_progress/completed/cancelled |
| `priority` | INTEGER | 1=Low, 2=Medium, 3=High, 4=Very High, 5=Critical |
| `due_date` | TIMESTAMP | unchanged |
| `created_at` | TIMESTAMP | unchanged |
| `updated_at` | TIMESTAMP | unchanged |
| `completed_at` | TIMESTAMP | unchanged |

---

## Entity: Reminder (NEW)

**Table**: `reminders`

A scheduled notification trigger tied to a task. Created when a user sets a reminder lead time on a task.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID PK | No | gen_random_uuid() | Unique identifier |
| `task_id` | UUID FK | No | — | References tasks(id) ON DELETE CASCADE |
| `lead_time_minutes` | INTEGER | No | — | 15, 60, 180, 1440, or 2880 minutes before due date |
| `fire_at` | TIMESTAMP | No | — | Exact UTC time when notification should be created |
| `status` | VARCHAR(20) | No | `'pending'` | pending / sent / cancelled |
| `created_at` | TIMESTAMP | No | now() | When reminder was created |

### Allowed `lead_time_minutes` values

| Value | Label |
|-------|-------|
| 15 | 15 minutes before |
| 60 | 1 hour before |
| 180 | 3 hours before |
| 1440 | 1 day before |
| 2880 | 2 days before |

### Indexes

```sql
-- Primary query: find all pending reminders due now (runs every 5 min via cron)
CREATE INDEX idx_reminders_pending_fire_at
  ON reminders (fire_at)
  WHERE status = 'pending';

-- Lookups by task (for cascade cancel on complete/delete)
CREATE INDEX idx_reminders_task_id ON reminders (task_id);
```

### State Transitions

```
pending → sent      (when cron fires and notification is created)
pending → cancelled (when parent task is completed or deleted)
sent    → [terminal]
cancelled → [terminal]
```

---

## Entity: Notification (NEW)

**Table**: `notifications`

An in-app alert delivered to a specific user. Created by the reminder cron handler when a reminder's `fire_at` time is reached.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID PK | No | gen_random_uuid() | Unique identifier |
| `user_id` | TEXT | No | — | Owner of this notification |
| `task_id` | UUID | Yes | NULL | Related task (nullable — task may be deleted) |
| `message` | TEXT | No | — | Human-readable notification text |
| `read` | BOOLEAN | No | `false` | Whether user has seen this notification |
| `created_at` | TIMESTAMP | No | now() | When notification was created |

### Indexes

```sql
-- Primary query: fetch unread notifications for a user (30-second poll)
CREATE INDEX idx_notifications_user_unread
  ON notifications (user_id, read, created_at DESC);
```

---

## Entity Relationships

```
tasks (1) ──────────────── (N) reminders
      │                            │
      │ recurrence_parent_id       │ task_id (CASCADE DELETE)
      │
tasks (1) ──── self-ref ──── (N) tasks (recurrence instances)

notifications.task_id ─── (optional ref) ──→ tasks
notifications.user_id ─── (user scoped, no FK to users table)
```

---

## Alembic Migration Plan

**Migration file**: `004_add_advanced_features.py`

```
Upgrade:
  1. ALTER TABLE tasks ADD COLUMN tags JSONB NOT NULL DEFAULT '[]'
  2. ALTER TABLE tasks ADD COLUMN recurrence_rule JSONB
  3. ALTER TABLE tasks ADD COLUMN recurrence_parent_id UUID REFERENCES tasks(id)
  4. ALTER TABLE tasks ADD COLUMN next_occurrence TIMESTAMP
  5. CREATE INDEX idx_tasks_tags_gin ON tasks USING GIN (tags)
  6. CREATE INDEX idx_tasks_next_occurrence ON tasks(user_id, next_occurrence) WHERE recurrence_rule IS NOT NULL
  7. CREATE UNIQUE INDEX idx_tasks_recurrence_dedup ON tasks(recurrence_parent_id, due_date) WHERE recurrence_parent_id IS NOT NULL
  8. CREATE TABLE reminders (id, task_id, lead_time_minutes, fire_at, status, created_at)
  9. CREATE INDEX idx_reminders_pending_fire_at ON reminders(fire_at) WHERE status = 'pending'
  10. CREATE INDEX idx_reminders_task_id ON reminders(task_id)
  11. CREATE TABLE notifications (id, user_id, task_id, message, read, created_at)
  12. CREATE INDEX idx_notifications_user_unread ON notifications(user_id, read, created_at DESC)

Downgrade:
  DROP TABLE notifications
  DROP TABLE reminders
  DROP INDEX idx_tasks_tags_gin
  DROP INDEX idx_tasks_next_occurrence
  DROP INDEX idx_tasks_recurrence_dedup
  ALTER TABLE tasks DROP COLUMN next_occurrence
  ALTER TABLE tasks DROP COLUMN recurrence_parent_id
  ALTER TABLE tasks DROP COLUMN recurrence_rule
  ALTER TABLE tasks DROP COLUMN tags
```

---

## SQLModel Models

### Updated Task Model

```python
class Task(SQLModel, table=True):
    # ... existing fields unchanged ...
    tags: List[str] = Field(default=[], sa_column=Column(JSONB, nullable=False, server_default="'[]'"))
    recurrence_rule: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    recurrence_parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="tasks.id", nullable=True)
    next_occurrence: Optional[datetime] = Field(default=None, nullable=True)
```

### Reminder Model

```python
class Reminder(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    task_id: uuid.UUID = Field(foreign_key="tasks.id")
    lead_time_minutes: int  # 15 | 60 | 180 | 1440 | 2880
    fire_at: datetime
    status: str = Field(default="pending")  # pending | sent | cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Notification Model

```python
class Notification(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str
    task_id: Optional[uuid.UUID] = Field(default=None, nullable=True)
    message: str
    read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Priority Label Mapping (UI only, no schema change)

| DB Value | Display Label | Badge Color |
|----------|--------------|-------------|
| 1 | Low | Gray |
| 2 | Medium | Blue |
| 3 | High | Amber |
| 4 | Very High | Orange |
| 5 | Critical | Red |
