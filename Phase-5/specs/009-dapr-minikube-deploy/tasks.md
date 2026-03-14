# Tasks: Local Deployment with Full Dapr on Minikube

**Input**: Design documents from `specs/009-dapr-minikube-deploy/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: No automated test tasks — this is an infrastructure/deployment feature. Verification is manual (kubectl logs, Zipkin UI, curl).

**Organization**: Tasks grouped by user story. Each story phase is independently deployable and verifiable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label [US1]–[US5] from spec.md
- Exact file paths included in all descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare Helm chart structure, directory layout, and base configuration files before any Dapr-specific work.

- [X] T001 Add Redis Bitnami dependency to `todo-chatbot/Chart.yaml` (version `^20.0.0`, condition `redis.enabled`)
- [X] T002 Add `redis`, `zipkin`, `dapr`, and `secrets` sections to `todo-chatbot/values.yaml`
- [X] T003 [P] Create `todo-chatbot/values-local.example.yaml` with placeholder secrets (DATABASE_URL, BETTER_AUTH_SECRET, JWT_SECRET_KEY, AI_API_KEY)
- [X] T004 [P] Create `scripts/` directory and add `scripts/.gitkeep`; add `todo-chatbot/values-local.yaml` to `.gitignore`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core shared infrastructure that ALL user stories depend on — Zipkin, K8s Secret template, namespace configuration. Must complete before any user story.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Create `todo-chatbot/templates/k8s-secret.yaml` templating a `flowtodo-secrets` K8s Secret from `values.yaml` secrets section (keys: DATABASE_URL, BETTER_AUTH_SECRET, JWT_SECRET_KEY, AI_API_KEY, redis-password)
- [X] T006 [P] Create `todo-chatbot/templates/zipkin-deployment.yaml` (image: `openzipkin/zipkin:latest`, port 9411, namespace default)
- [X] T007 [P] Create `todo-chatbot/templates/zipkin-service.yaml` (ClusterIP, port 9411, selector: app=zipkin)
- [X] T008 [P] Create `todo-chatbot/templates/dapr/tracing-config.yaml` (Dapr Configuration kind, name: `appconfig`, samplingRate: "1", zipkin endpoint: `http://zipkin.default.svc.cluster.local:9411/api/v2/spans`)
- [ ] T009 Run `helm dependency update todo-chatbot/` to download Redis chart into `todo-chatbot/charts/`

**Checkpoint**: Helm chart has Redis dependency, Zipkin, K8s Secret template, and Dapr tracing config. `helm template` should render without errors.

---

## Phase 3: User Story 1 — Deploy FlowTodo to Minikube with Dapr (Priority: P1) 🎯 MVP

**Goal**: Get the full FlowTodo stack (frontend, backend, Redis, Zipkin, Dapr control plane) running on Minikube with Dapr sidecars injected.

**Independent Test**: `kubectl get pods` shows all pods `Running`; backend pod shows `2/2` containers (app + daprd); frontend accessible via `minikube service flowtodo-frontend --url`.

### Implementation

- [X] T010 [US1] Update `todo-chatbot/templates/backend-deployment.yaml` — add pod annotations: `dapr.io/enabled: "true"`, `dapr.io/app-id: "flowtodo-backend"`, `dapr.io/app-port: "8000"`, `dapr.io/config: "appconfig"`, `dapr.io/log-level: "info"`
- [X] T011 [P] [US1] Create `scripts/deploy.sh` — full idempotent deploy script: `minikube start --cpus=4 --memory=8192`, `dapr init --kubernetes --wait` (skip if already done), `eval $(minikube docker-env)`, build frontend + backend Docker images, `helm dependency update`, `helm upgrade --install flowtodo ./todo-chatbot -f values-local.yaml --wait --timeout 5m`, print service URLs
- [X] T012 [P] [US1] Create `scripts/teardown.sh` — `helm uninstall flowtodo`, optional `dapr uninstall --kubernetes`, `minikube stop`
- [ ] T013 [US1] Run `bash scripts/deploy.sh` (with real secrets in `values-local.yaml`) and verify all pods reach `Running` state
- [ ] T014 [US1] Verify Dapr control plane: `kubectl get pods -n dapr-system` shows dapr-operator, dapr-sidecar-injector, dapr-sentry, dapr-placement-server all `Running`
- [ ] T015 [US1] Verify backend pod has `2/2` containers: `kubectl get pod -l app=flowtodo-backend` shows `2/2 Running`
- [ ] T016 [US1] Verify frontend accessible: `minikube service flowtodo-frontend --url` opens the app in browser; user can log in and view tasks

**Checkpoint**: Full stack deployed. Frontend accessible. Dapr sidecars injected. All pods Running. User Story 1 complete — MVP delivered.

---

## Phase 4: User Story 2 — Task Events via Dapr Pub/Sub (Priority: P2)

**Goal**: Backend publishes `task.created`/`updated`/`deleted` events to Redis via Dapr Pub/Sub. Subscriber receives events and processes notifications.

**Independent Test**: Create a task → `kubectl logs -l app=flowtodo-backend -c flowtodo-backend | grep "Published"` shows `"Published task.created event"` → notification appears in UI within 10 seconds.

### Implementation

- [X] T017 [P] [US2] Create `todo-chatbot/templates/dapr/pubsub.yaml` — Dapr Component kind, name: `pubsub`, type: `pubsub.redis`, spec.metadata: `redisHost: redis-master.default.svc.cluster.local:6379`, `redisPassword` as secretKeyRef from `flowtodo-secrets`, `consumerID: flowtodo-backend`, `enableTLS: false`
- [X] T018 [P] [US2] Create `todo-chatbot/templates/dapr/statestore.yaml` — Dapr Component kind, name: `statestore`, type: `state.redis`, same redisHost/password, `actorStateStore: false`
- [X] T019 [US2] Verify `backend/requirements.txt` contains `dapr>=1.14.0` (add if missing)
- [ ] T020 [US2] Run `helm upgrade --install flowtodo ./todo-chatbot -f values-local.yaml --wait` to redeploy with new Dapr components
- [ ] T021 [US2] Verify Dapr loaded pubsub component: `kubectl logs -l app=flowtodo-backend -c daprd | grep -i "pubsub\|component"` shows component registered
- [ ] T022 [US2] End-to-end Pub/Sub test: create a task via UI or `curl POST /api/tasks` → check `kubectl logs -l app=flowtodo-backend -c flowtodo-backend | grep "Published task.created"` — confirm event logged
- [ ] T023 [US2] Verify subscriber received event: `kubectl logs -l app=flowtodo-backend -c flowtodo-backend | grep "task-events\|Received task"` — confirm `POST /task-events` was called
- [ ] T024 [US2] Verify notification created in DB: check notifications panel in UI shows new notification for the created task

**Checkpoint**: Pub/Sub pipeline fully functional. Task mutations publish events. Subscriber processes them. Notifications appear in UI.

---

## Phase 5: User Story 3 — Reminder Cron via Dapr Bindings (Priority: P3)

**Goal**: Dapr Cron Bindings fire `POST /cron/check-reminders` every 60s and `POST /cron/generate-recurrences` every 300s on the backend.

**Independent Test**: `kubectl logs -l app=flowtodo-backend -c flowtodo-backend -f | grep "cron"` shows `/cron/check-reminders` being called every ~60 seconds.

### Implementation

- [X] T025 [P] [US3] Create `todo-chatbot/templates/dapr/cron-check-reminders.yaml` — Dapr Component kind, name: `check-reminders-cron`, type: `bindings.cron`, spec.metadata: `schedule: @every 60s`; include `route: /cron/check-reminders` if supported or rely on naming convention
- [X] T026 [P] [US3] Create `todo-chatbot/templates/dapr/cron-recurrences.yaml` — Dapr Component kind, name: `generate-recurrences-cron`, type: `bindings.cron`, spec.metadata: `schedule: @every 300s`
- [ ] T027 [US3] Run `helm upgrade --install flowtodo ./todo-chatbot -f values-local.yaml --wait` to deploy cron bindings
- [ ] T028 [US3] Verify cron binding registered: `kubectl logs -l app=flowtodo-backend -c daprd | grep -i "cron\|binding"` shows both bindings loaded
- [ ] T029 [US3] Verify reminder cron fires: `kubectl logs -l app=flowtodo-backend -c flowtodo-backend -f | grep "check-reminders"` — confirm `POST /cron/check-reminders` logged every ~60s
- [ ] T030 [US3] End-to-end reminder test: create task with reminder set 2 minutes in future via UI → wait for cron tick → verify notification created in DB and visible in UI

**Checkpoint**: Both cron bindings fire on schedule. Reminders are delivered without inline task-creation trigger. Recurrence generation runs every 5 minutes.

---

## Phase 6: User Story 4 — Secrets via Dapr Secrets Store (Priority: P4)

**Goal**: Backend loads DATABASE_URL, BETTER_AUTH_SECRET, JWT_SECRET_KEY, AI_API_KEY from Dapr Kubernetes Secrets Store at startup, instead of pod environment variables.

**Independent Test**: Backend startup logs show `"Secrets loaded from Dapr Secrets Store"`. Backend connects to database and processes requests normally without DATABASE_URL set as a pod env var.

### Implementation

- [X] T031 [US4] Create `todo-chatbot/templates/dapr/secretstore.yaml` — Dapr Component kind, name: `kubernetes`, type: `secretstores.kubernetes`, no spec.metadata required
- [X] T032 [US4] Create `backend/src/services/secrets_loader.py` — async `load_secrets()` function: GET `http://localhost:{DAPR_HTTP_PORT}/v1.0/secrets/kubernetes/flowtodo-secrets`, extract each key from response JSON `{key: {"value": "..."}}`, set `os.environ[key] = value`; on `ConnectionRefusedError` or `httpx.ConnectError`, log warning "Dapr unavailable — using environment variables" and return without error
- [X] T033 [US4] Update `backend/src/main.py` lifespan startup block — call `await secrets_loader.load_secrets()` before `await initialize_database()` (so DB URL is populated before DB init)
- [X] T034 [US4] Ensure `httpx` or `aiohttp` is in `backend/requirements.txt` (for the HTTP call to Dapr Secrets API)
- [ ] T035 [US4] Run `helm upgrade --install flowtodo ./todo-chatbot -f values-local.yaml --wait` with secretstore component added
- [ ] T036 [US4] Verify secrets loaded: `kubectl logs -l app=flowtodo-backend -c flowtodo-backend | grep -i "secret"` shows `"Secrets loaded from Dapr Secrets Store"`
- [ ] T037 [US4] Test fallback: run backend locally without Dapr (`python -m uvicorn ...`) — verify it starts and logs `"Dapr unavailable — using environment variables"` without crashing

**Checkpoint**: Backend reads secrets from Dapr Secrets Store in cluster. Falls back to env vars gracefully outside cluster. No secrets hardcoded in Helm values.

---

## Phase 7: User Story 5 — Service Invocation with mTLS + Zipkin (Priority: P5)

**Goal**: Demonstrate Dapr Service Invocation with mTLS by calling `GET /api/dapr/self-invoke-test`, which triggers a Dapr-proxied HTTP call to the backend itself. Zipkin shows the 2-span distributed trace.

**Independent Test**: `GET /api/dapr/self-invoke-test` returns 200 → `kubectl port-forward svc/zipkin 9411:9411` → Zipkin UI shows a trace with 2 spans (client + server) for `flowtodo-backend`.

### Implementation

- [X] T038 [P] [US5] Create `backend/src/api/routes/dapr_invoke.py` — `GET /api/dapr/self-invoke-test` endpoint: uses `httpx.AsyncClient` to call `http://localhost:3500/v1.0/invoke/flowtodo-backend/method/api/health` (Dapr sidecar); returns 200 JSON `{"status": "ok", "invocation_result": <health_response>, "dapr_app_id": "flowtodo-backend"}`; requires JWT auth via `get_current_user_id` dependency
- [X] T039 [US5] Register `dapr_invoke.router` in `backend/src/main.py` with prefix `/api`
- [ ] T040 [US5] Rebuild backend Docker image inside Minikube daemon: `eval $(minikube docker-env) && docker build -t hackathon-backend:latest ./backend`
- [ ] T041 [US5] Restart backend pod to pick up new image: `kubectl rollout restart deployment flowtodo-backend`
- [ ] T042 [US5] Start Zipkin port-forward: `kubectl port-forward svc/zipkin 9411:9411 &`
- [ ] T043 [US5] Call test endpoint: `curl -H "Authorization: Bearer <token>" http://<backend-url>/api/dapr/self-invoke-test` — verify 200 response with `invocation_result`
- [ ] T044 [US5] Open Zipkin at `http://localhost:9411` → search service `flowtodo-backend` → verify trace shows 2 spans (outbound invoke + inbound handler) with correct parent-child relationship
- [ ] T045 [US5] Verify mTLS active: `kubectl logs -l app=flowtodo-backend -c daprd | grep -i "mtls\|cert\|tls"` — confirm Dapr sentry issued certificate

**Checkpoint**: Service Invocation with mTLS works. Distributed traces visible in Zipkin. All 5 Dapr building blocks (Pub/Sub, State, Bindings, Secrets, Service Invocation) are functional.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Reproducibility verification, chart versioning, documentation, and security cleanup.

- [X] T046 [P] Add `todo-chatbot/values-local.yaml` to `.gitignore` (confirm not tracked); verify `values.yaml` committed to git contains only placeholder values for secrets
- [X] T047 [P] Update `todo-chatbot/Chart.yaml` version from `0.1.0` to `0.2.0` (chart changed significantly)
- [ ] T048 Full reproducibility test: run `bash scripts/teardown.sh` → run `bash scripts/deploy.sh` → verify all pods reach `Running` state again and all 5 Dapr building blocks still work
- [ ] T049 Create `specs/009-dapr-minikube-deploy/verification.md` documenting test results: pod status output, log excerpts confirming each building block, Zipkin screenshot description, any known issues

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 — first story, must complete before verifying any other building blocks
- **US2 (Phase 4)**: Depends on US1 (cluster must be running); independently testable after US1
- **US3 (Phase 5)**: Depends on US1 (cluster must be running); independent of US2
- **US4 (Phase 6)**: Depends on US1 (cluster must be running); independent of US2/US3
- **US5 (Phase 7)**: Depends on US1 (cluster running + Zipkin deployed in Phase 2)
- **Polish (Phase 8)**: Depends on all desired user stories complete

### User Story Dependencies

- **US1 (P1)**: After Foundational — no other story dependencies (foundational cluster)
- **US2 (P2)**: After US1 — Dapr sidecar must be running for Pub/Sub to work
- **US3 (P3)**: After US1 — Dapr sidecar must be running for Cron Bindings
- **US4 (P4)**: After US1 — Dapr sidecar must be running for Secrets Store API
- **US5 (P5)**: After US1 + Zipkin (T006/T007 in Foundational) — needs Zipkin for tracing

### Within Each User Story

- Helm template creation tasks (`[P]`) can run in parallel
- Helm deploy task must follow template creation
- Verification tasks must follow Helm deploy
- Fallback/edge case tests after primary verification

### Parallel Opportunities

- T003 + T004: Both Setup tasks
- T006 + T007 + T008: Zipkin deployment + service + Dapr tracing config (all different files)
- T011 + T012: deploy.sh + teardown.sh (independent scripts)
- T017 + T018: pubsub.yaml + statestore.yaml (independent component files)
- T025 + T026: Two cron binding YAMLs (independent)
- T038 + T039: dapr_invoke.py creation (parallel with router registration prep)
- T046 + T047: Polish tasks on different files

---

## Parallel Execution Example: User Story 2 (Pub/Sub)

```bash
# Run these in parallel (different Helm template files):
Task: "Create todo-chatbot/templates/dapr/pubsub.yaml"    # T017
Task: "Create todo-chatbot/templates/dapr/statestore.yaml" # T018
Task: "Verify backend/requirements.txt has dapr>=1.14.0"  # T019

# Then sequentially:
Task: "helm upgrade --install flowtodo (redeploy)"  # T020 — waits for T017+T018
Task: "Verify Dapr loaded pubsub component"          # T021 — waits for T020
Task: "End-to-end create task → check logs"          # T022 — waits for T021
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T004)
2. Complete Phase 2: Foundational (T005–T009)
3. Complete Phase 3: US1 — Deploy to Minikube (T010–T016)
4. **STOP and VALIDATE**: All pods Running, frontend accessible, Dapr sidecars injected
5. **MVP delivered** — basic Dapr-enabled deployment working

### Incremental Delivery

1. Setup + Foundational → Helm chart ready
2. US1 complete → Full stack on Minikube with Dapr ✅
3. US2 complete → Pub/Sub pipeline live ✅
4. US3 complete → Cron-driven reminders ✅
5. US4 complete → Secrets from Dapr Secrets Store ✅
6. US5 complete → Service Invocation + mTLS + Zipkin traces ✅
7. Polish → Reproducibility confirmed, chart versioned

---

## Notes

- `[P]` tasks = different files, no blocking dependencies
- Each user story phase ends with manual verification — no automated tests needed for infrastructure
- `scripts/deploy.sh` is idempotent — safe to re-run after partial failures
- Dapr sidecar annotation on backend pod is the single most important change (T010)
- Redis auth is disabled for local dev (`redis.auth.enabled: false`) — simplifies redisPassword secret references
- `values-local.yaml` must NEVER be committed to git (contains real secrets)
- Total tasks: **49** (T001–T049)
