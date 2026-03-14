# Contract: Dapr Service Invocation

**Building Block**: Service Invocation
**Security**: Mutual TLS (mTLS) enforced by Dapr sentry (automatic)
**Tracing**: Zipkin (all invocations traced automatically)

---

## Service Registry

| Service | App ID | Port | Dapr Enabled |
|---------|--------|------|--------------|
| FlowTodo Backend | `flowtodo-backend` | 8000 | Yes |
| FlowTodo Frontend | `flowtodo-frontend` | 3000 | Optional (for tracing only) |

App IDs are set via the `dapr.io/app-id` pod annotation.

---

## Demonstration: Self-Invocation Test Endpoint

**Purpose**: Prove mTLS service invocation and distributed tracing work without requiring 2 distinct services.

**Trigger**: `GET /api/dapr/self-invoke-test`
**Action**: Backend calls itself via Dapr sidecar:

```
GET http://localhost:3500/v1.0/invoke/flowtodo-backend/method/api/health
```

**Expected Result**:
- Dapr sidecar intercepts the call, applies mTLS, adds trace headers, forwards to target.
- Both the outbound span (caller) and inbound span (callee) appear in Zipkin with correct parent-child relationship.
- Response: 200 with health status.

### Request

```
GET /api/dapr/self-invoke-test
Authorization: Bearer <jwt-token>
```

### Response

```json
HTTP 200 OK
{
  "status": "ok",
  "invocation_result": {
    "status": "healthy"
  },
  "dapr_app_id": "flowtodo-backend",
  "trace_id": "abc123..."
}
```

---

## Dapr Service Invocation API

### Caller Side

```
POST/GET/PUT/DELETE http://localhost:3500/v1.0/invoke/{app-id}/method/{method-path}
```

Headers forwarded automatically by Dapr:
- `traceparent` (W3C Trace Context)
- `dapr-app-id`

### Target Side

Target receives the original HTTP method and path, stripping the Dapr prefix. No code changes needed in the target service — it's a normal HTTP endpoint.

---

## mTLS Configuration

Dapr mTLS is **enabled by default** when Dapr is initialized on Kubernetes. Configuration:
- Certificate rotation: managed by Dapr Sentry (automatic, 24h certificates)
- Trust domain: `cluster.local`
- No explicit configuration needed — zero-config mTLS

---

## Zipkin Trace Structure

For a service invocation call, Zipkin shows:

```
Trace: [trace-id]
  └─ Span: flowtodo-backend → GET /api/health (client span)
       └─ Span: flowtodo-backend → GET /api/health (server span)
```

Zipkin UI accessible at: `http://localhost:9411` (after `kubectl port-forward svc/zipkin 9411:9411`)

---

## Retry Policy

Dapr applies automatic retries for service invocation failures:

| Scenario | Behavior |
|----------|----------|
| Target pod not ready | Retry 3 times with 1s backoff (Dapr default) |
| Target returns 5xx | Retry per resiliency policy (if configured) |
| Target returns 4xx | No retry (client error) |
| Network timeout | Dapr retries up to configured limit |

For local dev, default retry behavior is sufficient. Resiliency policies (CRD) are out of scope.
