# Contract: Dapr Cron Bindings

**Building Block**: Input Bindings
**Binding Type**: `bindings.cron`

---

## Binding 1: Reminder Check

**Component Name**: `check-reminders-cron`
**Schedule**: `@every 60s`
**Target Endpoint**: `POST /cron/check-reminders`
**File**: `backend/src/api/routes/dapr_events.py`

### Request (from Dapr)

```
POST /cron/check-reminders
Content-Type: application/json

{}
```

Dapr sends an empty JSON body for cron bindings.

### Response

```json
HTTP 200 OK
{}
```

### Behavior

1. Backend queries the `reminders` table for all rows where `status='pending'` AND `fire_at <= NOW()`.
2. For each due reminder: creates a `notifications` row and marks reminder `status='sent'`.
3. If no due reminders: returns 200 with no side effects.
4. Endpoint is idempotent: re-running with the same due reminders produces the same notifications (uses upsert or checks for existing notification).

---

## Binding 2: Recurrence Generation

**Component Name**: `generate-recurrences-cron`
**Schedule**: `@every 300s` (every 5 minutes)
**Target Endpoint**: `POST /cron/generate-recurrences`
**File**: `backend/src/api/routes/dapr_events.py`

### Request (from Dapr)

```
POST /cron/generate-recurrences
Content-Type: application/json

{}
```

### Response

```json
HTTP 200 OK
{}
```

### Behavior

1. Queries tasks with `recurrence_rule != null` and `status != 'completed'`.
2. For each recurring task: generates the next instance(s) if the window is approaching.
3. Idempotent: does not create duplicate instances.

---

## Timing Guarantees

| Guarantee | Details |
|-----------|---------|
| First fire | Immediately on Dapr sidecar startup (at T=0 after schedule starts) |
| Missed ticks | Not retried — cron bindings are best-effort (fire-and-forget) |
| Concurrent calls | Not prevented by Dapr — endpoint must handle concurrent invocations safely |
| Timezone | UTC (no timezone configuration for cron bindings) |

---

## Naming Convention

Dapr maps cron binding component names to HTTP routes by convention:
- Component name `check-reminders-cron` → POST `/cron/check-reminders` (configured in binding YAML as `route`)
- Component name `generate-recurrences-cron` → POST `/cron/generate-recurrences`

The `route` field in the binding component YAML explicitly configures the target path.
