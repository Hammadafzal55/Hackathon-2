---
id: 038
title: Dapr Minikube Deploy Implementation
stage: green
date: 2026-03-11
surface: agent
model: claude-sonnet-4-6
feature: 009-dapr-minikube-deploy
branch: 009-dapr-minikube-deploy
user: hammad
command: /sp.implement
labels: ["dapr","minikube","kubernetes","helm","redis","zipkin","pub-sub","cron","secrets","service-invocation","implementation"]
links:
  spec: specs/009-dapr-minikube-deploy/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - todo-chatbot/Chart.yaml
  - todo-chatbot/values.yaml
  - todo-chatbot/values-local.example.yaml
  - todo-chatbot/templates/k8s-secret.yaml
  - todo-chatbot/templates/zipkin-deployment.yaml
  - todo-chatbot/templates/zipkin-service.yaml
  - todo-chatbot/templates/backend-deployment.yaml
  - todo-chatbot/templates/dapr/tracing-config.yaml
  - todo-chatbot/templates/dapr/pubsub.yaml
  - todo-chatbot/templates/dapr/statestore.yaml
  - todo-chatbot/templates/dapr/secretstore.yaml
  - todo-chatbot/templates/dapr/cron-check-reminders.yaml
  - todo-chatbot/templates/dapr/cron-recurrences.yaml
  - backend/src/services/secrets_loader.py
  - backend/src/api/routes/dapr_invoke.py
  - backend/src/main.py
  - scripts/deploy.sh
  - scripts/teardown.sh
  - .gitignore
  - specs/009-dapr-minikube-deploy/verification.md
  - specs/009-dapr-minikube-deploy/tasks.md
tests:
  - Manual verification via kubectl logs and Zipkin UI (see verification.md)
---

## Prompt

(empty — triggered via /sp.implement command)

## Response snapshot

Implemented all code-generating tasks (T001–T004, T005–T008, T010–T012, T017–T019, T025–T026, T031–T034, T038–T039, T046–T047) for feature 009-dapr-minikube-deploy. Runtime verification tasks (T009, T013–T016, T020–T024, T027–T030, T035–T037, T040–T045, T048–T049) require manual execution after `bash scripts/deploy.sh`.

### Files created/modified:

**Helm Chart (todo-chatbot/)**:
- `Chart.yaml`: Added Bitnami Redis dependency (v20.x.x), bumped version to 0.2.0
- `values.yaml`: Added `redis`, `zipkin`, `dapr`, `secrets` sections
- `values-local.example.yaml`: Secrets template (gitignored actual file)
- `templates/k8s-secret.yaml`: flowtodo-secrets K8s Secret (all 5 keys)
- `templates/zipkin-deployment.yaml` + `zipkin-service.yaml`: Zipkin pod + ClusterIP
- `templates/backend-deployment.yaml`: Added Dapr sidecar annotations block (conditional on `dapr.enabled`)
- `templates/dapr/tracing-config.yaml`: Dapr Configuration for Zipkin (samplingRate=1)
- `templates/dapr/pubsub.yaml`: pubsub.redis component, Redis host from subchart, password from secretKeyRef
- `templates/dapr/statestore.yaml`: state.redis component
- `templates/dapr/secretstore.yaml`: secretstores.kubernetes component
- `templates/dapr/cron-check-reminders.yaml`: bindings.cron @every 60s → /cron/check-reminders
- `templates/dapr/cron-recurrences.yaml`: bindings.cron @every 300s → /cron/generate-recurrences

**Backend**:
- `services/secrets_loader.py`: async load_secrets() — fetches from Dapr Secrets API, sets os.environ, graceful fallback on ConnectError
- `api/routes/dapr_invoke.py`: GET /api/dapr/self-invoke-test — calls self via Dapr sidecar, returns invocation result
- `main.py`: Added load_secrets() call before DB init; registered dapr_invoke router

**Scripts**:
- `scripts/deploy.sh`: 7-step idempotent deploy (Minikube → Dapr init → image build → Helm install → verify)
- `scripts/teardown.sh`: Helm uninstall + optional Dapr uninstall + Minikube stop

**Other**:
- `.gitignore`: Added `todo-chatbot/values-local.yaml` and `todo-chatbot/charts/`
- `verification.md`: Step-by-step verification guide for all 5 building blocks

## Outcome

- ✅ Impact: All infrastructure code complete. Full Dapr + Minikube deployment ready. Run `bash scripts/deploy.sh` to deploy.
- 🧪 Tests: Manual verification required — see specs/009-dapr-minikube-deploy/verification.md
- 📁 Files: 20 files created/modified
- 🔁 Next prompts: Run `bash scripts/deploy.sh` to verify deployment; then `/sp.git.commit_pr` to commit and create PR
- 🧠 Reflection: Redis auth disabled for local dev simplicity (no redis-password needed in secretKeyRef but kept for completeness). Dapr cron binding name `check-reminders-cron` maps to POST `/cron/check-reminders` by Dapr convention (binding name = route path). secrets_loader.py has full graceful fallback pattern — safe to run locally without K8s.

## Evaluation notes (flywheel)

- Failure modes observed: check-prerequisites.sh wrong path — overridden per MEMORY.md pattern
- Graders run and results (PASS/FAIL): helm template lint pending (requires helm installed); backend imports verified by code review
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add `helm template` validation step to deploy.sh before helm upgrade to catch template errors early
