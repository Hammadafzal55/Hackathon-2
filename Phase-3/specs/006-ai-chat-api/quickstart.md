# Quickstart: Stateless AI Chat API

**Feature**: 006-ai-chat-api | **Date**: 2026-02-09

## Prerequisites

- Python 3.11+
- Existing Phase-3 backend running (FastAPI + SQLModel + Neon PostgreSQL)
- MCP task tools from Spec-5 operational
- At least one AI provider API key (Gemini or OpenRouter)

## 1. Install New Dependencies

```bash
cd backend
pip install openai-agents
```

This installs:
- `openai-agents` - OpenAI Agents SDK for agent orchestration (includes `AsyncOpenAI` client)
- No LiteLLM needed — Gemini and OpenRouter both expose OpenAI-compatible API endpoints

## 2. Environment Variables

Add to `backend/.env`:

```env
# AI Provider Configuration
AI_PROVIDER=gemini                           # "gemini" or "openrouter"
AI_MODEL=gemini-2.5-flash                    # Model name (provider-specific)

# Provider API Keys (set at least one)
GEMINI_API_KEY=your-gemini-api-key
OPENROUTER_API_KEY=your-openrouter-api-key   # Optional fallback/alternative

# Chat Configuration (optional)
CHAT_CONTEXT_WINDOW=50                       # Messages loaded per request
CHAT_MAX_MESSAGE_LENGTH=4000                 # Max input message length
```

## 3. Database Migration

New tables will be created: `conversation` and `message`.

```bash
cd backend
# Tables are auto-created by SQLModel on startup (existing pattern)
# Or run alembic migration if configured:
# alembic upgrade head
```

## 4. Verify Setup

Start the backend:
```bash
cd backend
uvicorn src.main:app --reload
```

Test the chat endpoint:
```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task called buy groceries with priority 3"}'
```

Expected response:
```json
{
  "conversation_id": "uuid-here",
  "message": "I've created a task 'buy groceries' with priority 3 for you.",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "arguments": {"title": "buy groceries", "priority": 3},
      "result": "Task created successfully",
      "success": true
    }
  ]
}
```

## 5. Key Files (after implementation)

```
backend/src/
├── models/
│   ├── conversation.py      # Conversation SQLModel
│   └── message.py           # Message SQLModel
├── services/
│   └── ai_agent.py          # Agent factory, tool wrappers, runner
├── api/routes/
│   └── chat.py              # POST /api/{user_id}/chat endpoint
└── config.py                # Extended with AI provider settings
```

## 6. Testing

```bash
cd backend
pytest tests/test_chat_api.py -v
```

## Common Issues

- **"GEMINI_API_KEY not set"**: Add key to `.env` file
- **"conversation table not found"**: Restart server to trigger table creation
- **Tool calls not working**: Verify MCP tools from Spec-5 are operational with `pytest tests/test_mcp_tools_integration.py`
- **Model errors with gemini-2.0-flash**: Use `gemini-2.5-flash` instead (2.0 is deprecated)
