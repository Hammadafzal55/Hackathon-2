# Research: ChatKit Frontend Integration & Agent UI

**Feature**: 007-chatkit-frontend
**Date**: 2026-02-11
**Branch**: `007-chatkit-frontend`

---

## R1: OpenAI ChatKit Library Evaluation

### Findings

**Package**: `@openai/chatkit-react` (npm)

ChatKit is a **managed, batteries-included chat widget** that integrates with OpenAI's API infrastructure. Two deployment modes:

1. **Hosted mode (domain key)** — ChatKit connects to OpenAI's API using a domain key configured via OpenAI's platform. No `client_secret` management needed on the developer side. The domain must be allowlisted in OpenAI's security settings.

2. **Client secret mode** — Requires a backend endpoint to generate and refresh `client_secret` tokens from OpenAI's API.

### Key Capabilities

- **`<ChatKit />` component** — All-in-one chat UI (message list, input, thread management)
- **`useChatKit` hook** — Configuration and imperative control
- **Internal state management** — Messages and threads managed by ChatKit + OpenAI
- **Thread support** — `setThreadId(id)` for conversation switching, `setThreadId(null)` for new conversations
- **Client-side tools** — `onClientTool` callback for executing tool calls on the frontend
- **Theming** — Theme customization (colors, density, dark/light mode)
- **Peer dependencies** — React 18+, Next.js compatible

### Architecture: ChatKit Hosted Mode with Existing Backend

```
User → ChatKit UI → OpenAI API (hosted) → Tool Calls → onClientTool → Frontend API calls → FastAPI Backend → Database
```

1. User types message in ChatKit
2. ChatKit sends to OpenAI's hosted service (via domain key)
3. OpenAI's assistant processes the message and invokes tools
4. Tool calls return to frontend via `onClientTool` callback
5. Frontend executes tool calls by making API requests to the existing FastAPI backend
6. Results are returned to ChatKit → displayed to user

### Domain Allowlist Setup (Required for Hosted ChatKit)

1. Deploy frontend to get production URL
2. Navigate to: `https://platform.openai.com/settings/organization/security/domain-allowlist`
3. Add domain to allowlist
4. Get domain key from OpenAI
5. Set `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` in frontend environment

### Implications for Existing Architecture

| Aspect | Impact |
|--------|--------|
| Spec 006 POST /api/chat | **Not used by ChatKit** — ChatKit talks to OpenAI directly. Endpoint remains available as a fallback/API-only interface. |
| Spec 006 Conversation/Message tables | **Not used by ChatKit** — OpenAI manages threads internally. Tables remain for spec 006 API-only usage. |
| Spec 005 MCP tools | **Reused indirectly** — Tool logic wrapped as OpenAI function tools via `onClientTool`, which calls existing backend task CRUD endpoints. |
| Gemini AI provider | **Replaced by OpenAI** for ChatKit mode. OpenAI handles AI processing via hosted service. |
| Authentication | **Still required** — Frontend includes JWT Bearer token in API calls to backend task endpoints. |
| Stateless server | **Preserved** — Backend remains fully stateless. Conversation state managed by OpenAI. |

---

## R2: Frontend Codebase Patterns (from exploration)

### Existing Architecture

- **Framework**: Next.js 16.1.2 (App Router)
- **Auth**: Better Auth with JWT (`@/src/lib/auth.ts` client, `@/src/providers/AuthProvider.tsx`)
- **API Client**: Class-based singleton (`ApiClient` in `@/src/lib/api.ts`) with JWT token management
- **State**: Custom hooks (`useTasks`) + React Context (`AuthProvider`, `ThemeProvider`)
- **Styling**: Tailwind CSS with glassmorphism design, Framer Motion animations
- **Routing**: App Router with protected routes (redirect to login)
- **Navigation**: Header component with auth-aware nav items

### Key Files

| File | Purpose |
|------|---------|
| `app/layout.tsx` | Root layout: AuthProvider > ThemeProvider > Header > children |
| `app/tasks/page.tsx` | Protected tasks page with auth redirect |
| `src/lib/api.ts` | API client with JWT, retry, error handling (526 lines) |
| `src/lib/auth.ts` | Better Auth client instance |
| `src/providers/AuthProvider.tsx` | Auth context + session management |
| `src/hooks/useTasks.ts` | Task state management hook |
| `src/components/Header/Header.tsx` | Navigation with auth-aware links |

### Patterns to Follow

- Protected routes: check `user` from `useAuth()`, redirect if null
- API calls: use `ApiClient` with `getAuthHeaders()` for Bearer token
- Component structure: `src/components/<Feature>/<Component>.tsx`
- Hooks: `src/hooks/use<Feature>.ts`

---

## R3: ChatKit Integration Approach

### Component Architecture

```
app/chat/page.tsx                  — Chat page (protected route)
src/components/Chat/
  └── ChatPage.tsx                 — Client component wrapping ChatKit
```

ChatKit provides its own message list, input, and thread management. The frontend needs minimal custom components — mainly the page route and the ChatKit configuration wrapper.

### Tool Call Handling via `onClientTool`

When ChatKit's AI assistant invokes a tool, the `onClientTool` callback receives the tool call. The frontend executes it by calling the backend API:

```
onClientTool("add_task", {title: "Buy groceries"})
  → ApiClient.createTask({title: "Buy groceries"})
  → POST /api/tasks with Bearer token
  → Return result to ChatKit
```

### Tool-to-API Mapping

| Tool Name | Backend API Call | Method |
|-----------|-----------------|--------|
| add_task | `/api/tasks` | POST |
| list_tasks | `/api/tasks` | GET |
| update_task | `/api/tasks/{id}` | PUT |
| complete_task | `/api/tasks/{id}/complete` | PATCH |
| delete_task | `/api/tasks/{id}` | DELETE |

### Conversation Management

- ChatKit manages threads internally via OpenAI's Threads API
- `setThreadId(id)` to resume a conversation
- `setThreadId(null)` to start new
- `onThreadChange` callback to persist active thread ID to `localStorage`
- On page load: restore thread ID from `localStorage`

---

## R4: OpenAI Assistant Configuration

For ChatKit to work, an OpenAI Assistant needs to be configured on the OpenAI platform with:

1. **System instructions**: Task management assistant for the Todo app
2. **Tools**: Function tools matching the backend's task CRUD operations
3. **Model**: OpenAI model (e.g., gpt-4o-mini or gpt-4o)

The assistant is configured once on OpenAI's platform, not in code. ChatKit connects to it via the domain key.

---

## Summary of Resolved Questions

| Unknown | Resolution |
|---------|------------|
| ChatKit integration approach | Hosted mode with domain key; AI processed by OpenAI |
| How tools work with existing backend | `onClientTool` callback makes API calls to backend task endpoints |
| Conversation persistence | OpenAI manages threads; frontend stores active thread ID in localStorage |
| Impact on spec 006 work | Spec 006 chat endpoint remains as API-only interface; ChatKit is the primary UI |
| AI provider | OpenAI (via hosted ChatKit) replaces Gemini for the chat UI path |
| New dependencies | `@openai/chatkit-react` package |
