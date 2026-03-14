---
id: 036
title: Dapr Minikube Deploy Implementation Plan
stage: plan
date: 2026-03-11
surface: agent
model: claude-sonnet-4-6
feature: 009-dapr-minikube-deploy
branch: 009-dapr-minikube-deploy
user: hammad
command: /sp.plan
labels: ["dapr","minikube","kubernetes","helm","redis","zipkin","pub-sub","cron","secrets","service-invocation","plan"]
links:
  spec: specs/009-dapr-minikube-deploy/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/009-dapr-minikube-deploy/plan.md
  - specs/009-dapr-minikube-deploy/research.md
  - specs/009-dapr-minikube-deploy/data-model.md
  - specs/009-dapr-minikube-deploy/quickstart.md
  - specs/009-dapr-minikube-deploy/contracts/pubsub-contract.md
  - specs/009-dapr-minikube-deploy/contracts/cron-binding-contract.md
  - specs/009-dapr-minikube-deploy/contracts/secrets-contract.md
  - specs/009-dapr-minikube-deploy/contracts/service-invocation-contract.md
tests:
  - null
---

## Prompt

create implementation plan based on the specification

## Response snapshot

Generated full implementation plan for feature 009-dapr-minikube-deploy with the following artifacts:

**research.md** (Phase 0): 10 architectural decisions resolved — Dapr 1.14, Redis as Bitnami Helm subchart, default namespace, K8s Secrets Store, Redis pub/sub, cron binding names, self-invocation demo for Service Invocation, Zipkin tracing, Minikube docker-env image strategy, single deploy.sh script.

**data-model.md** (Phase 1): Dapr component schemas for 6 components (pubsub, statestore, secretstore, 2x cron bindings, tracing config); K8s Secret schema; Helm chart dependency schema; Backend secrets_loader config object; full file layout tree.

**4 contracts** (Phase 1):
- pubsub-contract.md: publisher schema, event types, subscriber CloudEvent format, error handling
- cron-binding-contract.md: 2 bindings (60s reminders, 300s recurrences), timing guarantees
- secrets-contract.md: secrets inventory, loader behavior, fallback rule, K8s Secret manifest
- service-invocation-contract.md: service registry, self-invocation demo endpoint, mTLS config, Zipkin trace structure

**quickstart.md** (Phase 1): Full step-by-step guide covering prerequisites, one-script deploy, manual steps, access URLs, building block verification, teardown, troubleshooting.

**plan.md**: Technical context, Constitution Check (all PASS), 25-task implementation plan across 4 phases (A: Helm chart extension 12 tasks, B: Backend code 5 tasks, C: Deploy scripts 2 tasks, D: Verification 6 tasks), component interaction diagram, risk analysis, verification checklist.

## Outcome

- ✅ Impact: Complete implementation plan for Dapr + Minikube deployment. All 5 Dapr building blocks designed. Ready for /sp.tasks.
- 🧪 Tests: Infrastructure verification checklist with 11 items in plan.md.
- 📁 Files: 8 artifacts created under specs/009-dapr-minikube-deploy/
- 🔁 Next prompts: `/sp.tasks` to generate actionable tasks.md
- 🧠 Reflection: Key insight: existing backend code (event_publisher.py, dapr_events.py) is already Dapr-ready. Minimal backend changes needed — main work is Helm chart extension and deploy scripts. self-invocation pattern solves Service Invocation demo without adding a second service.

## Evaluation notes (flywheel)

- Failure modes observed: setup-plan.sh resolved wrong paths (parent dir) — overridden per MEMORY.md.
- Graders run and results (PASS/FAIL): Constitution Check — PASS (all gates)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Consider adding a local PostgreSQL fallback option in values.yaml for when Neon DB is unreachable
