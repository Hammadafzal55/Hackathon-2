# Research: Dapr Minikube Local Deployment

**Feature**: 009-dapr-minikube-deploy
**Date**: 2026-03-11
**Status**: Complete — all unknowns resolved

---

## Decision 1: Dapr Version

**Decision**: Dapr 1.14.x (latest stable)
**Rationale**: Dapr 1.14 is the current stable release with full Kubernetes support, stable Pub/Sub, Bindings, Secrets, and Service Invocation building blocks. Helm chart `dapr/dapr` version `1.14.0`.
**Alternatives considered**: Dapr 1.13 (older LTS, no new features needed); Dapr 1.15-rc (not stable enough for dev use).

---

## Decision 2: Redis Deployment Strategy

**Decision**: Bitnami Redis Helm chart (`bitnami/redis`) in standalone mode as a Helm dependency inside `todo-chatbot/Chart.yaml`.
**Rationale**: Simplest way to co-deploy Redis with the application in one `helm install` command. Standalone mode sufficient for local development. No external cluster dependency.
**Alternatives considered**:
- Manual Redis Deployment YAML — works but adds maintenance burden.
- Redis Sentinel / Cluster — HA overkill for local dev.
- RabbitMQ as Pub/Sub broker — adds complexity; Redis is already available and Dapr supports it natively.

---

## Decision 3: Kubernetes Namespace

**Decision**: All FlowTodo pods deploy into the `default` namespace. Dapr control plane deploys into `dapr-system` namespace (Dapr CLI default).
**Rationale**: Simplest configuration; Dapr sidecar injection works in `default` namespace with label `dapr-injection=enabled`. Separating namespaces (e.g., `flowtodo`) adds complexity without benefit for local dev.
**Alternatives considered**: Custom `flowtodo` namespace — would require additional RBAC, namespace labels, and component namespace targeting.

---

## Decision 4: Dapr Secrets Store Backend

**Decision**: Kubernetes Secret Store (`type: secretstores.kubernetes`) backed by a Kubernetes Secret named `flowtodo-secrets`.
**Rationale**: Zero additional infrastructure — K8s Secrets are native. Backend reads `DATABASE_URL`, `BETTER_AUTH_SECRET`, `JWT_SECRET_KEY`, `AI_API_KEY` from the Dapr Secrets API at startup via a new `secrets_loader.py` module.
**Alternatives considered**:
- HashiCorp Vault — production-grade but requires additional Vault pod.
- AWS Secrets Manager — cloud dependency, violates FR-011.
- Environment variables only — insecure, doesn't demonstrate Dapr Secrets Store.

---

## Decision 5: Pub/Sub Component Backend

**Decision**: Dapr Pub/Sub backed by Redis (same Redis instance as State Store). Component name: `pubsub`. Topic: `task-events`.
**Rationale**: The existing `event_publisher.py` already reads `PUBSUB_NAME=pubsub` from env. The existing `dapr_events.py` already exposes `GET /dapr/subscribe` and `POST /task-events`. No application code changes needed — only add the Dapr sidecar annotation and the Redis pubsub component YAML.
**Alternatives considered**: RabbitMQ, Kafka — unnecessary complexity for single-topic local dev.

---

## Decision 6: Cron Binding Name and Route

**Decision**: Cron binding component name `check-reminders-cron`. Schedule: `@every 60s`. Target endpoint: `POST /cron/check-reminders` (already implemented in `dapr_events.py`).
**Rationale**: The endpoint already exists. Dapr invokes the route matching the binding name, so the binding component name must be `check-reminders-cron` for Dapr to POST to `/cron/check-reminders`. A second binding `generate-recurrences-cron` covers the recurrence generation endpoint at `@every 300s`.
**Alternatives considered**: K8s CronJob — works without Dapr but loses the Dapr building block demonstration requirement.

---

## Decision 7: Service Invocation Demonstration

**Decision**: Demonstrate Service Invocation by having the backend call itself through the Dapr sidecar (loopback via app-id `flowtodo-backend`). This is triggered from a test health endpoint `GET /api/dapr/self-invoke-test`.
**Rationale**: FlowTodo is a 2-service architecture (frontend + backend). The frontend (Next.js) cannot easily use the Dapr sidecar for client-initiated service invocation without significant rearchitecting. The loopback self-invocation pattern is the minimal viable demonstration that proves mTLS and distributed tracing work.
**Alternatives considered**: Frontend → Backend via Dapr sidecar — requires frontend to talk to `localhost:3500` (Dapr sidecar) instead of the backend NodePort, which breaks the existing API URL pattern. Cross-pod invocation between two backend replicas — would require 2 replicas which consumes more Minikube resources.

---

## Decision 8: Distributed Tracing

**Decision**: Zipkin deployed as a single pod + ClusterIP service in the cluster. Dapr tracing configuration set to export to `http://zipkin.default.svc.cluster.local:9411/api/v2/spans`. Zipkin UI accessible via `kubectl port-forward`.
**Rationale**: Zipkin is the default Dapr tracing target and is officially documented. Minimal resource footprint (single container). No persistence needed for local dev.
**Alternatives considered**: Jaeger — heavier, more complex. Otel Collector — additional configuration layer. No tracing — fails FR-013.

---

## Decision 9: Image Build and Push Strategy

**Decision**: Build Docker images directly into Minikube's Docker daemon using `eval $(minikube docker-env)` before building. Use `imagePullPolicy: Never` (already set in `values.yaml`).
**Rationale**: Already configured in existing `values.yaml`. No registry needed. Images are built once per deploy cycle.
**Alternatives considered**: Local registry (`minikube addons enable registry`) — adds an extra push/pull step without benefit for single-node dev. Docker Hub — requires auth and internet.

---

## Decision 10: Deploy Script Design

**Decision**: Single `scripts/deploy.sh` bash script covering: Minikube start → Dapr init (if not already) → Helm dependency update → Docker image builds → Helm upgrade/install → apply Dapr components → verify pods.
**Rationale**: Meets FR-010 (single script or ≤5 commands), FR-011 (local-only). Script is idempotent — safe to re-run.
**Alternatives considered**: Makefile — preferred by some but requires `make` installed; bash script is universally available.

---

## Existing Code Reuse Summary

| Component | Status | Action Required |
|-----------|--------|-----------------|
| `event_publisher.py` | Ready | Add `dapr-python-sdk` to requirements |
| `dapr_events.py` (pubsub subscriber) | Ready | No changes needed |
| `dapr_events.py` (cron endpoints) | Ready | Ensure binding name matches component |
| `todo-chatbot/` Helm chart | Extend | Add Dapr annotations, Redis dependency, Zipkin |
| `values.yaml` | Extend | Add Dapr + Redis + Zipkin config sections |
| Backend Dockerfile | Verify | Ensure `dapr-python-sdk` installed |
| Secrets (hardcoded in values) | Migrate | Move to K8s Secret → Dapr Secrets Store |
