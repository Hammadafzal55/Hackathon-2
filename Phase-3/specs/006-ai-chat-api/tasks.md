# Tasks: Stateless AI Chat API

**Input**: Design documents from `/specs/006-ai-chat-api/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/chat-api.yaml

**Tests**: Not explicitly requested in spec. Implementation tasks only.

**Organization**: Tasks grouped by user story (US1-US4) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`
- All paths relative to repository root (`/mnt/c/Users/User/Desktop/Hackathon-02/Phase-3/`)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependency and extend configuration for AI provider support

- [x] T001 Install `openai-agents` package and add to `backend/requirements.txt`
- [x] T002 Extend Settings class with AI provider fields (ai_model, gemini_api_key, chat_context_window, chat_max_message_length) in `backend/src/config.py`
- [x] T003 [P] Add AI environment variables to `backend/.env` and `backend/.env.example` (AI_MODEL=gemini-2.5-flash, GEMINI_API_KEY, CHAT_CONTEXT_WINDOW=50, CHAT_MAX_MESSAGE_LENGTH=4000)

**Checkpoint**: Settings load correctly, `openai-agents` importable, env vars configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database models and AI agent service that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 [P] Create Conversation SQLModel in `backend/src/models/conversation.py` with fields: id (UUID PK), user_id (str, indexed), title (str, default "New Conversation"), created_at (datetime), updated_at (datetime) — follow existing Task model pattern
- [x] T005 [P] Create Message SQLModel in `backend/src/models/message.py` with fields: id (UUID PK), conversation_id (UUID FK to conversation.id with CASCADE), role (str: user/assistant/tool), content (Optional[str]), tool_calls (Optional JSON column), tool_call_id (Optional[str]), tool_name (Optional[str]), created_at (datetime) — include composite index on (conversation_id, created_at)
- [x] T006 Import new models in `backend/src/models/__init__.py` (or database init) to ensure tables are auto-created on startup via SQLModel.metadata.create_all
- [x] T007 Create Pydantic request/response schemas in `backend/src/api/schemas/chat.py`: ChatRequest (message: str, conversation_id: Optional[UUID]), ChatResponse (conversation_id: UUID, message: str, tool_calls: List[ToolCallInfo]), ToolCallInfo (tool_name: str, arguments: dict, result: str, success: bool), ConversationListResponse, ConversationSummary, ConversationDetailResponse, MessageInfo — per contracts/chat-api.yaml
- [x] T008 Create AI agent service in `backend/src/services/ai_agent.py` with: create_task_tools(user_id, session) wrapping all 5 MCP handlers as @function_tool with user_id closure, create_agent(user_id, session) building Agent with AsyncOpenAI(base_url=Gemini endpoint) and OpenAIChatCompletionsModel(model="gemini-2.5-flash"), SYSTEM_PROMPT constant, and run_chat_agent(agent, messages) calling Runner.run and returning final_output + tool call metadata
- [x] T009 Add AI-specific exception classes in `backend/src/exceptions.py`: AIProviderError (503), AIConfigurationError (500), ConversationNotFoundError (404)

**Checkpoint**: Models created, schemas defined, agent service testable in isolation, tables auto-created on startup

---

## Phase 3: User Story 1 — Natural Language Task Management (Priority: P1) MVP

**Goal**: Users send natural language messages to manage tasks via AI chat endpoint. The AI interprets intent, calls MCP tools, and returns a conversational response.

**Independent Test**: POST /api/chat with "Add a task called buy groceries with priority 3" → verify response confirms task creation and task exists in DB.

**Maps to**: FR-001, FR-002, FR-003, FR-011 | SC-001, SC-006

### Implementation for User Story 1

- [x] T010 [US1] Create POST /api/chat endpoint in `backend/src/api/routes/chat.py` implementing the full stateless request cycle: authenticate JWT via Depends(get_current_user_id) from src/middleware/auth.py (same pattern as tasks.py) → load or create Conversation (scoped to user_id) → persist user Message → load last N messages as context → convert to SDK format → create Agent with tools → run Agent → extract response + tool call metadata → persist assistant Message → return ChatResponse
- [x] T011 [US1] Register chat router in `backend/src/main.py` with prefix `/api` and include it in the FastAPI app
- [x] T012 [US1] Write SYSTEM_PROMPT in `backend/src/services/ai_agent.py` defining the assistant's role (task management), capabilities (add, list, update, complete, delete tasks via tools), behavior (conversational, ask for clarification when ambiguous), and constraints (only manage tasks for current user, stay in scope)
- [x] T013 [US1] Implement convert_to_sdk_format() helper in `backend/src/services/ai_agent.py` that converts database Message objects to the input format expected by Runner.run() (list of dicts with role/content/tool_calls keys)

**Checkpoint**: User can send "Add a task called buy groceries" and receive a conversational response confirming task creation. All 5 task operations (add, list, update, complete, delete) work via natural language.

---

## Phase 4: User Story 2 — Persistent Conversation History (Priority: P2)

**Goal**: Multi-turn conversations persist in the database. The AI maintains context across messages within a conversation. Server restarts don't lose history.

**Independent Test**: Send "Add a task called dentist appointment", then send "Change its priority to 5" in same conversation → AI resolves "it" to the dentist task. Restart server → send follow-up → AI retains full context.

**Maps to**: FR-004, FR-005, FR-006 | SC-002, SC-004, SC-005

### Implementation for User Story 2

- [x] T014 [US2] Implement context window loading in `backend/src/api/routes/chat.py`: query last N messages (from settings.chat_context_window) for the conversation ordered by created_at ASC, using the composite index on (conversation_id, created_at)
- [x] T015 [US2] Handle conversation_id in chat endpoint: when conversation_id is provided, load existing Conversation (verify user_id ownership), when null/omitted create new Conversation with auto-generated title from first message — in `backend/src/api/routes/chat.py`
- [x] T016 [US2] Update Conversation.updated_at timestamp on each new message in `backend/src/api/routes/chat.py` to support ordering conversations by recent activity
- [x] T017 [US2] Persist tool-role messages in `backend/src/api/routes/chat.py`: when the agent makes tool calls, extract tool call metadata from the RunResult and persist both the assistant message (with tool_calls JSON) and tool result messages (with tool_call_id and tool_name) to maintain complete conversation history

**Checkpoint**: Multi-turn conversations work with pronoun resolution. Server restart preserves all history. Context window correctly limits loaded messages.

---

## Phase 5: User Story 4 — Error Handling and Graceful Failures (Priority: P4)

**Goal**: All error scenarios produce helpful responses without corrupting conversation state.

**Independent Test**: Send empty message → 400. Send to invalid conversation_id → 404. Simulate AI provider down → 503. Send ambiguous message → AI asks for clarification.

**Maps to**: FR-012 | SC-003

### Implementation for User Story 4

- [x] T018 [US4] Add input validation in chat endpoint in `backend/src/api/routes/chat.py`: reject empty/whitespace-only messages with 400, enforce max message length from settings, validate conversation_id format when provided
- [x] T019 [US4] Add AI provider error handling in run_chat_agent() in `backend/src/services/ai_agent.py`: catch Gemini connection errors and timeout errors, wrap in AIProviderError(503), ensure user message is already persisted before agent runs so it's not lost on failure
- [x] T020 [US4] Add conversation ownership validation in `backend/src/api/routes/chat.py`: when loading existing conversation, verify conversation.user_id matches authenticated user_id from JWT, return 404 when conversation_id doesn't exist or doesn't belong to user (no user_id in URL path — follows existing tasks.py pattern)

**Checkpoint**: All error scenarios (empty input, missing conversation, auth mismatch, provider down) return correct HTTP status codes with helpful messages. Conversation state remains consistent after any error.

---

## Phase 6: User Story 2 Extension — Conversation Management Endpoints (Priority: P2)

**Goal**: Users can list their conversations and view conversation history via dedicated endpoints.

**Independent Test**: GET /api/conversations → list of user's conversations ordered by recent. GET /api/conversations/{id} → conversation with messages.

**Maps to**: contracts/chat-api.yaml (listConversations, getConversation)

### Implementation for Conversation Management

- [x] T021 [US2] Implement GET /api/conversations endpoint in `backend/src/api/routes/chat.py`: list conversations for authenticated user, ordered by updated_at DESC, with pagination (limit/offset query params), include message_count per conversation, enforce user isolation
- [x] T022 [US2] Implement GET /api/conversations/{conversation_id} endpoint in `backend/src/api/routes/chat.py`: return conversation details with message history, ordered by created_at ASC, with limit query param (default 50), verify user owns conversation, return 404 if not found

**Checkpoint**: All 3 API endpoints functional (POST chat, GET list, GET detail). Full CRUD on conversations through chat + read-only management endpoints.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation across all user stories

- [x] T023 Verify statelessness: confirm no module-level mutable state in `backend/src/services/ai_agent.py` — agent and client created fresh per request, no cached sessions or conversations
- [x] T024 Verify user isolation: confirm all DB queries in `backend/src/api/routes/chat.py` filter by user_id — no endpoint returns data belonging to a different user
- [x] T025 Validate all endpoints match contracts/chat-api.yaml: verify request/response schemas, HTTP status codes, and error response formats match the OpenAPI spec
- [ ] T026 Run quickstart.md validation: follow steps in `specs/006-ai-chat-api/quickstart.md` to verify end-to-end setup and first chat message flow

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (config must be extended first) — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Phase 2 (models + agent service must exist)
- **User Story 2 (Phase 4)**: Depends on Phase 3 (chat endpoint must exist to add persistence logic)
- **User Story 4 (Phase 5)**: Depends on Phase 3 (chat endpoint must exist to add error handling)
- **Conversation Mgmt (Phase 6)**: Depends on Phase 4 (conversation persistence must work)
- **Polish (Phase 7)**: Depends on all prior phases

### User Story Dependencies

- **US1 (P1 — MVP)**: Requires Phase 2. No other story dependencies.
- **US2 (P2)**: Requires US1 endpoint (Phase 3) to exist. Extends it with persistence.
- **US4 (P4)**: Requires US1 endpoint (Phase 3) to exist. Adds error handling on top.

### Within Each User Story

- Models/schemas before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T004 + T005 can run in parallel (different model files)
- T003 can run in parallel with T004/T005 (env config vs models)
- US3 (Phase 5) can run in parallel with US2 (Phase 4) after US1 is done
- T026 + T027 + T028 can run in parallel in Phase 8

---

## Parallel Example: Phase 2 (Foundational)

```
# Launch model creation in parallel:
Task T004: "Create Conversation SQLModel in backend/src/models/conversation.py"
Task T005: "Create Message SQLModel in backend/src/models/message.py"

# Then sequentially:
Task T006: "Import new models for table auto-creation" (depends on T004, T005)
Task T007: "Create Pydantic schemas" (independent, can parallel with T006)
Task T008: "Create AI agent service" (depends on T007 for response types)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T009)
3. Complete Phase 3: User Story 1 (T010-T013)
4. **STOP and VALIDATE**: Send a chat message, verify AI creates a task
5. This is a deployable/demoable MVP

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Natural language task management works → **MVP!**
3. Add US2 → Multi-turn conversations persist → Demo
4. Add US4 → Error handling polished → Production-ready
5. Add US2 extension (Phase 6) → Conversation management → Complete
6. Polish → Validated and hardened → Ship

---

## Summary

| Phase | Story | Tasks | Files Modified/Created |
|-------|-------|-------|----------------------|
| Phase 1 | Setup | T001-T003 (3) | config.py, requirements.txt, .env |
| Phase 2 | Foundation | T004-T009 (6) | conversation.py, message.py, __init__.py, chat schemas, ai_agent.py, exceptions.py |
| Phase 3 | US1 (P1) | T010-T013 (4) | chat.py route, main.py, ai_agent.py |
| Phase 4 | US2 (P2) | T014-T017 (4) | chat.py route |
| Phase 5 | US4 (P4) | T018-T020 (3) | chat.py route, ai_agent.py |
| Phase 6 | US2 ext | T021-T022 (2) | chat.py route |
| Phase 7 | Polish | T023-T026 (4) | validation only |
| **Total** | | **26 tasks** | |

**Provider**: Gemini only (`gemini-2.5-flash`). If Gemini has issues, we manually switch entire config to OpenRouter.

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
