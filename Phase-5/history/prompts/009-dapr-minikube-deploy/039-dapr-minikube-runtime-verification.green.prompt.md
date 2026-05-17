---
id: 039
title: Dapr Minikube Runtime Verification
stage: green
date: 2026-03-29
surface: agent
model: claude-sonnet-4-6
feature: 009-dapr-minikube-deploy
branch: main
user: hammad
command: run the local minikube deployment and test it
labels: ["dapr","minikube","verification","runtime","helm","rbac"]
links:
  spec: specs/009-dapr-minikube-deploy/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - todo-chatbot/templates/redis.yaml
  - todo-chatbot/templates/dapr/secretstore.yaml
  - todo-chatbot/templates/rbac.yaml
  - todo-chatbot/Chart.yaml
  - todo-chatbot/values-local.yaml
  - backend/Dockerfile.update
  - specs/009-dapr-minikube-deploy/verification.md
tests:
  - US1: kubectl get pods — backend 2/2 Running (app + daprd sidecar)
  - US2: Dapr state store write/read via /v1.0/state/statestore
  - US3: Dapr pub/sub publish to task-events via /v1.0/publish/pubsub/task-events
  - Cron: check-reminders-cron + generate-recurrences-cron registered in Dapr metadata
  - US4: Dapr secrets /v1.0/secrets/kubernetes/flowtodo-secrets → 5 keys
  - US5: Service invocation /v1.0/invoke/flowtodo-backend/method/health → 200
---

## Prompt

run the local minikube deployment and test it

## Response snapshot

Started Minikube (docker driver, 3072 MB, K8s v1.35.1), installed Dapr v1.17.3 on cluster, resolved 5 blocking issues, deployed FlowTodo Helm release, and verified all 5 Dapr building blocks.

**Issues resolved:**
1. Bitnami Redis OCI chart blocked (Docker Hub unreachable from WSL/Minikube) → replaced subchart with inline redis:7-alpine template
2. daprd fatal error: "component kubernetes already exists" → disabled duplicate secretstore template (Dapr K8s auto-registers one)
3. Service account RBAC missing → added rbac.yaml Role + RoleBinding for secret read
4. redis:7-alpine + openzipkin/zipkin ImagePullBackOff → loaded via minikube image load from host Docker
5. NodePorts 30300/30800 blocked by old Phase-4 release → helm uninstall todo

**All 5 Dapr building blocks PASS:**
- State Store: write+read `"dapr-works"` via Redis
- Pub/Sub: published to `task-events` HTTP 204
- Cron Bindings: `check-reminders-cron` and `generate-recurrences-cron` registered
- Secrets Store: all 5 keys from `flowtodo-secrets` K8s secret
- Service Invocation: `invoke/flowtodo-backend/method/health` → 200

## Outcome

- ✅ Impact: All spec-009 runtime verification tasks (T009, T013-T049) complete; verification.md updated with PASS results
- 🧪 Tests: 6 live tests run against running cluster — all PASS
- 📁 Files: 7 files created/modified (redis.yaml, rbac.yaml, secretstore.yaml patch, Chart.yaml, values-local.yaml, Dockerfile.update, verification.md)
- 🔁 Next prompts: Phase V Part C cloud deployment (AKS/GKE/DOKS)
- 🧠 Reflection: WSL2 Docker Hub connectivity is unreliable inside Minikube's docker daemon; always test image pulls separately and use `minikube image load` as fallback

## Evaluation notes (flywheel)

- Failure modes observed: OCI registry timeout in Minikube; duplicate Dapr built-in component; missing RBAC for K8s secret store; stale NodePort allocation from prior release
- Graders run and results (PASS/FAIL): All 6 building-block tests PASS
- Prompt variant (if applicable): null
- Next experiment: Test cron binding invocations in backend logs after 60s wait; add Zipkin trace verification
