# Implementation Plan: Local Deployment with Full Dapr on Minikube

**Branch**: `009-dapr-minikube-deploy` | **Date**: 2026-03-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/009-dapr-minikube-deploy/spec.md`

---

## Summary

Deploy FlowTodo (Next.js frontend + FastAPI backend) to a local Minikube cluster with the full Dapr runtime, covering all 5 building blocks: Pub/Sub (Redis), State Store (Redis), Cron Bindings (reminders + recurrences), Kubernetes Secrets Store, and Service Invocation with mTLS + Zipkin tracing. The existing `todo-chatbot/` Helm chart is extended with Dapr annotations, Redis as a Helm subchart, Zipkin, and Dapr component manifests. A new `secrets_loader.py` module loads secrets from the Dapr Secrets API at startup. A `scripts/deploy.sh` script enables one-command local deployment.

---

## Technical Context

**Language/Version**: Python 3.11 (backend), Node.js 20 (frontend)
**Primary Dependencies**: FastAPI, Dapr Python SDK, Next.js 16, Helm 3.14, Dapr 1.14, Redis 7
**Storage**: Neon Serverless PostgreSQL (external, existing), Redis (in-cluster, new for Dapr Pub/Sub + State)
**Testing**: Manual end-to-end verification via kubectl logs and Zipkin UI; no automated test suite for infrastructure
**Target Platform**: Minikube (local Kubernetes, single-node, Linux/macOS/WSL2)
**Project Type**: Web application (frontend + backend) + infrastructure (K8s manifests + Helm chart)
**Performance Goals**: All pods Running ≤5 min; pub/sub roundtrip ≤10s; cron fires within 5s of schedule
**Constraints**: Local-only (no cloud); ≥8 GB RAM for Minikube; `imagePullPolicy: Never` (local images)
**Scale/Scope**: Single replica per service, local dev only

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Stateless Architecture | ✅ PASS | FastAPI remains stateless; Dapr State Store is external |
| Security and Authentication | ✅ PASS | Secrets moved to K8s Secret + Dapr Secrets Store; JWT unchanged |
| Reliability and Persistence | ✅ PASS | Dapr sidecar graceful fallback already implemented |
| Tool-driven AI Behavior | ✅ PASS | No AI changes; existing MCP tools unchanged |
| No manual coding | ✅ PASS | All changes via spec-driven implementation |
| Database | ✅ PASS | Neon PostgreSQL unchanged; Redis is additive for Dapr only |

**Gate Result**: PASS — no violations.

---

## Project Structure

### Documentation (this feature)

```text
specs/009-dapr-minikube-deploy/
├── spec.md              ✅ Done
├── plan.md              ✅ This file
├── research.md          ✅ Done
├── data-model.md        ✅ Done
├── quickstart.md        ✅ Done
├── contracts/
│   ├── pubsub-contract.md              ✅ Done
│   ├── cron-binding-contract.md        ✅ Done
│   ├── secrets-contract.md             ✅ Done
│   └── service-invocation-contract.md  ✅ Done
├── checklists/
│   └── requirements.md  ✅ Done
└── tasks.md             ⏳ Phase 2 output (/sp.tasks)
```

### Source Code Layout

```text
todo-chatbot/                           (EXTENDED from Phase 4)
├── Chart.yaml                          UPDATE: add Redis dependency
├── values.yaml                         UPDATE: add dapr, redis, zipkin, secrets sections
├── values-local.example.yaml           NEW: template for local overrides
├── charts/                             AUTO: Helm dependency artifacts
└── templates/
    ├── backend-deployment.yaml         UPDATE: add Dapr sidecar annotations
    ├── deployment.yaml                 KEEP: frontend (no Dapr changes needed)
    ├── backend-service.yaml            KEEP: unchanged
    ├── service.yaml                    KEEP: frontend unchanged
    ├── serviceaccount.yaml             KEEP: unchanged
    ├── k8s-secret.yaml                 NEW: flowtodo-secrets K8s Secret
    ├── zipkin-deployment.yaml          NEW: Zipkin pod
    ├── zipkin-service.yaml             NEW: Zipkin ClusterIP service
    └── dapr/
        ├── pubsub.yaml                 NEW: Dapr Pub/Sub component (Redis)
        ├── statestore.yaml             NEW: Dapr State Store component (Redis)
        ├── secretstore.yaml            NEW: Dapr Secrets Store component (K8s)
        ├── cron-check-reminders.yaml   NEW: Cron binding → /cron/check-reminders
        ├── cron-recurrences.yaml       NEW: Cron binding → /cron/generate-recurrences
        └── tracing-config.yaml         NEW: Dapr Configuration (Zipkin endpoint)

backend/
├── requirements.txt                    UPDATE: ensure dapr>=1.14.0 present
└── src/
    ├── services/
    │   ├── event_publisher.py          KEEP: already correct (uses dapr SDK)
    │   └── secrets_loader.py           NEW: loads secrets from Dapr Secrets API
    └── main.py                         UPDATE: call secrets_loader in lifespan startup

scripts/
├── deploy.sh                           NEW: full one-command local deploy
└── teardown.sh                         NEW: full teardown
```

**Structure Decision**: Web application structure (frontend + backend). Helm chart extended (not replaced). Infrastructure artifacts in `todo-chatbot/templates/dapr/`. Scripts in `scripts/`.

---

## Complexity Tracking

No constitution violations requiring justification.

---

## Architecture Decisions

### AD-1: Redis as Helm Subchart Dependency

Embed Redis as a Bitnami Helm chart dependency within `todo-chatbot/Chart.yaml` rather than as a standalone deployment. This enables `helm upgrade --install flowtodo ./todo-chatbot` to deploy Redis, the app, and all Dapr components atomically.

```yaml
# Chart.yaml
dependencies:
  - name: redis
    version: "20.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
```

Redis configured in standalone mode, no persistence, no auth (local dev simplicity).

### AD-2: Dapr Sidecar Annotations on Backend Only

Only the backend deployment gets Dapr sidecar injection. The Next.js frontend cannot use the Dapr SDK natively (it runs in a Node.js server context, not as a Dapr-aware service). Service Invocation is demonstrated via backend self-invocation.

Backend pod annotations:
```yaml
dapr.io/enabled: "true"
dapr.io/app-id: "flowtodo-backend"
dapr.io/app-port: "8000"
dapr.io/config: "appconfig"
dapr.io/log-level: "info"
```

### AD-3: Secrets Loader with Graceful Fallback

`secrets_loader.py` attempts to contact Dapr Secrets API on startup. If unreachable (local dev, no Dapr), it falls back to `os.getenv()`. This preserves developer ergonomics for local-without-K8s development while enabling full secrets management when deployed to Minikube.

```python
# Pseudo-code
async def load_secrets():
    try:
        resp = await http_get(f"http://localhost:{DAPR_PORT}/v1.0/secrets/kubernetes/flowtodo-secrets")
        for key, val in resp.items():
            os.environ[key] = val["value"]
        logger.info("Secrets loaded from Dapr Secrets Store")
    except ConnectionRefusedError:
        logger.warning("Dapr unavailable — using environment variables")
```

### AD-4: Service Invocation Demo via Self-Invocation

A new endpoint `GET /api/dapr/self-invoke-test` on the backend calls itself through the Dapr sidecar at `http://localhost:3500/v1.0/invoke/flowtodo-backend/method/api/health`. This generates the required mTLS-secured service invocation and a 2-span Zipkin trace without requiring a second service.

### AD-5: values-local.yaml Pattern for Secrets

Real secret values are never committed to git. The Helm chart's `values.yaml` contains placeholder strings for secrets. A `values-local.yaml` (gitignored) holds real values and is passed to `helm upgrade` with `-f values-local.yaml`. A `values-local.example.yaml` (committed) provides the template.

---

## Component Interaction Map

```
┌─────────────────────────────────────────────────────────┐
│                   default namespace                       │
│                                                           │
│  ┌──────────────────────────────┐                        │
│  │     flowtodo-backend pod      │                        │
│  │  ┌──────────┐ ┌───────────┐  │                        │
│  │  │ FastAPI  │ │  daprd    │  │◄──── mTLS ────► daprd  │
│  │  │ :8000    │ │ :3500     │  │                        │
│  │  └────┬─────┘ └─────┬─────┘  │                        │
│  └───────│─────────────│────────┘                        │
│          │             │                                  │
│          │     ┌───────▼────────┐                        │
│          │     │ Redis :6379    │  ◄─ pubsub, statestore │
│          │     └────────────────┘                        │
│          │                                                │
│          │     ┌───────────────┐                         │
│          │     │ Zipkin :9411  │  ◄─ traces              │
│          │     └───────────────┘                         │
│          │                                                │
│          ▼ DB connections                                 │
│     Neon PostgreSQL (external)                           │
│                                                           │
│  ┌──────────────────────────────┐                        │
│  │   flowtodo-frontend pod       │                        │
│  │   Next.js :3000               │                        │
│  └──────────────────────────────┘                        │
└─────────────────────────────────────────────────────────┘
                  │
        ┌─────────▼──────────┐
        │   dapr-system ns   │
        │  operator/sentry/  │
        │  injector/placement│
        └────────────────────┘
```

---

## Implementation Phases

### Phase A: Helm Chart Extension

**Goal**: Extend `todo-chatbot/` with Redis, Zipkin, K8s Secret, and Dapr component templates.

1. Update `Chart.yaml` — add Bitnami Redis dependency (version `^20.0.0`)
2. Update `values.yaml` — add `redis`, `zipkin`, `dapr`, `secrets` sections
3. Create `values-local.example.yaml` — placeholder secrets template
4. Create `templates/k8s-secret.yaml` — renders `flowtodo-secrets` K8s Secret from values
5. Create `templates/zipkin-deployment.yaml` + `zipkin-service.yaml`
6. Create `templates/dapr/pubsub.yaml` — Redis pub/sub component
7. Create `templates/dapr/statestore.yaml` — Redis state store component
8. Create `templates/dapr/secretstore.yaml` — Kubernetes secrets store component
9. Create `templates/dapr/cron-check-reminders.yaml` — cron binding (60s)
10. Create `templates/dapr/cron-recurrences.yaml` — cron binding (300s)
11. Create `templates/dapr/tracing-config.yaml` — Dapr Configuration for Zipkin
12. Update `templates/backend-deployment.yaml` — add Dapr sidecar annotations

### Phase B: Backend Code Changes

**Goal**: Add secrets loading and service invocation demo endpoint.

13. Update `backend/requirements.txt` — ensure `dapr>=1.14.0` is present
14. Create `backend/src/services/secrets_loader.py` — Dapr Secrets API client with env fallback
15. Update `backend/src/main.py` — call `secrets_loader.load_secrets()` in lifespan startup
16. Create `backend/src/api/routes/dapr_invoke.py` — `GET /api/dapr/self-invoke-test` endpoint
17. Update `backend/src/main.py` — register `dapr_invoke` router

### Phase C: Deploy Scripts

**Goal**: Single-script deployment and teardown.

18. Create `scripts/deploy.sh` — full deployment script (Minikube → Dapr init → build images → Helm install → verify)
19. Create `scripts/teardown.sh` — full teardown (helm uninstall, optional dapr uninstall, minikube stop)

### Phase D: Verification

20. Run `bash scripts/deploy.sh` and verify all pods Running
21. Verify Pub/Sub: create task → check logs for published/received event
22. Verify Cron: wait 60s → check `/cron/check-reminders` was called
23. Verify Secrets: check logs for "Secrets loaded from Dapr"
24. Verify Service Invocation: call `/api/dapr/self-invoke-test` → check Zipkin
25. Document any issues in a `specs/009-dapr-minikube-deploy/verification.md`

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Minikube memory exhaustion during Dapr init | Medium | High | Set `--memory=8192` in deploy script; document minimum requirements |
| Redis pod crash invalidates pub/sub | Low | Medium | Redis restarts automatically; Dapr buffers and retries delivery |
| Dapr sidecar injection fails (namespace label missing) | Low | High | Deploy script labels the `default` namespace explicitly |
| Neon DB unreachable from Minikube (network block) | Medium | High | Fallback: add optional local PostgreSQL pod in `values.yaml`; documented in quickstart |
| Windows WSL2 Minikube driver compatibility | Medium | Medium | Use `--driver=docker`; documented in quickstart |

---

## Verification Checklist

- [ ] `kubectl get pods` shows all pods in `Running` state
- [ ] Backend pod has `2/2` containers (app + daprd sidecar)
- [ ] Frontend accessible via `minikube service flowtodo-frontend --url`
- [ ] `GET /dapr/subscribe` returns subscription manifest
- [ ] Creating a task logs "Published task.created event"
- [ ] `/task-events` subscriber logs "Received task event"
- [ ] Cron fires `/cron/check-reminders` every ~60 seconds
- [ ] Backend startup logs "Secrets loaded from Dapr Secrets Store"
- [ ] `GET /api/dapr/self-invoke-test` returns 200 with invocation result
- [ ] Zipkin shows 2-span trace for service invocation
- [ ] `bash scripts/teardown.sh && bash scripts/deploy.sh` produces identical working cluster
