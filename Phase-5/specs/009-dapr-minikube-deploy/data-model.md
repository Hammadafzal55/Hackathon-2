# Data Model: Dapr Component Configuration Schemas

**Feature**: 009-dapr-minikube-deploy
**Date**: 2026-03-11
**Note**: This feature is infrastructure/configuration focused. "Data model" covers the Dapr component YAML schemas, Kubernetes resource schemas, and configuration object shapes — not database tables.

---

## Dapr Component Schema

All Dapr components follow this base structure:

```
DaprComponent:
  apiVersion: dapr.io/v1alpha1
  kind: Component
  metadata:
    name: <string>              # Referenced by application code as pubsub/statestore/secretstore name
    namespace: <string>         # Must match application pod namespace (default)
  spec:
    type: <string>              # Building block type (pubsub.redis, state.redis, etc.)
    version: v1
    metadata:
      - name: <key>
        value: <value>          # OR secretKeyRef for secret values
```

---

## Component 1: Pub/Sub (Redis)

**Name**: `pubsub`
**Type**: `pubsub.redis`
**Used by**: `event_publisher.py` (PUBSUB_NAME=pubsub), `dapr_events.py` subscriber

| Field | Value | Description |
|-------|-------|-------------|
| `redisHost` | `redis-master.default.svc.cluster.local:6379` | In-cluster Redis master |
| `redisPassword` | secretKeyRef → `flowtodo-secrets.redis-password` | Pulled from K8s Secret |
| `consumerID` | `flowtodo-backend` | Consumer group ID |
| `enableTLS` | `false` | Local dev, no TLS needed |

**Topic**: `task-events`
**Publisher endpoint**: via Dapr sidecar HTTP `POST /v1.0/publish/pubsub/task-events`
**Subscriber route**: `POST /task-events` on the backend app

---

## Component 2: State Store (Redis)

**Name**: `statestore`
**Type**: `state.redis`
**Used by**: Future use (sessions, cache); demonstrates State building block

| Field | Value | Description |
|-------|-------|-------------|
| `redisHost` | `redis-master.default.svc.cluster.local:6379` | Same Redis instance |
| `redisPassword` | secretKeyRef → `flowtodo-secrets.redis-password` | Pulled from K8s Secret |
| `actorStateStore` | `false` | Not using Actors |

---

## Component 3: Secrets Store (Kubernetes)

**Name**: `kubernetes`
**Type**: `secretstores.kubernetes`
**Used by**: Backend `secrets_loader.py` at startup

| Field | Value | Description |
|-------|-------|-------------|
| (no metadata fields) | — | K8s secret store has no required metadata |

**Access pattern**: Dapr Secrets API
`GET http://localhost:3500/v1.0/secrets/kubernetes/flowtodo-secrets`

**Returns** (from K8s Secret `flowtodo-secrets`):
| Key | Description |
|-----|-------------|
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Better Auth / JWT signing secret |
| `JWT_SECRET_KEY` | Same as BETTER_AUTH_SECRET (alias) |
| `AI_API_KEY` | OpenRouter API key |
| `redis-password` | Redis password for Dapr component auth |

---

## Component 4: Cron Binding — Reminder Check

**Name**: `check-reminders-cron`
**Type**: `bindings.cron`
**Target endpoint**: `POST /cron/check-reminders`

| Field | Value | Description |
|-------|-------|-------------|
| `schedule` | `@every 60s` | Fire every 60 seconds |

**Dapr invocation**: Dapr POSTs `{}` body to `http://localhost:<app-port>/cron/check-reminders`

---

## Component 5: Cron Binding — Recurrence Generation

**Name**: `generate-recurrences-cron`
**Type**: `bindings.cron`
**Target endpoint**: `POST /cron/generate-recurrences`

| Field | Value | Description |
|-------|-------|-------------|
| `schedule` | `@every 300s` | Fire every 5 minutes |

---

## Component 6: Dapr Tracing Configuration

**Kind**: `Configuration`
**Name**: `appconfig`

```
DaprConfiguration:
  apiVersion: dapr.io/v1alpha1
  kind: Configuration
  metadata:
    name: appconfig
    namespace: default
  spec:
    tracing:
      samplingRate: "1"          # 100% sampling for local dev
      zipkin:
        endpointAddress: http://zipkin.default.svc.cluster.local:9411/api/v2/spans
```

---

## Kubernetes Resources

### Secret: `flowtodo-secrets`

```
K8sSecret:
  apiVersion: v1
  kind: Secret
  metadata:
    name: flowtodo-secrets
    namespace: default
  type: Opaque
  stringData:                    # Base64-encoded by kubectl apply
    DATABASE_URL: <value>
    BETTER_AUTH_SECRET: <value>
    JWT_SECRET_KEY: <value>
    AI_API_KEY: <value>
    redis-password: ""           # Empty for local dev Redis (no auth)
```

### Helm Chart Dependencies

```
Chart.yaml dependencies:
  - name: redis
    version: "20.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
```

```
values.yaml redis section:
  redis:
    enabled: true
    architecture: standalone
    auth:
      enabled: false             # No password for local dev simplicity
    master:
      persistence:
        enabled: false           # Ephemeral for local dev
```

### Backend Pod Annotations (added to backend-deployment.yaml)

```
podAnnotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "flowtodo-backend"
  dapr.io/app-port: "8000"
  dapr.io/config: "appconfig"
  dapr.io/log-level: "info"
```

### Zipkin Deployment

```
ZipkinDeployment:
  image: openzipkin/zipkin:latest
  port: 9411
  service: ClusterIP
  name: zipkin
  namespace: default
```

---

## Configuration Object: secrets_loader.py

```python
SecretsConfig:
  dapr_port: int = 3500               # Dapr sidecar HTTP port (env: DAPR_HTTP_PORT)
  store_name: str = "kubernetes"       # Dapr component name
  secret_name: str = "flowtodo-secrets"

  # Keys to load
  keys:
    - DATABASE_URL
    - BETTER_AUTH_SECRET
    - JWT_SECRET_KEY
    - AI_API_KEY

  # Fallback behavior
  fallback: use os.getenv() if Dapr sidecar unreachable (local dev without K8s)
```

---

## File Layout

```
todo-chatbot/
├── Chart.yaml                          (add redis dependency)
├── values.yaml                         (add dapr + redis + zipkin sections)
├── charts/                             (Helm dependency artifacts)
└── templates/
    ├── backend-deployment.yaml         (add Dapr annotations)
    ├── deployment.yaml                 (frontend — optional Dapr annotations)
    ├── zipkin-deployment.yaml          (NEW)
    ├── zipkin-service.yaml             (NEW)
    ├── k8s-secret.yaml                 (NEW: flowtodo-secrets)
    └── dapr/
        ├── pubsub.yaml                 (NEW: Dapr Pub/Sub component)
        ├── statestore.yaml             (NEW: Dapr State Store component)
        ├── secretstore.yaml            (NEW: Dapr Secrets Store component)
        ├── cron-check-reminders.yaml   (NEW: Cron binding - reminders)
        ├── cron-recurrences.yaml       (NEW: Cron binding - recurrences)
        └── tracing-config.yaml         (NEW: Dapr Configuration for Zipkin)

backend/
└── src/
    └── services/
        └── secrets_loader.py           (NEW: Dapr Secrets API client)

scripts/
├── deploy.sh                           (NEW: full setup script)
└── teardown.sh                         (NEW: full teardown script)
```
