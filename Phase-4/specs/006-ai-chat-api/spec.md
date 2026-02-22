# Feature Specification: Stateless AI Chat API

**Feature Branch**: `006-ai-chat-api`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "Phase III - Spec 6: Stateless AI Chat API using OpenAI Agents SDK. Implement a stateless conversational chat API that uses OpenAI Agents SDK to interpret natural language todo commands and invoke MCP task tools, while persisting all conversation state in the database. Configure Agents SDK for non-OpenAI models (Gemini/OpenRouter) via Context7 MCP."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task Management (Priority: P1)

An authenticated user sends a natural language message (e.g., "Add a task to buy groceries with priority 3") to the chat endpoint. The system interprets the user's intent, invokes the appropriate task management tool, performs the action, and returns a conversational response confirming what was done along with metadata about which tools were called.

**Why this priority**: This is the core value proposition of the entire feature. Without natural language task management, there is no chat API. It enables users to manage their todos without learning specific commands or navigating a UI.

**Independent Test**: Can be fully tested by sending a POST request with a natural language instruction and verifying the AI response correctly reflects the completed task action and that the task exists in the database.

**Acceptance Scenarios**:

1. **Given** an authenticated user with no tasks, **When** the user sends "Add a task called buy groceries with priority 3", **Then** the system creates a task titled "buy groceries" with priority 3 and returns a confirmation message.
2. **Given** an authenticated user with existing tasks, **When** the user sends "Show me all my tasks", **Then** the system returns a human-readable list of the user's tasks.
3. **Given** an authenticated user with existing tasks, **When** the user sends "Mark the groceries task as done", **Then** the system marks the matching task as completed and confirms the action.
4. **Given** an authenticated user with existing tasks, **When** the user sends "Delete the groceries task", **Then** the system deletes the matching task and confirms removal.
5. **Given** an authenticated user, **When** the user sends "Update priority of groceries task to 5", **Then** the system updates the task's priority and confirms the change.

---

### User Story 2 - Persistent Conversation History (Priority: P2)

A user has an ongoing conversation with the AI assistant. Every message (both user and assistant messages, including tool calls) is stored in the database. When the user sends a new message, the system loads the full conversation history from the database, includes it as context for the AI, and processes the new message with full conversational awareness. After a server restart, conversations resume seamlessly.

**Why this priority**: Without conversation persistence, the AI cannot maintain context between messages, making multi-turn interactions impossible. This is essential for a usable conversational experience.

**Independent Test**: Can be tested by sending multiple messages, restarting the server, and verifying the AI references previous conversation context correctly in its response.

**Acceptance Scenarios**:

1. **Given** a user who previously said "Add a task called dentist appointment", **When** the user later sends "Change its priority to 5", **Then** the system understands "it" refers to the dentist appointment task and updates it correctly.
2. **Given** a conversation with 10+ messages, **When** a new message is sent, **Then** the system includes previous messages as context and responds coherently.
3. **Given** a server that has been restarted, **When** a user sends a follow-up message, **Then** the conversation resumes with full history intact from the database.
4. **Given** a new user with no prior conversation, **When** the user sends their first message, **Then** a new conversation is created and the message is stored.

---

### User Story 3 - AI Model Provider Flexibility (Priority: P3)

The system uses an AI agent framework to orchestrate tool calls, but is configured to work with alternative model providers (Gemini or OpenRouter-hosted models) rather than requiring direct access to OpenAI's hosted models. Runtime configuration determines which provider and model are used for AI reasoning.

**Why this priority**: This enables cost flexibility and provider independence. It also removes the hard requirement on OpenAI API keys, allowing the system to run with alternative providers.

**Independent Test**: Can be tested by configuring the system to use Gemini or OpenRouter, sending a chat message, and verifying the AI responds correctly and invokes tools as expected.

**Acceptance Scenarios**:

1. **Given** the system is configured to use an alternative model provider, **When** a user sends a natural language task command, **Then** the AI correctly interprets the intent and invokes the right tool.
2. **Given** a valid runtime configuration for model routing, **When** the chat endpoint is called, **Then** the system uses the configured provider for AI reasoning without errors.
3. **Given** an invalid or missing model configuration, **When** the chat endpoint is called, **Then** the system returns a clear error message indicating the configuration issue.

---

### User Story 4 - Error Handling and Graceful Failures (Priority: P4)

When a user sends a message that cannot be processed (ambiguous intent, failed tool calls, invalid input), the system returns a helpful, human-readable error response rather than crashing or returning raw error data. The conversation state remains consistent even when errors occur.

**Why this priority**: Robust error handling is essential for a production-quality API, but the core functionality must work before polishing failure modes.

**Independent Test**: Can be tested by sending malformed, ambiguous, or edge-case messages and verifying the system responds gracefully without corrupting conversation state.

**Acceptance Scenarios**:

1. **Given** a user sends an ambiguous message like "Do the thing", **When** the AI cannot determine the intent, **Then** the system responds asking for clarification rather than taking an incorrect action.
2. **Given** a tool call fails (e.g., task not found), **When** the error occurs during processing, **Then** the system returns a friendly error message and the conversation remains in a valid state.
3. **Given** a user sends an empty message, **When** the request is processed, **Then** the system returns a validation error with a clear message.
4. **Given** the AI model provider is temporarily unavailable, **When** a user sends a message, **Then** the system returns a service unavailability message without losing the user's message.

---

### Edge Cases

- What happens when the user sends a message unrelated to task management (e.g., "What's the weather?")?
  - The AI responds conversationally but does not invoke any task tools, staying within the scope of a task management assistant.
- What happens when the conversation history grows very large (100+ messages)?
  - The system loads a bounded window of recent messages (most recent N messages) to maintain performance while preserving relevant context.
- What happens when two requests arrive simultaneously for the same user?
  - Each request operates independently with its own database read/write cycle. The most recently persisted state wins, and no in-memory locking is required due to the stateless architecture.
- What happens when the user references a task that has been deleted?
  - The AI informs the user that the referenced task no longer exists.
- What happens when authentication fails or the user ID is invalid?
  - The system returns an authentication error before any AI processing occurs.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept natural language text input and return a conversational AI response with tool call metadata.
- **FR-002**: System MUST interpret user intent from natural language and map it to the correct task management operation (add, list, update, complete, delete).
- **FR-003**: System MUST invoke existing MCP task tools exclusively for all task operations - no direct database manipulation for task management.
- **FR-004**: System MUST persist every user message and assistant response (including tool call details) in the database before and after AI processing.
- **FR-005**: System MUST load conversation history from the database on each request - no conversation state stored in application memory.
- **FR-006**: System MUST be fully stateless - a server restart must not lose any conversation data or affect the ability to resume conversations.
- **FR-007**: System MUST support AI reasoning through alternative model providers (Gemini or OpenRouter) without requiring direct OpenAI API access.
- **FR-008**: System MUST use runtime configuration to determine which AI model provider and model are used for reasoning.
- **FR-009**: System MUST enforce user isolation - users can only access and manage their own tasks and conversation history.
- **FR-010**: System MUST integrate into the existing backend without creating new services or servers.
- **FR-011**: System MUST return structured response data including the assistant's text response and metadata about any tool calls made.
- **FR-012**: System MUST handle errors gracefully, returning human-readable error messages without corrupting conversation state.

### Key Entities

- **Conversation**: Represents a chat session belonging to a user. Contains an ordered sequence of messages. A user may have one or more conversations.
- **Message**: A single exchange within a conversation. Has a role (user, assistant, or tool), content text, optional tool call metadata, and a timestamp. Messages are ordered chronologically within their conversation.
- **Tool Call Record**: Metadata about an MCP tool invocation made during AI processing. Includes the tool name, input parameters, output result, and success/failure status. Associated with a specific assistant message.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can manage all five task operations (add, list, update, complete, delete) through natural language with at least 90% intent recognition accuracy on standard task commands.
- **SC-002**: Conversations resume correctly after server restart with 100% of message history preserved in the database.
- **SC-003**: Chat responses are returned within 10 seconds for standard task commands under normal load.
- **SC-004**: Users can reference previous conversation context (e.g., "mark it as done") and the system resolves the reference correctly in at least 80% of follow-up messages.
- **SC-005**: The system operates with zero server-side memory between requests - verified by restarting the server between every request in a test sequence and confirming correct behavior.
- **SC-006**: 100% of task operations performed through the chat API are executed via MCP tools with no direct database manipulation.
- **SC-007**: The system successfully processes chat requests using at least one non-OpenAI model provider (Gemini or OpenRouter).

## Assumptions

- The existing MCP task tools (add_task, list_tasks, update_task, complete_task, delete_task) from Spec-5 are fully operational and tested.
- The existing Better Auth authentication system provides valid user IDs that can be used to scope conversations and tasks.
- The existing database (Neon PostgreSQL) can accommodate the additional conversation and message tables without schema conflicts.
- A reasonable conversation context window (last 50 messages) is sufficient for maintaining conversational coherence.
- The OpenAI Agents SDK supports configuration for alternative model providers through its extensibility mechanisms.
- Context7 MCP is available as a configuration mechanism for model provider routing.
- API rate limiting and abuse prevention are out of scope for this specification and will be addressed separately if needed.
- The chat API is consumed by other services or a future frontend - no UI is built in this spec.

## Scope Boundaries

### In Scope
- Single chat API endpoint for natural language task management
- AI agent configuration with alternative model provider support
- Database-backed conversation persistence (messages and tool call metadata)
- Integration with existing MCP task tools from Spec-5
- Conversation context loading from database per request
- Runtime model provider configuration via Context7 MCP
- Error handling for failed tool calls, ambiguous input, and provider issues

### Out of Scope
- Frontend chat UI (separate spec)
- Streaming/real-time responses (future enhancement)
- Multi-agent collaboration
- Long-term memory beyond conversation history
- Any state stored in application memory
- Rate limiting or abuse prevention
- Multi-language support
- Voice input/output
- File attachments or media in conversations

## Dependencies

- **Spec-5 (MCP Task Tools)**: All five task management MCP tools must be operational
- **Better Auth**: Authentication system must provide valid user context
- **Neon PostgreSQL**: Database must be accessible for conversation storage
- **OpenAI Agents SDK**: Must be installable and configurable for alternative providers
- **Context7 MCP**: Must be available for runtime model configuration
- **AI Model Provider**: At least one of Gemini or OpenRouter must be accessible with valid API credentials
