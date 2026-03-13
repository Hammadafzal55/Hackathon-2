# Implementation Plan: Chat Frontend Integration & Agent UI

**Branch**: `007-chatkit-frontend` | **Date**: 2026-02-11 (updated 2026-02-12) | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/007-chatkit-frontend/spec.md`

## Summary

Custom chat UI integrated into the existing Next.js frontend to provide a conversational AI interface for task management. The frontend connects to the existing FastAPI `POST /api/chat` backend endpoint (Gemini/OpenRouter-powered AI agent). Tool calls are handled server-side by the backend agent. Conversations are persisted in the database via existing conversation/message models from spec 006.

**Implementation pivot**: ChatKit hosted mode was initially planned but OpenAI's domain allowlist doesn't accept `localhost`, making local development impossible. Replaced with a custom chat UI that works with the existing backend immediately. ChatKit package remains installed for potential future production use.

## Technical Context

**Language/Version**: TypeScript / Next.js 16.1.2 (App Router), React 19.2.3
**Primary Dependencies**: existing Better Auth, existing ApiClient, existing backend chat API
**Storage**: PostgreSQL via existing Conversation/Message tables (spec 006)
**Testing**: Manual verification (frontend integration)
**Target Platform**: Web browser (responsive, desktop + mobile)
**Project Type**: Web application (frontend + backend agent improvement)
**Performance Goals**: AI response displayed within 5 seconds (SC-001); tool confirmations visible for 100% of actions (SC-003)
**Constraints**: Must reuse existing backend chat endpoints; custom UI instead of ChatKit for local dev
**Scale/Scope**: Single-user concurrent; conversation history managed by backend database

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Agent-first Development**: All implementation via Claude Code tools following spec > plan > tasks workflow
- [x] **Stateless Architecture**: Backend remains fully stateless; conversation state managed by OpenAI's service
- [x] **Tool-driven AI Behavior**: Task operations executed via `onClientTool` → backend CRUD endpoints (same underlying task handlers)
- [x] **Natural Language Interface**: ChatKit provides seamless natural language UI; OpenAI processes intent and invokes tools
- [x] **Reliability and Persistence**: Task data persists in PostgreSQL; conversation history managed by OpenAI Threads
- [x] **Security and Authentication**: JWT auth enforced on all backend API calls from `onClientTool`; ChatKit domain allowlist for production

## Project Structure

### Documentation (this feature)

```text
specs/007-chatkit-frontend/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 research output
├── data-model.md        # Phase 1 data model (no new models)
├── quickstart.md        # Developer quickstart
├── contracts/
│   └── frontend-api-integration.yaml  # Existing API contract reference
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── chat/
│   │   └── page.tsx             # NEW - Chat page (protected route)
│   ├── layout.tsx               # EXISTING - no changes needed
│   ├── tasks/page.tsx           # EXISTING - no changes
│   └── ...
├── src/
│   ├── components/
│   │   ├── Chat/
│   │   │   └── ChatPage.tsx     # NEW - ChatKit wrapper component
│   │   ├── Header/
│   │   │   └── Header.tsx       # MODIFY - add Chat navigation link
│   │   └── ...
│   ├── lib/
│   │   ├── api.ts               # MODIFY - add chat tool execution methods
│   │   └── chatkit-tools.ts     # NEW - onClientTool handler mapping
│   ├── types/
│   │   └── chat.ts              # NEW - ChatKit-related type definitions
│   └── ...
├── package.json                 # MODIFY - add @openai/chatkit-react
└── .env.local                   # MODIFY - add NEXT_PUBLIC_OPENAI_DOMAIN_KEY
```

**Structure Decision**: Extend the existing `frontend/` Next.js application. New chat page under `app/chat/`. ChatKit component and tool handlers in `src/components/Chat/` and `src/lib/`. Minimal file count — ChatKit handles most UI rendering internally.

## Complexity Tracking

No constitution violations. ChatKit handles conversation UI; backend remains unchanged.

---

## Implementation Phases

### Phase 1: ChatKit Package Installation & Configuration

**Goal**: Install ChatKit and create the basic chat page with ChatKit rendering.

**Files**:
- `frontend/package.json` (MODIFY — add `@openai/chatkit-react`)
- `frontend/.env.local` (MODIFY — add `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`)
- `frontend/app/chat/page.tsx` (NEW — protected chat route)
- `frontend/src/components/Chat/ChatPage.tsx` (NEW — ChatKit wrapper)

**Design Decisions**:
- Use ChatKit hosted mode with domain key (simplest setup, no backend session management needed)
- Chat page is a protected route (same pattern as `/tasks`)
- ChatPage is a `'use client'` component wrapping the ChatKit component
- Domain key stored in `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` environment variable

**Key Pattern — ChatKit Setup**:
```typescript
'use client';
import { ChatKit, useChatKit } from '@openai/chatkit-react';

export function ChatPage() {
  const { control } = useChatKit({
    api: {
      domainKey: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY,
    },
    theme: 'auto', // respects system/app theme
    onClientTool: async (toolCall) => {
      // Handle tool calls — Phase 2
    },
    onThreadChange: ({ threadId }) => {
      // Persist active thread — Phase 3
    },
  });

  return <ChatKit control={control} className="h-full w-full" />;
}
```

**Acceptance**:
- [ ] `@openai/chatkit-react` installed and importable
- [ ] Chat page accessible at `/chat` (requires authentication)
- [ ] ChatKit renders with basic UI (message input, send button)
- [ ] Unauthenticated users redirected to login

**Commit**: `feat: integrate ChatKit UI with domain key configuration`

---

### Phase 2: Tool Call Integration with Backend

**Goal**: Connect ChatKit's `onClientTool` callback to the existing backend task CRUD endpoints.

**Files**:
- `frontend/src/lib/chatkit-tools.ts` (NEW — tool call handler)
- `frontend/src/lib/api.ts` (MODIFY — ensure task methods are accessible for tool calls)
- `frontend/src/components/Chat/ChatPage.tsx` (MODIFY — wire up `onClientTool`)
- `frontend/src/types/chat.ts` (NEW — tool call type definitions)

**Design Decisions**:
- Each tool call from OpenAI maps to an existing backend endpoint
- The `onClientTool` callback uses the existing `ApiClient` with JWT authentication
- Tool results are returned as strings back to ChatKit for the AI to incorporate in its response
- Authentication is enforced on every backend call (JWT Bearer token from Better Auth)

**Tool Mapping**:

| OpenAI Tool Name | Action | Backend Endpoint | Method |
|-----------------|--------|------------------|--------|
| `add_task` | Create task | `/api/tasks` | POST |
| `list_tasks` | List user tasks | `/api/tasks` | GET |
| `update_task` | Update task fields | `/api/tasks/{id}` | PUT |
| `complete_task` | Toggle completion | `/api/tasks/{id}/complete` | PATCH |
| `delete_task` | Delete task | `/api/tasks/{id}` | DELETE |

**Key Pattern — Tool Handler**:
```typescript
// src/lib/chatkit-tools.ts
import { apiClient } from './api';

export async function handleToolCall(toolCall: { name: string; arguments: Record<string, any> }) {
  switch (toolCall.name) {
    case 'add_task':
      const task = await apiClient.createTask({
        title: toolCall.arguments.title,
        description: toolCall.arguments.description,
        priority: toolCall.arguments.priority,
      });
      return { success: true, task_id: task.id, message: `Task "${task.title}" created` };

    case 'list_tasks':
      const tasks = await apiClient.fetchTasks();
      return { success: true, tasks, count: tasks.length };

    case 'update_task':
      const updated = await apiClient.updateTask(toolCall.arguments.task_id, {
        title: toolCall.arguments.title,
        description: toolCall.arguments.description,
        priority: toolCall.arguments.priority,
      });
      return { success: true, message: `Task updated` };

    case 'complete_task':
      await apiClient.toggleTaskCompletion(toolCall.arguments.task_id);
      return { success: true, message: `Task completion toggled` };

    case 'delete_task':
      await apiClient.deleteTask(toolCall.arguments.task_id);
      return { success: true, message: `Task deleted` };

    default:
      return { success: false, error: `Unknown tool: ${toolCall.name}` };
  }
}
```

**Acceptance**:
- [ ] `onClientTool` receives tool calls from ChatKit
- [ ] Each tool call maps to correct backend endpoint
- [ ] JWT token included in all backend requests
- [ ] Tool results returned to ChatKit for AI to process
- [ ] Error handling: backend errors return friendly error to ChatKit
- [ ] User can add a task via natural language and verify it in `/tasks` page

**Commit**: `feat: connect ChatKit to backend chat endpoint`

---

### Phase 3: Conversation Persistence & Resume

**Goal**: Allow users to resume conversations after page refresh and switch between conversations.

**Files**:
- `frontend/src/components/Chat/ChatPage.tsx` (MODIFY — add thread persistence)

**Design Decisions**:
- Store active thread ID in `localStorage` via `onThreadChange` callback
- On page mount, restore thread ID from `localStorage` and call `setThreadId()`
- Starting a new conversation: call `setThreadId(null)` and clear `localStorage`
- ChatKit internally manages thread message history via OpenAI's Threads API

**Key Pattern — Thread Persistence**:
```typescript
const THREAD_STORAGE_KEY = 'chatkit-active-thread';

// On ChatKit init
const savedThread = localStorage.getItem(THREAD_STORAGE_KEY);

const { control } = useChatKit({
  // ... config
  onThreadChange: ({ threadId }) => {
    if (threadId) {
      localStorage.setItem(THREAD_STORAGE_KEY, threadId);
    } else {
      localStorage.removeItem(THREAD_STORAGE_KEY);
    }
  },
});

// After control is ready, restore thread
useEffect(() => {
  if (savedThread && control) {
    control.setThreadId(savedThread);
  }
}, [control, savedThread]);
```

**Acceptance**:
- [ ] Active thread ID saved to `localStorage` on conversation change
- [ ] Page refresh restores the previous conversation
- [ ] New conversation clears the stored thread ID
- [ ] Conversation messages reload correctly from OpenAI after refresh

**Commit**: `feat: implement conversation resume support`

---

### Phase 4: Tool Call UX & Error Handling

**Goal**: Ensure tool call confirmations display clearly and errors are handled gracefully.

**Files**:
- `frontend/src/lib/chatkit-tools.ts` (MODIFY — enhance error handling)
- `frontend/src/components/Chat/ChatPage.tsx` (MODIFY — error state handling)

**Design Decisions**:
- ChatKit renders tool call results as part of the assistant's message automatically
- The `onClientTool` return value becomes the tool result that the AI incorporates into its response
- Structured return values help the AI generate clear confirmation messages
- Network errors and auth failures are caught and returned as tool failures

**Error Handling Strategy**:
```typescript
try {
  const result = await handleToolCall(toolCall);
  return result;
} catch (error) {
  if (error instanceof ApiError && error.status === 401) {
    // Auth expired — prompt re-login
    return { success: false, error: 'Session expired. Please refresh and log in again.' };
  }
  return { success: false, error: `Failed to execute ${toolCall.name}: ${error.message}` };
}
```

**Tool Confirmation Display**:
- The AI assistant receives the tool result and generates a natural-language confirmation
- Example: Tool returns `{success: true, message: "Task 'Buy groceries' created"}` → AI says "I've created a new task called 'Buy groceries' for you."
- Failed tools: AI says "I wasn't able to delete that task. The error was: Task not found."
- ChatKit natively renders the conversation flow including tool interactions

**Acceptance**:
- [ ] Successful tool calls result in clear AI confirmation messages
- [ ] Failed tool calls display the error reason in the conversation
- [ ] Network errors (backend unreachable) are handled gracefully
- [ ] Auth errors prompt user to re-authenticate
- [ ] No unhandled promise rejections or console errors

**Commit**: `feat: add tool confirmation and error handling UI`

---

### Phase 5: Navigation Integration

**Goal**: Add chat navigation to the application header so users can access chat from anywhere.

**Files**:
- `frontend/src/components/Header/Header.tsx` (MODIFY — add Chat link)

**Design Decisions**:
- Add a "Chat" link next to the existing "Tasks" link in the authenticated navigation
- Use the same styling pattern as the existing navigation items
- Chat link visible only to authenticated users (same as Tasks)
- Active route highlighting for `/chat`

**Acceptance**:
- [ ] "Chat" link appears in header navigation for authenticated users
- [ ] Chat link navigates to `/chat` page
- [ ] Active route highlighting works for the chat page
- [ ] Mobile responsive navigation includes chat link

**Commit**: `feat: add chat navigation to application header`

---

### Phase 6: Final Validation & Polish

**Goal**: End-to-end validation of all user stories and success criteria.

**Validation Checklist**:
- [ ] User can send a message and receive AI response (SC-001)
- [ ] User can add a task via natural language → verify in `/tasks` page (SC-002)
- [ ] User can list tasks via chat (SC-002)
- [ ] User can update a task via chat (SC-002)
- [ ] User can complete a task via chat (SC-002)
- [ ] User can delete a task via chat (SC-002)
- [ ] Tool confirmations display clearly in conversation (SC-003)
- [ ] Page refresh resumes the conversation (SC-004)
- [ ] User can start a new conversation (SC-005)
- [ ] Chat accessible from navigation header (SC-006)
- [ ] Error states show friendly messages (SC-007)
- [ ] No new backend services created (SC-008)

**Commit**: `feat: complete Spec 7 - ChatKit frontend and AI agent integration`

---

## Key Architectural Decisions

### D1: ChatKit Hosted Mode over Custom Chat UI

**Decision**: Use OpenAI ChatKit in hosted mode (domain key) rather than building a custom chat UI.

**Rationale**: ChatKit provides a complete, polished chat experience out of the box — message rendering, thread management, input handling, and tool call execution. Building a custom UI would require significantly more code for the same functionality. The domain key approach eliminates the need for backend session token management.

**Trade-off**: The AI provider switches from Gemini (spec 006) to OpenAI for the ChatKit path. The spec 006 Gemini-powered endpoint remains available as an API-only interface.

### D2: Client-Side Tool Execution via `onClientTool`

**Decision**: Execute tool calls on the frontend via `onClientTool` callback rather than server-side tool execution.

**Rationale**: The frontend already has authenticated API access via the `ApiClient` with JWT tokens. Client-side execution reuses the existing auth flow without requiring the backend to be publicly accessible to OpenAI's servers. No additional security exposure.

### D3: OpenAI Thread Management over Local Conversation Tables

**Decision**: Let OpenAI manage conversation threads rather than using the local Conversation/Message tables from spec 006.

**Rationale**: ChatKit's thread system handles conversation persistence, history, and context window management automatically. Using local tables would require a complex sync mechanism. The spec 006 tables remain for the API-only chat endpoint.

### D4: localStorage for Active Thread Persistence

**Decision**: Store the active thread ID in `localStorage` rather than a backend endpoint.

**Rationale**: The thread ID is a session-level concern (which conversation is the user viewing). It doesn't need cross-device sync. `localStorage` is the simplest approach that survives page refresh without backend roundtrips.

---

## Risk Analysis

1. **OpenAI API Key Requirement**: ChatKit hosted mode requires an OpenAI API key/domain key. This adds a dependency on OpenAI's platform. Mitigation: The spec 006 Gemini-powered endpoint remains as a fallback.

2. **Tool Call Fidelity**: OpenAI's model may not always invoke the correct tool or pass correct parameters. Mitigation: Clear tool descriptions, input validation in `onClientTool`, and error handling that returns helpful messages to the AI.

3. **ChatKit API Changes**: ChatKit is a relatively new library and its API may change. Mitigation: Pin the package version, test thoroughly before upgrading.

4. **Domain Allowlist Requirement**: Production deployment requires domain allowlisting on OpenAI's platform. This adds a manual deployment step. Mitigation: Document the setup process in quickstart.md; localhost works without allowlisting for development.

---

## Follow-ups

- `/sp.tasks` to generate the dependency-ordered task list from this plan
- Configure OpenAI Assistant with task management tools on OpenAI's platform
- Set up domain allowlist after frontend deployment
- Consider adding streaming response support as a future enhancement
