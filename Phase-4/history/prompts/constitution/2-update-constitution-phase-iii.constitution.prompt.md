---
id: 2
title: Update Constitution Phase III
stage: constitution
date: 2026-02-07
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: 004-auth-integration
user: User
command: /sp.constitution
labels: [constitution,ai-chatbot,mcp,stateless]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

```
/sp.constitution

Project: Phase III – Todo AI Chatbot (AI-native task management via MCP)

Core principles:
- Agent-first development (spec → plan → tasks → implementation)
- Stateless backend architecture with database-backed state
- Tool-driven AI behavior (no direct DB access by agents)
- Natural language as the primary user interface
- Reliability across restarts and deployments

Key standards:
- All task operations must be executed via MCP tools only
- AI logic must use OpenAI Agents SDK
- MCP server must use Official MCP SDK
- FastAPI server must remain stateless at all times
- Conversation history reconstructed from database on each request
- All user and assistant messages must be persisted
- Authentication enforced via Better Auth

Constraints:
- No manual coding; implementation only via Claude Code
- Technology stack is fixed and non-negotiable:
  - Frontend: OpenAI ChatKit
  - Backend: Python FastAPI
  - AI Framework: OpenAI Agents SDK
  - MCP Server: Official MCP SDK
  - ORM: SQLModel
  - Database: Neon Serverless PostgreSQL
  - Auth: Better Auth
- MCP tools must be single-responsibility and stateless
- Server must hold zero in-memory session or conversation state

Not building:
- Stateful chat servers or in-memory agents
- Direct database access by AI agents
- UI-heavy or non-chat-based task management
- Advanced AI features beyond defined task operations
- Manual task CRUD outside MCP tools

Success criteria:
- Users can manage todos via natural language
- AI correctly infers intent and invokes MCP tools
- Conversations persist across server restarts
- System behaves predictably and is review-ready
- All specs and plans comply fully with this constitution
```

## Response snapshot

The constitution file was successfully updated from the Phase II Todo Full-Stack Web Application constitution to the Phase III Todo AI Chatbot constitution. The new constitution includes:

- Core principles focused on agent-first development, stateless architecture, tool-driven AI behavior, natural language interface, and reliability
- Technical standards for the new tech stack including OpenAI ChatKit, OpenAI Agents SDK, Official MCP SDK
- Updated constraints reflecting the AI/MCP architecture and avoiding stateful implementations
- Success criteria aligned with AI chatbot functionality

The version was incremented from 1.0 to 2.0 to reflect the significant architectural shift from a traditional web application to an AI-native chatbot system.

## Outcome

- ✅ Impact: High - Complete rewrite of project constitution for AI chatbot focus
- 🧪 Tests: None - Documentation update only
- 📁 Files: 1 file updated (.specify/memory/constitution.md)
- 🔁 Next prompts: Ready for spec creation following new constitution
- 🧠 Reflection: The new constitution properly captures the MCP and AI-focused approach of Phase III

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Not applicable
- Prompt variant (if applicable): Standard constitution update
- Next experiment (smallest change to try): Begin spec creation for Phase III features