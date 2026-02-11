# Implementation Plan: Stateless AI Chat API

**Branch**: `006-ai-chat-api` | **Date**: 2026-02-09 | **Spec**: [specs/006-ai-chat-api/spec.md](spec.md)
**Input**: Feature specification from `/specs/006-ai-chat-api/spec.md`

## Summary

Implement a stateless conversational chat API endpoint (`POST /api/chat`) that uses the OpenAI Agents SDK with `OpenAIChatCompletionsModel` to interpret natural language todo commands and invoke existing MCP task tool handlers. All conversation state is persisted in Neon PostgreSQL via new Conversation and Message tables. The agent is created fresh per request with zero in-memory state.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, SQLModel, OpenAI Agents SDK (`openai-agents`)
**Storage**: Neon Serverless PostgreSQL (existing) + new Conversation/Message tables
**Testing**: pytest + pytest-asyncio (existing test infrastructure)
**Target Platform**: Linux server (FastAPI on uvicorn)
**Project Type**: Web application (backend-only for this spec)
**Performance Goals**: <10s response for standard task commands (SC-003)
**Constraints**: Zero server-side memory between requests, integrate into existing backend only
**Scale/Scope**: Single user concurrent requests, 50-message context window

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Agent-first Development**: All implementation via Claude Code tools following spec > plan > tasks workflow
- [x] **Stateless Architecture**: Agent created per request, conversation loaded from DB, zero in-memory state
- [x] **Tool-driven AI Behavior**: All task operations via wrapped MCP tool handlers, no direct DB access by agent
- [x] **Natural Language Interface**: Users manage todos via natural language through chat API endpoint
- [x] **Reliability and Persistence**: Conversation history persists in PostgreSQL, survives restarts
- [x] **Security and Authentication**: JWT auth required, user isolation enforced on conversations and tasks

## Project Structure

### Documentation (this feature)

```text
specs/006-ai-chat-api/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 research output
├── data-model.md        # Phase 1 data model
├── quickstart.md        # Phase 1 developer quickstart
├── contracts/
│   └── chat-api.yaml    # OpenAPI contract for chat endpoints
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py              # Existing - no changes
│   │   ├── user.py              # Existing - no changes
│   │   ├── conversation.py      # NEW - Conversation SQLModel
│   │   └── message.py           # NEW - Message SQLModel
│   ├── services/
│   │   ├── mcp_server.py        # Existing - no changes
│   │   └── ai_agent.py          # NEW - Agent factory + tool wrappers + runner
│   ├── api/routes/
│   │   ├── tasks.py             # Existing - no changes
│   │   └── chat.py              # NEW - Chat API endpoints
│   ├── mcp_tools/
│   │   ├── handlers.py          # Existing - referenced by tool wrappers
│   │   └── schemas.py           # Existing - referenced by tool wrappers
│   ├── database/
│   │   ├── database.py          # Existing - no changes
│   │   └── init.py              # Existing - may need model imports
│   ├── config.py                # MODIFIED - add AI provider settings
│   ├── auth.py                  # Existing - no changes
│   ├── main.py                  # MODIFIED - register chat routes
│   └── exceptions.py            # Existing - may extend for AI errors
│
└── tests/
    ├── test_chat_api.py              # NEW - Chat endpoint integration tests
    ├── test_ai_agent.py              # NEW - Agent + tool wrapper unit tests
    ├── test_conversation_models.py   # NEW - Model CRUD tests
    ├── conftest.py                   # Existing - may extend fixtures
    ├── test_mcp_tools_integration.py # Existing - no changes
    └── test_mcp_concurrency.py       # Existing - no changes
```

**Structure Decision**: Extend the existing `backend/` web application structure. New models go in `models/`, new service logic in `services/`, new routes in `api/routes/`. This follows the established patterns from Spec-5.

## Complexity Tracking

No constitution violations. All additions follow existing patterns.

---

## Implementation Phases

### Phase 1: Database Models (Conversation + Message)

**Goal**: Create SQLModel entities for conversation persistence.

**Files**:
- `backend/src/models/conversation.py` (NEW)
- `backend/src/models/message.py` (NEW)
- `backend/src/database/init.py` (MODIFY - import new models for table creation)

**Design Decisions**:
- Follow existing Task model pattern: UUID primary keys, `user_id` as string (no FK constraint), `created_at`/`updated_at` timestamps
- `Message.tool_calls` stored as JSON column (SQLAlchemy `Column(JSON)`)
- `Message.conversation_id` has a foreign key to `Conversation.id` with CASCADE delete
- No `ToolCallRecord` as a separate table - tool call data is embedded in the Message's `tool_calls` JSON field (simpler, avoids extra joins)

**Acceptance**:
- [ ] Conversation model with: id, user_id, title, created_at, updated_at
- [ ] Message model with: id, conversation_id, role, content, tool_calls, tool_call_id, tool_name, created_at
- [ ] Tables auto-created on startup via existing SQLModel.metadata.create_all pattern
- [ ] Unit tests for model creation and querying

### Phase 2: Configuration Extension

**Goal**: Add AI provider settings to the existing Settings class.

**Files**:
- `backend/src/config.py` (MODIFY)
- `backend/.env.example` (MODIFY or CREATE)

**Settings to add**:
```python
# AI Provider settings
ai_provider: str = Field(default="gemini", alias="AI_PROVIDER")
ai_model: str = Field(default="gemini-2.5-flash", alias="AI_MODEL")
gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
openrouter_api_key: Optional[str] = Field(default=None, alias="OPENROUTER_API_KEY")

# Chat settings
chat_context_window: int = Field(default=50, alias="CHAT_CONTEXT_WINDOW")
chat_max_message_length: int = Field(default=4000, alias="CHAT_MAX_MESSAGE_LENGTH")
```

**Acceptance**:
- [ ] Settings class includes all AI provider fields
- [ ] Environment variables load correctly from .env
- [ ] Default values are sensible (gemini provider, 50 message context window)

### Phase 3: AI Agent Service

**Goal**: Create the agent factory that wraps MCP handlers as Agents SDK function tools and runs the agent per request.

**Files**:
- `backend/src/services/ai_agent.py` (NEW)

**Architecture**:

```
Request → create_agent(user_id) → Agent with tools → Runner.run(agent, messages) → Response
```

1. **Tool Wrappers**: Wrap each existing MCP handler as an `@function_tool` compatible function. The `user_id` is injected via closure (not exposed to the LLM).

2. **Agent Factory**: `create_agent(user_id, session)` returns a configured Agent with:
   - System instructions for task management assistant behavior
   - OpenAIChatCompletionsModel with AsyncOpenAI client pointing to configured provider
   - All 5 task tools with user_id bound

3. **Runner**: `run_agent(agent, messages)` calls `Runner.run()` and extracts the response text + tool call metadata.

**Key Pattern - Tool Wrapper with User ID Closure** (verified via Context7 MCP):

The `@function_tool` decorator auto-extracts name from function name, description from docstring, and schema from type hints. Supports both sync/async functions.

```python
def create_task_tools(user_id: str, session: AsyncSession):
    @function_tool
    async def add_task(title: str, description: str = "", priority: int = 1) -> str:
        """Add a new task for the user.

        Args:
            title: The title of the task to create.
            description: Optional description for the task.
            priority: Priority level from 1-5.
        """
        request = AddTaskRequest(user_id=user_id, title=title, description=description, priority=priority)
        result = await add_task_handler(request, session=session)
        return f"Task '{title}' created with id {result.task_id}"

    # ... similar for list_tasks, update_task, complete_task, delete_task
    return [add_task, list_tasks, update_task, complete_task, delete_task]
```

**Key Pattern - Agent Creation with OpenAIChatCompletionsModel**:

Uses `AsyncOpenAI` client with provider-specific `base_url`. No LiteLLM dependency needed — both Gemini and OpenRouter expose OpenAI-compatible APIs.

```python
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, function_tool

def create_agent(user_id: str, session: AsyncSession) -> Agent:
    settings = get_settings()
    tools = create_task_tools(user_id, session)

    client = AsyncOpenAI(
        api_key=settings.gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    return Agent(
        name="TaskAssistant",
        instructions=SYSTEM_PROMPT,
        model=OpenAIChatCompletionsModel(
            model=settings.ai_model,  # "gemini-2.5-flash"
            openai_client=client,
        ),
        tools=tools,
    )
```

**Provider strategy**: Gemini only for now. If Gemini has API issues, we manually switch the entire config to OpenRouter (same `OpenAIChatCompletionsModel` pattern, different `base_url` and `api_key`).

**Key Pattern - Running Agent with History**:

Conversation history is managed manually via database queries (not SDK sessions, which don't fully support non-OpenAI providers):

```python
async def run_chat(user_id: str, conversation_id: UUID, new_message: str, session: AsyncSession):
    # Load history from DB
    messages = await load_messages_from_db(conversation_id, limit=settings.chat_context_window)

    # Convert to SDK input format
    input_messages = convert_to_sdk_format(messages)
    input_messages.append({"role": "user", "content": new_message})

    # Create fresh agent per request (stateless)
    agent = create_agent(user_id, session)

    # Run agent
    result = await Runner.run(agent, input_messages)

    # Extract response
    return result.final_output  # string response from agent
```

**System Prompt** (stored as constant in ai_agent.py):
- Role: Task management assistant
- Capabilities: Add, list, update, complete, delete tasks
- Behavior: Use tools for task operations, be conversational, ask for clarification when intent is ambiguous
- Constraints: Only manage tasks for the current user, stay within task management scope

**Acceptance**:
- [ ] 5 function tools wrap existing MCP handlers correctly
- [ ] Agent factory creates agent with LitellmModel
- [ ] Runner executes agent and returns response + tool call metadata
- [ ] User ID is injected via closure, not exposed to LLM
- [ ] Tracing disabled for non-OpenAI providers
- [ ] Unit tests for tool wrappers (mock handlers)

### Phase 4: Chat API Endpoint

**Goal**: Implement the `POST /api/chat` endpoint with the full stateless request cycle.

**Files**:
- `backend/src/api/routes/chat.py` (NEW)
- `backend/src/main.py` (MODIFY - register chat router)

**Request Flow** (10 steps from research.md):
1. Receive POST /api/chat with `{message, conversation_id?}`
2. Authenticate user via Better Auth JWT (reuse existing `get_current_user_id` from `src/middleware/auth.py`)
3. Load or create Conversation from database (scoped to authenticated user_id)
5. Persist user message to database
6. Load last N messages from database as context
7. Convert messages to Agents SDK format
8. Create Agent with tools (user_id injected via closure)
9. Run Agent with message history
10. Extract assistant response + tool call metadata
11. Persist assistant message(s) to database
12. Return ChatResponse to client

**Pydantic Request/Response Models** (in chat.py or separate schemas file):
- `ChatRequest`: message (str), conversation_id (Optional[UUID])
- `ChatResponse`: conversation_id (UUID), message (str), tool_calls (List[ToolCallInfo])
- `ToolCallInfo`: tool_name (str), arguments (dict), result (str), success (bool)

**Acceptance**:
- [ ] POST /api/chat endpoint registered and accessible
- [ ] JWT authentication enforced (via Depends(get_current_user_id) — same pattern as tasks.py)
- [ ] New conversation created when conversation_id is null
- [ ] Existing conversation loaded when conversation_id is provided
- [ ] User message persisted before agent execution
- [ ] Agent response persisted after execution
- [ ] Response includes conversation_id, message text, and tool_calls array
- [ ] Integration test: send message, verify task created + response correct

### Phase 5: Conversation Management Endpoints

**Goal**: Add read-only endpoints for listing conversations and viewing conversation history.

**Files**:
- `backend/src/api/routes/chat.py` (EXTEND)

**Endpoints**:
- `GET /api/conversations` - List conversations with pagination
- `GET /api/conversations/{conversation_id}` - Get conversation with message history

**Acceptance**:
- [ ] List conversations returns user's conversations ordered by updated_at DESC
- [ ] Get conversation returns messages ordered by created_at ASC
- [ ] User isolation enforced (can only see own conversations)
- [ ] Pagination works correctly

### Phase 6: Error Handling

**Goal**: Graceful error handling for all failure modes identified in the spec.

**Error Scenarios**:
- Empty message → 400 with validation error
- AI provider unavailable → 503 with service unavailability message
- Tool call fails (e.g., task not found) → Agent handles gracefully, returns friendly message
- Invalid conversation_id → 404
- Authentication failure → 401 (existing handler)
- User ID mismatch → 403

**Files**:
- `backend/src/exceptions.py` (EXTEND - add AI-specific exceptions)
- `backend/src/services/ai_agent.py` (EXTEND - error handling in runner)
- `backend/src/api/routes/chat.py` (EXTEND - endpoint error handling)

**Key Principle**: Errors during AI processing should not corrupt conversation state. If the agent fails mid-execution, the user message is already persisted but no partial assistant message is saved.

**Acceptance**:
- [ ] All error scenarios return appropriate HTTP status codes
- [ ] Conversation state remains consistent after errors
- [ ] AI provider errors return 503 with helpful message
- [ ] User's message is not lost on agent failure

### Phase 7: Integration Testing

**Goal**: Comprehensive tests covering the full stateless chat flow.

**Files**:
- `backend/tests/test_chat_api.py` (NEW)
- `backend/tests/test_ai_agent.py` (NEW)
- `backend/tests/test_conversation_models.py` (NEW)
- `backend/tests/conftest.py` (EXTEND - add chat-specific fixtures)

**Test Categories**:

1. **Model Tests** (`test_conversation_models.py`):
   - Create conversation, create messages, query by conversation_id
   - Context window loading (last N messages)
   - Cascade delete (deleting conversation removes messages)

2. **Agent Tests** (`test_ai_agent.py`):
   - Tool wrappers call correct handlers with user_id
   - Agent creation with LitellmModel configuration
   - Response extraction (text + tool calls)
   - Mock AI provider to avoid real API calls in unit tests

3. **Integration Tests** (`test_chat_api.py`):
   - Full chat flow: send message → agent processes → tool called → response returned
   - Conversation continuity: multi-turn conversation with context
   - Statelessness: verify no state between requests
   - Error handling: invalid input, missing conversation, auth failures
   - User isolation: user A cannot access user B's conversations

**Acceptance**:
- [ ] All model CRUD operations tested
- [ ] Tool wrappers tested with mock handlers
- [ ] Full chat flow tested end-to-end (with mock AI provider)
- [ ] Statelessness verified
- [ ] User isolation verified
- [ ] Error scenarios tested

---

## Key Architectural Decisions

### D1: Tool Wrappers over Direct MCP Server Connection

**Decision**: Wrap existing MCP handlers as `@function_tool` functions instead of connecting to the MCP server via `MCPServerStdio`.

**Rationale**: Same process, no IPC overhead, simpler debugging, direct access to handler return types. The MCP server is an external interface; internally we call handlers directly.

### D2: Embedded Tool Calls over Separate ToolCallRecord Table

**Decision**: Store tool call metadata as JSON within the Message table's `tool_calls` column instead of a separate `ToolCallRecord` table.

**Rationale**: Simpler schema, fewer joins, follows OpenAI message format naturally. Tool call data is always read alongside its parent message, never queried independently.

### D3: OpenAIChatCompletionsModel over LitellmModel

**Decision**: Use `OpenAIChatCompletionsModel` with `AsyncOpenAI(base_url=provider_url)` instead of `LitellmModel` from the LiteLLM extension.

**Rationale**: No extra dependency needed (`openai-agents` core only vs `openai-agents[litellm]`). Both Gemini and OpenRouter expose OpenAI-compatible API endpoints, so a standard `AsyncOpenAI` client with a custom `base_url` is sufficient. Simpler, no beta-stability concerns, no special patches or tracing configuration required.

### D4: User ID Closure over Tool Parameter

**Decision**: Inject user_id into tools via Python closure rather than exposing it as a tool parameter for the LLM.

**Rationale**: Security - the LLM should not be able to fabricate or modify the user_id. The authenticated user_id from JWT is bound at agent creation time and cannot be overridden by the AI.

---

## Risk Analysis

1. **Tool Calling Fidelity**: Gemini/OpenRouter models may not handle tool calling identically to OpenAI models. Mitigation: Thorough testing with actual provider, clear system prompt with explicit tool descriptions, graceful handling of malformed tool calls.

2. **Context Window Limits**: Loading 50 messages may exceed model context for some providers. Mitigation: Configurable window size, truncation strategy, monitor token usage in responses.

3. **Provider API Compatibility**: Gemini's and OpenRouter's OpenAI-compatible endpoints may not support all features (e.g., certain message formats, tool_choice options). Mitigation: Test with actual providers during development, add provider-specific error handling.

---

## Follow-ups

- `/sp.tasks` to generate the dependency-ordered task list from this plan
- Frontend chat UI will be a separate spec (out of scope for 006)
- Streaming responses can be added as a future enhancement
