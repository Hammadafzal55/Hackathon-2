---
id: 022
title: AI Chat API Implementation Plan
stage: plan
date: 2026-02-09
surface: agent
model: claude-opus-4-6
feature: 006-ai-chat-api
branch: 006-ai-chat-api
user: Hammad Afzal
command: /sp.plan
labels: ["ai-chat", "openai-agents-sdk", "litellm", "implementation-plan", "stateless"]
links:
  spec: specs/006-ai-chat-api/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-ai-chat-api/plan.md
  - specs/006-ai-chat-api/research.md
  - specs/006-ai-chat-api/data-model.md
  - specs/006-ai-chat-api/quickstart.md
  - specs/006-ai-chat-api/contracts/chat-api.yaml
tests:
  - none (planning phase)
---

## Prompt

/sp.plan Phase III – Spec 6: Stateless AI Chat API using OpenAI Agents SDK

Implementation Plan Phases:
1. Database Models – Conversation + Message SQLModel entities
2. Configuration – Extend Settings with AI provider env vars
3. AI Agent Service – OpenAI Agents SDK + LiteLLM + MCP tool wrappers
4. Chat Endpoint – POST /api/{user_id}/chat with full stateless cycle
5. Conversation Management – GET endpoints for history listing
6. Error Handling – Graceful failures for all identified scenarios
7. Integration Testing – Full chat flow + statelessness + user isolation

Key decisions: Use LitellmModel for Gemini/OpenRouter, wrap MCP handlers as function_tools with user_id closure, embed tool calls as JSON in Message table, Context7 MCP is documentation provider not model router.

## Response snapshot

Generated complete implementation plan for "Stateless AI Chat API" (006-ai-chat-api) with 7 implementation phases, 4 key architectural decisions, and 3 risk mitigations. Created 5 planning artifacts: research.md (provider research + integration patterns), data-model.md (Conversation + Message entities), contracts/chat-api.yaml (OpenAPI spec for 3 endpoints), quickstart.md (developer setup guide), and plan.md (full implementation plan with phase breakdowns, acceptance criteria, and project structure).

## Outcome

- ✅ Impact: Complete implementation plan with all Phase 1 design artifacts generated
- 🧪 Tests: N/A (planning phase - no code written)
- 📁 Files: 5 files created (plan.md, research.md, data-model.md, quickstart.md, contracts/chat-api.yaml)
- 🔁 Next prompts: /sp.tasks to generate dependency-ordered task list, then /sp.implement to execute
- 🧠 Reflection: Research phase clarified Context7 MCP as documentation provider rather than model router; LitellmModel selected as primary integration path over global client override for better per-agent control

## Evaluation notes (flywheel)

- Failure modes observed: Context window ran out during extended session requiring continuation; Context7 MCP initially misunderstood as model routing system (corrected via web research)
- Graders run and results (PASS/FAIL): Constitution check PASS (all 6 principles verified)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
