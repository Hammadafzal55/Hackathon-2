# Contract: Dapr Pub/Sub — Task Events

**Building Block**: Pub/Sub
**Component Name**: `pubsub`
**Broker**: Redis (in-cluster, Bitnami Helm chart)
**Topic**: `task-events`

---

## Publisher Contract

**Caller**: `backend/src/services/event_publisher.py`
**Method**: Dapr SDK `client.publish_event()`
**Dapr Sidecar Endpoint**: `POST http://localhost:3500/v1.0/publish/pubsub/task-events`

### Event Payload Schema

```json
{
  "event_type": "task.created | task.updated | task.deleted | task.completed | task.reopened",
  "task_id": "uuid-string",
  "user_id": "uuid-string",
  "timestamp": "ISO-8601 UTC string",
  "changed_fields": ["field1", "field2"],
  "has_recurrence": false,
  "has_reminders": true
}
```

### Event Types

| Event Type | Triggered When |
|------------|----------------|
| `task.created` | POST /api/tasks succeeds |
| `task.updated` | PUT /api/tasks/{id} succeeds |
| `task.deleted` | DELETE /api/tasks/{id} succeeds |
| `task.completed` | PATCH /api/tasks/{id}/complete → status=completed |
| `task.reopened` | PATCH /api/tasks/{id}/complete → status=pending |

### Publisher Behavior

- Non-blocking: `publish_task_event()` is called with `await` but failures are caught and logged at DEBUG level.
- If Dapr sidecar is unavailable (local dev without K8s), the error is swallowed — backend continues normally.
- Event is published with `data_content_type: "application/json"` as a CloudEvent.

---

## Subscriber Contract

**Endpoint**: `POST /task-events`
**File**: `backend/src/api/routes/dapr_events.py`
**Subscription Discovery**: `GET /dapr/subscribe` returns:

```json
[
  {
    "pubsubname": "pubsub",
    "topic": "task-events",
    "route": "/task-events"
  }
]
```

### Subscriber Request (from Dapr)

Dapr wraps the event in a CloudEvent envelope:

```json
{
  "specversion": "1.0",
  "type": "com.dapr.event.sent",
  "source": "flowtodo-backend",
  "id": "uuid",
  "datacontenttype": "application/json",
  "data": {
    "event_type": "task.created",
    "task_id": "...",
    "user_id": "...",
    "timestamp": "...",
    "changed_fields": [],
    "has_recurrence": false,
    "has_reminders": false
  }
}
```

### Subscriber Response

```json
HTTP 200 OK
{
  "status": "SUCCESS"
}
```

Dapr retries delivery if subscriber returns non-200. Subscriber must be idempotent.

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Redis unavailable | Dapr buffers and retries; publisher logs debug warning |
| Subscriber returns 4xx | Dapr does NOT retry (considered processing error) |
| Subscriber returns 5xx | Dapr retries with exponential backoff |
| Subscriber returns 200 SUCCESS | Dapr acknowledges, message removed from queue |
| Duplicate message delivered | Subscriber should be idempotent (log and return 200) |
