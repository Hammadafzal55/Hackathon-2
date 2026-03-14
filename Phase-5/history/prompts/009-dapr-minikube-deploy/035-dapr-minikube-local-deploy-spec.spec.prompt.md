---
id: 035
title: Dapr Minikube Local Deploy Spec
stage: spec
date: 2026-03-10
surface: agent
model: claude-sonnet-4-6
feature: 009-dapr-minikube-deploy
branch: 009-dapr-minikube-deploy
user: hammad
command: /sp.specify
labels: ["dapr","minikube","kubernetes","deployment","pub-sub","cron","secrets","service-invocation"]
links:
  spec: specs/009-dapr-minikube-deploy/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/009-dapr-minikube-deploy/spec.md
  - specs/009-dapr-minikube-deploy/checklists/requirements.md
  - history/prompts/009-dapr-minikube-deploy/035-dapr-minikube-local-deploy-spec.spec.prompt.md
tests:
  - null
---

## Prompt

Part B: Local Deployment
Deploy to Minikube
Deploy Dapr on Minikube use Full Dapr: Pub/Sub, State, Bindings (cron), Secrets, Service Invocation

## Response snapshot

Created feature spec for 009-dapr-minikube-deploy covering local deployment of FlowTodo to Minikube with the full Dapr runtime. Spec includes 5 prioritized user stories:

- P1: Deploy FlowTodo to Minikube with Dapr (foundational)
- P2: Task Events via Dapr Pub/Sub (Redis-backed event pipeline)
- P3: Reminder Cron via Dapr Bindings (scheduled reminder delivery)
- P4: Secrets via Dapr Secrets Store (K8s Secret-backed secret retrieval)
- P5: Service Invocation between services (mTLS, retries, distributed tracing)

13 functional requirements (FR-001–FR-013) covering cluster setup, Dapr initialization, component configuration, single-script deploy, and tracing. 8 measurable success criteria including 5-minute startup, 10-second pub/sub roundtrip, and full reproducibility.

Checklist validated: all items pass. Spec ready for `/sp.plan`.

## Outcome

- ✅ Impact: Feature 009 spec written and validated. Branch 009-dapr-minikube-deploy created and active.
- 🧪 Tests: No automated tests — spec-stage artifact only.
- 📁 Files: specs/009-dapr-minikube-deploy/spec.md, specs/009-dapr-minikube-deploy/checklists/requirements.md
- 🔁 Next prompts: `/sp.plan` to generate architecture and implementation plan
- 🧠 Reflection: Full Dapr building block coverage specified: Pub/Sub (Redis), State Store (Redis), Cron Binding, Kubernetes Secrets Store, Service Invocation with mTLS + Zipkin tracing. Local-only deployment, Neon DB as external data store, Redis in-cluster.

## Evaluation notes (flywheel)

- Failure modes observed: Script resolved SPEC_FILE to wrong parent dir — overridden using Phase-5 correct path per MEMORY.md.
- Graders run and results (PASS/FAIL): Requirements checklist — PASS (all items)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Consider adding a data-model.md for Dapr component YAML schemas in the plan phase
