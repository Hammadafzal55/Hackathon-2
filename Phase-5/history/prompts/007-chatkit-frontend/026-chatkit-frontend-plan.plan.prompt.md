---
id: 026
title: ChatKit Frontend Implementation Plan
stage: plan
date: 2026-02-11
surface: agent
model: claude-opus-4-6
feature: 007-chatkit-frontend
branch: 007-chatkit-frontend
user: hammad
command: sp.plan
labels: ["chatkit", "frontend", "plan", "openai", "tool-calls"]
links:
  spec: specs/007-chatkit-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - Phase-3/specs/007-chatkit-frontend/plan.md
  - Phase-3/specs/007-chatkit-frontend/research.md
  - Phase-3/specs/007-chatkit-frontend/data-model.md
  - Phase-3/specs/007-chatkit-frontend/quickstart.md
  - Phase-3/specs/007-chatkit-frontend/contracts/frontend-api-integration.yaml
tests:
  - Constitution check: 6/6 gates PASS
---

## Prompt

/sp.plan Phase III – Spec 7: ChatKit Frontend Integration & Agent UI

Implementation Strategy:
Enhance existing frontend without creating new backend services.

STEP 1 – ChatKit Setup
- Install OpenAI ChatKit
- Create Chat component
- Configure initial system message
- Connect UI to authenticated user context

STEP 2 – API Integration
- Connect ChatKit message send handler to POST /api/chat
- Send: { conversation_id, message }
- Receive: { conversation_id, response, tool_calls }
- Store conversation_id in frontend state

STEP 3 – Conversation Persistence
- On component mount: Load existing conversation if available
- Render previous messages
- Ensure refresh does not reset conversation

STEP 4 – Tool Call UX Enhancements
- Display tool call confirmations in friendly format
- Handle: Task created, updated, completed, deleted
- Graceful UI error handling

(followed by user clarification)

use the original nextjs frontend after that this will be followed:
OpenAI ChatKit Setup & Deployment with Domain Allowlist Configuration (Required for Hosted ChatKit). Deploy frontend first, add domain to OpenAI allowlist, get domain key, set NEXT_PUBLIC_OPENAI_DOMAIN_KEY env var.

## Response snapshot

### Phase 0: Research
- Evaluated OpenAI ChatKit: managed chat widget requiring OpenAI API (hosted mode with domain key)
- ChatKit handles conversation UI, threads, and tool execution via `onClientTool` callback
- Tool calls from OpenAI assistant mapped to existing backend task CRUD endpoints
- Architecture: User → ChatKit → OpenAI (hosted) → Tool Call → onClientTool → ApiClient → FastAPI → PostgreSQL

### Architecture Decisions
- D1: ChatKit hosted mode (domain key) over custom chat UI
- D2: Client-side tool execution via `onClientTool` over server-side
- D3: OpenAI thread management over local Conversation/Message tables
- D4: localStorage for active thread persistence

### Implementation Plan (6 Phases)
- Phase 1: ChatKit package installation and configuration
- Phase 2: Tool call integration with backend (onClientTool → ApiClient → CRUD endpoints)
- Phase 3: Conversation persistence and resume (localStorage + setThreadId)
- Phase 4: Tool call UX and error handling
- Phase 5: Navigation integration (Chat link in Header)
- Phase 6: Final validation and polish

### Artifacts Generated
- research.md: ChatKit evaluation, frontend patterns, tool mapping, thread persistence
- data-model.md: No new models; documents existing entities consumed
- plan.md: 6-phase implementation plan with acceptance criteria
- quickstart.md: Developer setup guide with OpenAI Assistant tool configuration
- contracts/frontend-api-integration.yaml: Existing API endpoints consumed by frontend

## Outcome

- ✅ Impact: Complete implementation plan for ChatKit frontend integration with 6 phases and 4 architectural decisions documented
- 🧪 Tests: Constitution check 6/6 PASS; no gate violations
- 📁 Files: 5 planning artifacts created (plan.md, research.md, data-model.md, quickstart.md, contracts/frontend-api-integration.yaml)
- 🔁 Next prompts: Run `/sp.tasks` to generate dependency-ordered task list; configure OpenAI Assistant on platform
- 🧠 Reflection: ChatKit is a managed service, not a UI library — initial research incorrectly assumed it could be used with custom backends. User clarification about hosted mode with domain key resolved the architectural approach. The spec 006 backend chat endpoints remain as API-only fallback.

## Evaluation notes (flywheel)

- Failure modes observed: create-new-feature.sh created specs/ at repo root instead of Phase-3/specs/ (fixed manually); setup-plan.sh and update-agent-context.sh fail due to missing common.sh dependency
- Graders run and results (PASS/FAIL): Constitution check 6/6 PASS
- Prompt variant (if applicable): User provided detailed step-by-step implementation strategy in prompt, plus architecture clarification mid-planning
- Next experiment (smallest change to try): Fix .specify scripts to handle Phase-3 subdirectory structure
