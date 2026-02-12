# Tasks: Chat Frontend Integration & Agent UI

**Input**: Design documents from `/specs/007-chatkit-frontend/`
**Status**: All code tasks COMPLETE

---

## Implementation Summary

**Approach changed**: ChatKit hosted mode requires OpenAI domain allowlist which doesn't support `localhost`. Replaced with a **custom chat UI** that works with the existing `POST /api/chat` backend (Gemini-powered AI agent from spec 006). All tool calls handled server-side by the backend.

### Completed Tasks

- [x] T001 Install `@openai/chatkit-react` package (available for future production use with domain key)
- [x] T002 Create chat type definitions in `frontend/src/types/chat.ts` — ChatResponse, ConversationSummary, MessageInfo, ToolCallInfo, ConversationListResponse, ConversationDetailResponse
- [x] T003 Add `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` to `frontend/.env.local` with domain key
- [x] T004 Create ChatPage component in `frontend/src/components/Chat/ChatPage.tsx` — full custom chat UI with message list, input, conversation sidebar, tool call badges, loading states, error handling
- [x] T005 Create protected chat route in `frontend/app/chat/page.tsx` — auth check with redirect to login
- [x] T006 Add chat API methods to `frontend/src/lib/api.ts` — sendChatMessage, listConversations, getConversation
- [x] T007 Wire chat page to backend POST /api/chat endpoint with conversation persistence
- [x] T008 Add error handling — network errors, timeouts, API errors displayed inline
- [x] T009 Add conversation persistence — active conversation ID saved to localStorage, restored on page load
- [x] T010 Add conversation list sidebar — loads past conversations, click to resume, new chat button
- [x] T011 New conversation — clears messages, resets conversation ID, clears localStorage
- [x] T012 Add "Chat" navigation link in Header.tsx (desktop + mobile)
- [x] T013 Add active route highlighting for /chat and /tasks using usePathname()

### Files Created/Modified

| File | Action | Description |
|------|--------|-------------|
| `frontend/src/types/chat.ts` | CREATED | Chat API type definitions |
| `frontend/src/components/Chat/ChatPage.tsx` | CREATED | Full custom chat UI component |
| `frontend/app/chat/page.tsx` | CREATED | Protected chat route |
| `frontend/src/lib/chatkit-tools.ts` | CREATED | Placeholder (tool calls handled server-side) |
| `frontend/src/lib/api.ts` | MODIFIED | Added sendChatMessage, listConversations, getConversation methods |
| `frontend/src/components/Header/Header.tsx` | MODIFIED | Added Chat nav link + active highlighting |
| `frontend/.env.local` | MODIFIED | Added NEXT_PUBLIC_OPENAI_DOMAIN_KEY |
| `frontend/package.json` | MODIFIED | Added @openai/chatkit-react dependency |

### Features Implemented

1. **Send messages** — Type natural language, get AI responses from Gemini-powered backend
2. **Tool call badges** — Visual indicators showing what actions the AI performed (create_task, list_tasks, etc.)
3. **Conversation sidebar** — List of past conversations, click to resume any conversation
4. **New chat** — Button to start fresh conversation
5. **Conversation persistence** — Active conversation saved to localStorage, restored on refresh
6. **Loading states** — Animated dots while waiting for AI response
7. **Error handling** — Inline error display for network/API errors
8. **Empty state** — Welcome screen with suggested prompts
9. **Auto-scroll** — Messages auto-scroll to bottom
10. **Auto-resize input** — Textarea grows with content (up to 120px)
11. **Keyboard shortcuts** — Enter to send, Shift+Enter for new line
12. **Navigation** — Chat link in header with active state highlighting
13. **Mobile responsive** — Collapsible sidebar, full-width chat on mobile
14. **Auth protection** — Redirect to login if not authenticated

### Manual Tasks Remaining

- [ ] T014 Validate empty message prevention
- [ ] T015 Validate loading state display
- [ ] T016 Run end-to-end testing with backend running
- [ ] T017 Test all success criteria (SC-001 through SC-008)
- [ ] T018 Deploy frontend to Vercel (future)
- [ ] T019 Configure OpenAI domain allowlist with production domain (future, for ChatKit)
