---
id: 021
title: AI Chat API Specification
stage: spec
date: 2026-02-09
surface: agent
model: claude-opus-4-6
feature: 006-ai-chat-api
branch: 006-ai-chat-api
user: Hammad Afzal
command: /sp.specify
labels: ["ai-chat", "openai-agents-sdk", "mcp-tools", "stateless", "chat-api"]
links:
  spec: specs/006-ai-chat-api/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-ai-chat-api/spec.md
  - specs/006-ai-chat-api/checklists/requirements.md
tests:
  - none (specification phase)
---

## Prompt

/sp.specify Phase III – Spec 6: Stateless AI Chat API using OpenAI Agents SDK

Project context:
Phase III of the Todo AI Chatbot. Existing Phase-2 backend (FastAPI, SQLModel, Neon PostgreSQL, Better Auth) is already in working condition.
Spec-5 has delivered MCP tools for task management.

Objective:
Implement a stateless conversational chat API that uses OpenAI Agents SDK to interpret natural language todo commands and invoke MCP task tools, while persisting all conversation state in the database.

Core focus:
- AI reasoning and orchestration
- Stateless request-response cycle
- MCP tool invocation via OpenAI Agents SDK

AI configuration requirements:
- Use OpenAI Agents SDK for agent logic and tool execution
- Configure the Agents SDK to run on non-OpenAI models (Gemini or OpenRouter-backed models)
- Use Context7 MCP to:
  - Provide runtime configuration context for model routing
  - Configure provider selection (Gemini / OpenRouter)
  - Inject model, provider, and safety settings into the agent execution environment
- No direct OpenAI-hosted models required

API scope:
- Implement POST /api/{user_id}/chat
- Accept natural language input
- Return assistant response and tool call metadata

Conversation model:
- Server must be fully stateless
- Conversation history is fetched from the database on each request
- Messages are persisted before and after agent execution

Success criteria:
- User can manage todos using natural language via API
- Agent correctly maps intent to MCP tools
- Conversations resume correctly after server restart
- Agent successfully runs using Gemini or OpenRouter through Context7 MCP
- No server-side memory between requests

Constraints:
- Must integrate into existing backend only
- Must reuse existing database, auth, and task models
- No new backend service or server
- No frontend changes in this spec
- No manual task logic outside MCP tools

Not building:
- Frontend chat UI
- Streaming responses
- Multi-agent collaboration
- Long-term memory beyond conversation history
- Any state stored in application memory

Deliverables:
- Chat API endpoint
- Agent configuration using OpenAI Agents SDK
- Context7 MCP configuration for Gemini / OpenRouter
- Database-backed conversation flow
- Clean integration with MCP task tools

## Response snapshot

Created feature specification for "Stateless AI Chat API" (006-ai-chat-api) with 4 prioritized user stories covering natural language task management (P1), persistent conversation history (P2), AI model provider flexibility (P3), and error handling (P4). Defined 12 functional requirements, 7 measurable success criteria, and identified 3 key entities (Conversation, Message, Tool Call Record). Specification quality checklist passed all validation items with zero NEEDS CLARIFICATION markers. Branch 006-ai-chat-api created and spec written to Phase-3/specs/006-ai-chat-api/spec.md.

## Outcome

- ✅ Impact: Complete feature specification created for AI chat API integration
- 🧪 Tests: N/A (specification phase - no code written)
- 📁 Files: 2 files created (spec.md, checklists/requirements.md)
- 🔁 Next prompts: /sp.plan to generate implementation plan, /sp.clarify if refinements needed
- 🧠 Reflection: User provided exceptionally detailed feature description covering scope, constraints, and non-goals, enabling a zero-clarification spec

## Evaluation notes (flywheel)

- Failure modes observed: Initially created spec directory in wrong location (Hackathon-02 root instead of Phase-3); corrected immediately
- Graders run and results (PASS/FAIL): Quality checklist PASS (all 16 items validated)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
