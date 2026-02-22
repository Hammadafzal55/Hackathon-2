---
id: 029
title: OpenRouter Switch and Spec Completion
stage: green
date: 2026-02-12
surface: agent
model: claude-opus-4-6
feature: 007-chatkit-frontend
branch: 007-chatkit-frontend
user: hammad
command: sp.implement (continued)
labels: ["openrouter", "deepseek", "ai-provider", "agent-improvement", "completion"]
links:
  spec: specs/007-chatkit-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - Phase-3/backend/src/services/ai_agent.py
  - Phase-3/backend/src/config.py
  - Phase-3/backend/.env
  - Phase-3/specs/007-chatkit-frontend/plan.md
  - Phase-3/specs/007-chatkit-frontend/tasks.md
tests:
  - Manual: AI agent resolves positional task references (task 1, task 2)
  - Manual: AI agent resolves name-based task references (buy groceries)
  - Manual: OpenRouter DeepSeek model responds to chat messages
---

## Prompt

User reported Gemini quota exceeded. Switch to OpenRouter with DeepSeek model. Also fix AI agent to handle positional/name-based task references instead of requiring UUIDs.

Configuration provided:
- base_url: https://openrouter.ai/api/v1
- model: deepseek/deepseek-r1-0528:free
- api_key: sk-or-v1-... (OpenRouter key)

## Response snapshot

### Changes made

1. **AI provider switched from Gemini to OpenRouter + DeepSeek**
   - `backend/.env`: Added AI_API_KEY, AI_BASE_URL, AI_MODEL for OpenRouter; commented out old Gemini settings
   - `backend/src/config.py`: Added `ai_api_key`, `ai_base_url` fields with OpenRouter defaults; kept `gemini_api_key` as fallback
   - `backend/src/services/ai_agent.py`: Updated `create_agent()` to use `ai_api_key`/`ai_base_url` with fallback to `gemini_api_key`

2. **AI agent improved to handle natural task references**
   - System prompt updated with CRITICAL section on resolving task references
   - Agent now handles: positional ("task 2"), name-based ("buy groceries task"), description-based references
   - Agent instructed to ALWAYS call list_tasks first to resolve references, NEVER ask user for UUIDs
   - `list_tasks` output now includes numbered positions (1., 2., 3.) for positional mapping

3. **Spec 007 documentation finalized**
   - plan.md updated to reflect custom UI implementation (not ChatKit)
   - tasks.md updated with all 13 code tasks marked complete
   - PHRs 028 and 029 created

## Outcome

All spec 007 implementation complete. AI provider switched to OpenRouter/DeepSeek. Agent improved with natural language task references. Ready for commit.
