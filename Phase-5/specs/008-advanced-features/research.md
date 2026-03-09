# Research: Advanced Features — Recurring Tasks, Reminders, Tags, Search/Filter/Sort & Dapr

**Feature**: 008-advanced-features
**Phase**: 0 — Research
**Date**: 2026-03-07

---

## Decision 1: Tags Storage — JSONB Array vs Separate Table

**Decision**: JSONB array column (`tags: List[str]`) directly on the `tasks` table.

**Rationale**:
- Tags are user-scoped strings with no shared taxonomy — no normalization benefit from a separate table.
- PostgreSQL JSONB supports GIN indexing for array containment queries (`@>` operator) — fast enough for 10k tasks.
- Avoids JOIN complexity on every task query.
- SQLModel stores it as `JSON` type; Alembic migrates as `JSONB` via `postgresql_using`.

**Alternatives considered**:
- Separate `tags` table with many-to-many join: rejected — overkill for single-user scoped free-text labels, adds JOIN to every list query.
- PostgreSQL native ARRAY type: rejected — JSONB is more flexible for SQLModel serialization and compatible with existing JSON field patterns in the codebase.

---

## Decision 2: Pub/Sub Broker — Redis Streams (default) vs Kafka

**Decision**: Redis Streams as the default Dapr pub/sub component for local/dev. Kafka (Confluent Cloud) component YAML provided as a drop-in alternative for cloud deployment.

**Rationale**:
- Dapr abstracts the broker entirely — switching from Redis Streams to Kafka is a single component YAML swap, zero application code change.
- Redis is already used for Dapr state store, reducing additional infrastructure dependencies for local dev.
- The 4GB RAM constraint makes running a full Kafka broker locally infeasible; Redis is lightweight.
- For cloud deployment (Part B/C), the Kafka component YAML targets Confluent Cloud with SASL_SSL authentication.

**Alternatives considered**:
- Kafka locally (Redpanda): rejected due to memory constraints (4GB DDR3).
- NATS JetStream: viable alternative but Redis Streams is simpler since Redis is already needed.

---

## Decision 3: Recurrence Instance Generation — Cron Binding

**Decision**: Dapr cron input binding fires every 5 minutes and invokes `POST /cron/generate-recurrences` on the backend. The handler queries recurring tasks whose `next_occurrence` is in the past, creates new instances, and updates the `next_occurrence` timestamp.

**Rationale**:
- Cron binding is the canonical Dapr pattern for scheduled work — fully managed, no custom scheduler needed.
- 5-minute polling is within the 5-minute SLA from SC-003.
- Idempotency enforced by unique constraint on `(recurrence_parent_id, due_date)`.

**Alternatives considered**:
- On task completion, immediately schedule next: rejected — misses occurrences if task is never marked complete (user forgets).
- APScheduler in FastAPI process: rejected — ties scheduling to a single process, violates stateless architecture principle.

---

## Decision 4: Notification Delivery — HTTP Polling

**Decision**: Frontend polls `GET /api/notifications?unread=true` every 30 seconds. Backend writes notifications to the `notifications` table when a reminder fires (via Dapr cron handler).

**Rationale**:
- Spec explicitly limits scope to in-app notifications — no real-time requirement stated.
- 30-second polling satisfies SC-002 (reminders within 5 minutes of target) with plenty of margin.
- Zero additional infrastructure (no WebSocket server, no SSE stream management).
- Stateless — aligns with constitution principle.

**Alternatives considered**:
- Server-Sent Events (SSE): better latency but requires persistent HTTP connections — complicates load balancing and violates stateless principle.
- WebSocket: lowest latency but highest complexity, violates stateless architecture.

---

## Decision 5: Search Implementation — Backend ILIKE + JSONB

**Decision**: All search/filter/sort logic runs server-side on the database. The `GET /api/tasks` endpoint accepts query parameters; the backend builds a dynamic SQLAlchemy query with:
- `ILIKE '%query%'` for title and description text search
- `tags @> '["tag"]'::jsonb` for tag containment search
- `WHERE` clauses for status, priority, due date range filters
- `ORDER BY` clause for sort

**Rationale**:
- No separate search engine required at this scale (up to 10k tasks per user).
- PostgreSQL GIN index on `tags` makes JSONB containment fast.
- Backend search ensures consistent results across all clients and sessions.

**Alternatives considered**:
- Client-side filtering: rejected — breaks pagination, doesn't scale, exposes all user data to browser.
- Elasticsearch/Meilisearch: rejected — massive operational overhead for single-user task lists.

---

## Decision 6: Dapr Pub/Sub Pattern for FastAPI

**Pattern selected**: Programmatic subscription via `GET /dapr/subscribe` endpoint returning subscription metadata, with topic-specific POST handlers.

```
GET  /dapr/subscribe       → returns subscription list (Dapr calls this at startup)
POST /task-events          → handles task lifecycle events
POST /cron/check-reminders     → Dapr cron binding (every 5 min)
POST /cron/generate-recurrences → Dapr cron binding (every 5 min)
```

**Publishing**: Use `dapr-python-sdk` (`DaprClient().publish_event(...)`) synchronously after each task mutation.

---

## Decision 7: Dapr State Store

**Decision**: Use PostgreSQL as Dapr state store (reuses existing Neon connection). No Redis state store needed — pub/sub is Redis Streams, state store is Postgres.

**Rationale**: Avoids introducing Redis as a second data store just for Dapr state. PostgreSQL supports strong consistency. Reuses existing Neon Serverless connection.

---

## Decision 8: Frontend Priority Display

**Decision**: Map existing 1–5 integer priority to named labels with color-coded badges:

| Value | Label | Color |
|-------|-------|-------|
| 1 | Low | Gray |
| 2 | Medium | Blue |
| 3 | High | Yellow/Amber |
| 4 | Very High | Orange |
| 5 | Critical | Red |

Existing priority field on Task model (1–5 integer) requires no schema change — only UI display enhancement.

---

## Dapr Component YAML Patterns

### pubsub-redis.yaml (default)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: "redis:6379"
  - name: consumerGroup
    value: "flowtodo-consumers"
  - name: processingTimeout
    value: "30s"
  - name: maxRetries
    value: "3"
```

### pubsub-kafka.yaml (cloud, Confluent)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    secretKeyRef:
      name: kafka-secret
      key: brokers
  - name: authRequired
    value: "true"
  - name: saslUsername
    secretKeyRef:
      name: kafka-secret
      key: sasl-username
  - name: saslPassword
    secretKeyRef:
      name: kafka-secret
      key: sasl-password
  - name: saslMechanism
    value: "PLAIN"
  - name: securityProtocol
    value: "SASL_SSL"
  - name: consumerGroup
    value: "flowtodo-consumers"
```

### cron-reminders.yaml
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: cron-reminders
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: "@every 5m"
```

### cron-recurrences.yaml
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: cron-recurrences
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: "@every 5m"
```

---

## JSONB Search Patterns (SQLAlchemy Async)

```python
# ILIKE text search
Task.title.ilike(f"%{query}%")

# JSONB array containment (tags @> '["tag"]')
from sqlalchemy import cast, text
from sqlalchemy.dialects.postgresql import JSONB
Task.tags.cast(JSONB).contains(cast([tag], JSONB))

# Combined multi-tag filter (task has ALL specified tags)
from sqlalchemy import and_
conditions = [Task.tags.cast(JSONB).contains(cast([t], JSONB)) for t in tags]
stmt = select(Task).where(and_(*conditions))
```

---

## Key Library Versions

| Library | Version | Purpose |
|---------|---------|---------|
| dapr-python-sdk | >=1.13 | Dapr pub/sub, state, bindings |
| dapr | latest sidecar | Dapr runtime |
| sqlalchemy | >=2.0 (async) | JSONB queries |
| alembic | >=1.13 | DB migrations |
