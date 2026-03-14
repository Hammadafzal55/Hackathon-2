# Feature Specification: Local Deployment with Full Dapr on Minikube

**Feature Branch**: `009-dapr-minikube-deploy`
**Created**: 2026-03-10
**Status**: Draft
**Input**: User description: "Part B: Local Deployment — Deploy to Minikube. Deploy Dapr on Minikube use Full Dapr: Pub/Sub, State, Bindings (cron), Secrets, Service Invocation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy FlowTodo to Minikube with Dapr (Priority: P1)

A developer sets up the FlowTodo application locally on Minikube with the full Dapr runtime, enabling all Dapr building blocks (Pub/Sub, State, Bindings, Secrets, Service Invocation) to operate as they would in production.

**Why this priority**: This is the foundational deployment story. Without a working Minikube + Dapr cluster, none of the other Dapr features can be validated locally. It is the prerequisite for every other story.

**Independent Test**: A developer can run `minikube start`, apply all manifests, and verify all pods (frontend, backend, dapr sidecars, Redis, Zipkin) reach `Running` state. The app is accessible via `minikube service` or port-forward without any external DB or cloud dependency.

**Acceptance Scenarios**:

1. **Given** a machine with Minikube, kubectl, Helm, and Dapr CLI installed, **When** the developer runs the deploy script/commands, **Then** all pods are in `Running` state within 5 minutes and the app responds on the exposed URL.
2. **Given** the cluster is running, **When** the developer inspects pod annotations, **Then** each backend pod has `dapr.io/enabled: "true"` and shows a `daprd` sidecar container.
3. **Given** the app is deployed, **When** the developer navigates to the frontend URL, **Then** they can log in and view their tasks.

---

### User Story 2 - Task Events via Dapr Pub/Sub (Priority: P2)

When a task is created, updated, or deleted, the backend publishes an event via Dapr Pub/Sub to a Redis-backed message broker. A subscriber (notification service or the same backend) receives the event and processes it (e.g., persists a notification).

**Why this priority**: Pub/Sub is the primary asynchronous integration pattern for FlowTodo notifications and event-driven workflows. Validating it locally confirms the production event pipeline works end-to-end.

**Independent Test**: Create a task via the UI → check backend logs for "Published task.created event" → check subscriber logs for "Received task.created event" → verify a notification appears in the notifications panel.

**Acceptance Scenarios**:

1. **Given** a running cluster with Dapr Pub/Sub configured to Redis, **When** a task is created via the API, **Then** the backend publishes a `task.created` event and logs success.
2. **Given** a published event, **When** the Dapr runtime delivers it to the subscriber, **Then** the subscriber endpoint is called with the correct event payload.
3. **Given** a delivered event, **When** the notification service processes it, **Then** a notification record appears in the database and in the user's notification feed.

---

### User Story 3 - Reminder Cron via Dapr Bindings (Priority: P3)

Dapr's Cron Binding triggers a backend endpoint on a schedule (e.g., every minute) to check for due reminders and deliver them as notifications, replacing the inline check currently done on task creation.

**Why this priority**: Cron-driven reminders are time-sensitive and require reliable scheduling. Dapr Bindings provide a portable, infrastructure-independent way to run periodic jobs without managing cron infrastructure manually.

**Independent Test**: Create a task with a reminder set 2 minutes in the future → wait → observe the cron binding trigger the `/cron/check-reminders` endpoint → verify a notification is created for the reminder.

**Acceptance Scenarios**:

1. **Given** a Dapr Cron Binding component configured for a 60-second interval, **When** the interval elapses, **Then** Dapr calls `POST /cron/check-reminders` on the backend.
2. **Given** a task with a reminder whose `fire_at` is in the past, **When** the cron endpoint is called, **Then** the reminder is marked `sent` and a notification is created.
3. **Given** no due reminders, **When** the cron endpoint is called, **Then** it responds with 200 and no notifications are created.

---

### User Story 4 - Secrets via Dapr Secrets Store (Priority: P4)

The backend retrieves the database connection string and JWT secret from a Dapr Secrets Store (backed by a Kubernetes Secret) rather than reading environment variables directly, enabling centralized secret management.

**Why this priority**: Secrets management is a production-readiness concern. Using Dapr Secrets Store decouples the app from environment variable injection and provides a consistent secret access pattern across all environments.

**Independent Test**: Remove DATABASE_URL from the pod env vars → redeploy → verify the backend starts successfully and connects to the database by fetching secrets from the Dapr Secrets Store.

**Acceptance Scenarios**:

1. **Given** a Kubernetes Secret holding `DATABASE_URL` and `BETTER_AUTH_SECRET`, **When** the backend pod starts, **Then** it retrieves these values via the Dapr Secrets API and connects successfully.
2. **Given** a misconfigured secret name, **When** the backend starts, **Then** it logs a clear error indicating which secret could not be retrieved.

---

### User Story 5 - Service Invocation between Frontend and Backend (Priority: P5)

Internal service-to-service calls (e.g., a notification aggregator calling the task service) use Dapr Service Invocation with mTLS, rather than direct HTTP calls, providing built-in retries, tracing, and mutual authentication.

**Why this priority**: Service Invocation adds resilience and observability to inter-service communication. It is lower priority than Pub/Sub and Cron since FlowTodo currently has a simple 2-service architecture, but is required for full Dapr coverage.

**Independent Test**: Trigger a cross-service call (e.g., notification service invoking task service to enrich a notification) → verify the call is visible in the Zipkin/distributed tracing UI with both service spans.

**Acceptance Scenarios**:

1. **Given** two Dapr-enabled services deployed in the cluster, **When** one service invokes the other via the Dapr service invocation API, **Then** the call succeeds with mTLS and appears in distributed traces.
2. **Given** the target service is temporarily unavailable, **When** a service invocation is attempted, **Then** Dapr retries the call and reports failure after the configured retry limit.

---

### Edge Cases

- What happens when Minikube runs out of memory during Dapr initialization?
- How does the system behave if Redis (Dapr state/pubsub backend) pod crashes mid-operation?
- What if the Dapr sidecar injector fails to inject (missing namespace label)?
- How does the cron binding behave if the backend pod is restarting (missed ticks)?
- What happens if a Kubernetes Secret is missing a required key at pod startup?
- How are duplicate Pub/Sub messages handled if the subscriber crashes mid-processing?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST deploy all FlowTodo components (frontend, backend) to a local Minikube cluster using Kubernetes manifests or Helm charts.
- **FR-002**: System MUST initialize the Dapr runtime on Minikube using the Dapr CLI (`dapr init --kubernetes`), with Dapr control plane pods running in the `dapr-system` namespace.
- **FR-003**: System MUST configure Dapr Pub/Sub component backed by Redis for task event publishing and subscription.
- **FR-004**: System MUST configure Dapr Cron Binding to trigger the backend reminder check endpoint on a defined interval (≤ 60 seconds).
- **FR-005**: System MUST configure a Dapr Secrets Store component backed by Kubernetes Secrets for DATABASE_URL and authentication secrets.
- **FR-006**: System MUST enable Dapr Service Invocation between backend services with mTLS enforced by the Dapr runtime.
- **FR-007**: System MUST annotate backend Kubernetes pods with Dapr sidecar injection annotations so the Dapr runtime injects `daprd` automatically.
- **FR-008**: System MUST include a Redis deployment (or Helm chart) in the cluster to serve as the Pub/Sub broker and State Store backend.
- **FR-009**: All Dapr component manifests (pubsub.yaml, statestore.yaml, secretstore.yaml, cron-binding.yaml) MUST be applied to the correct Kubernetes namespace.
- **FR-010**: System MUST provide a single command or script to bring up the full local environment from scratch (Minikube start → Dapr init → apply manifests → verify).
- **FR-011**: The deployment MUST NOT require any cloud account, external SaaS, or network connectivity beyond pulling container images.
- **FR-012**: System MUST expose the frontend and backend services locally via Minikube service tunnels or NodePort/LoadBalancer so a browser can access the app.
- **FR-013**: Distributed traces from Dapr service invocations MUST be visible in a local Zipkin or compatible tracing UI.

### Key Entities

- **Minikube Cluster**: Local single-node Kubernetes cluster running all application pods and Dapr control plane.
- **Dapr Control Plane**: Set of Dapr system pods (dapr-operator, dapr-placement, dapr-sidecar-injector, dapr-sentry) running in `dapr-system` namespace.
- **Dapr Component**: A YAML manifest declaring a Dapr building block (pubsub, statestore, binding, secretstore) and its configuration.
- **Redis**: In-cluster message broker and state store backing Dapr Pub/Sub and State building blocks.
- **Dapr Sidecar (daprd)**: Injected container in each backend pod that intercepts and handles Dapr API calls.
- **Kubernetes Secret**: Native K8s resource storing sensitive values (DB URL, auth secrets) accessed via Dapr Secrets Store.
- **Cron Binding**: Dapr binding component that triggers a backend HTTP endpoint on a configurable schedule.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All application pods (frontend, backend, Redis, Dapr control plane) reach `Running` state within 5 minutes of running the setup script on a standard developer machine.
- **SC-002**: 100% of Dapr building blocks (Pub/Sub, State, Bindings, Secrets, Service Invocation) are functional and verifiable via manual end-to-end tests.
- **SC-003**: A task created via the UI triggers a Pub/Sub event that results in a notification appearing in the notification panel within 10 seconds.
- **SC-004**: The cron binding fires the reminder check endpoint within 5 seconds of its scheduled interval.
- **SC-005**: Backend starts successfully and retrieves all secrets from the Dapr Secrets Store without any environment variable overrides.
- **SC-006**: A developer with Minikube and Dapr CLI installed can bring up the full environment using a single script or at most 5 commands.
- **SC-007**: Distributed traces for inter-service calls are visible in the local tracing UI with correct parent-child span relationships.
- **SC-008**: The deployment is fully reproducible — running the teardown and setup scripts produces an identical working environment.

## Assumptions

- Developer machine has at least 8 GB RAM allocated to Minikube and 4 CPUs.
- Minikube, kubectl, Helm, and Dapr CLI are pre-installed (their installation is out of scope for this spec).
- Container images for frontend and backend are built locally (`eval $(minikube docker-env)`) or pushed to a local registry.
- The Neon PostgreSQL database remains the data store; the local cluster connects to the external Neon DB (not a local Postgres pod). If connectivity is unavailable, a local PostgreSQL pod is an acceptable fallback.
- Redis is deployed in-cluster via Helm (Bitnami Redis chart) and not shared with any external system.
- Dapr version is compatible with the current Kubernetes version supported by Minikube.
- The existing `todo-chatbot/` Helm chart structure from Phase 4 will be extended rather than replaced.

## Out of Scope

- Production cloud deployment (AWS EKS, GCP GKE, Azure AKS) — this is a local-only deployment.
- CI/CD pipeline integration or GitOps automation.
- High availability, multi-replica deployments, or horizontal pod autoscaling.
- Dapr Actor model (not used in FlowTodo).
- External secret management solutions (HashiCorp Vault, AWS Secrets Manager) — Kubernetes Secrets are sufficient for local dev.
- Installation guides for Minikube, kubectl, Helm, or Dapr CLI.
