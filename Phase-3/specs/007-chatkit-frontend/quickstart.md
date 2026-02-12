# Developer Quickstart: ChatKit Frontend Integration

**Feature**: 007-chatkit-frontend
**Date**: 2026-02-11

---

## Prerequisites

1. **Backend running** on `http://localhost:8000` with task CRUD endpoints functional
2. **Frontend running** on `http://localhost:3000` with authentication working
3. **OpenAI API access** with ChatKit domain key (get from OpenAI platform)
4. **OpenAI Assistant configured** with task management tools (see below)
5. **User account** created via signup page

## OpenAI Setup (One-Time)

### 1. Configure Domain Allowlist

1. Go to: https://platform.openai.com/settings/organization/security/domain-allowlist
2. Add `localhost` for development (if required)
3. For production: add your deployment URL (e.g., `https://your-app.vercel.app`)
4. Copy the domain key provided

### 2. Set Environment Variable

Add to `frontend/.env.local`:
```
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here
```

### 3. Configure OpenAI Assistant

Create an Assistant on OpenAI's platform with:
- **Name**: Todo Task Assistant
- **Instructions**: "You are a task management assistant. Help users manage their todo list by creating, listing, updating, completing, and deleting tasks. Always confirm actions clearly."
- **Tools**: Add the following function tools:

```json
[
  {
    "name": "add_task",
    "description": "Create a new task for the user",
    "parameters": {
      "type": "object",
      "required": ["title"],
      "properties": {
        "title": {"type": "string", "description": "Task title"},
        "description": {"type": "string", "description": "Task description"},
        "priority": {"type": "integer", "description": "Priority 1-5, default 1"}
      }
    }
  },
  {
    "name": "list_tasks",
    "description": "List all tasks for the current user",
    "parameters": {"type": "object", "properties": {}}
  },
  {
    "name": "update_task",
    "description": "Update an existing task",
    "parameters": {
      "type": "object",
      "required": ["task_id"],
      "properties": {
        "task_id": {"type": "string", "description": "UUID of the task to update"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "priority": {"type": "integer"},
        "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "cancelled"]}
      }
    }
  },
  {
    "name": "complete_task",
    "description": "Toggle task completion status",
    "parameters": {
      "type": "object",
      "required": ["task_id"],
      "properties": {
        "task_id": {"type": "string", "description": "UUID of the task to complete"}
      }
    }
  },
  {
    "name": "delete_task",
    "description": "Delete a task permanently",
    "parameters": {
      "type": "object",
      "required": ["task_id"],
      "properties": {
        "task_id": {"type": "string", "description": "UUID of the task to delete"}
      }
    }
  }
]
```

## Development Setup

```bash
cd Phase-3/frontend

# Install ChatKit
npm install @openai/chatkit-react

# Start development server
npm run dev
```

## Key Files to Create

```
app/chat/page.tsx                        — Chat page (protected route)
src/components/Chat/ChatPage.tsx         — ChatKit wrapper component
src/lib/chatkit-tools.ts                 — Tool call handler (onClientTool)
src/types/chat.ts                        — ChatKit type definitions
```

## Key Files to Modify

```
src/components/Header/Header.tsx         — Add "Chat" navigation link
src/lib/api.ts                           — Ensure task methods accessible for tool calls
package.json                             — Add @openai/chatkit-react dependency
.env.local                               — Add NEXT_PUBLIC_OPENAI_DOMAIN_KEY
```

## Quick Validation

After implementation, verify:

- [ ] Chat page loads at `/chat` (requires authentication)
- [ ] ChatKit renders (message input visible)
- [ ] Send "What tasks do I have?" → AI lists tasks
- [ ] Send "Add a task: Buy groceries" → task appears in `/tasks` page
- [ ] Send "Delete the groceries task" → task removed
- [ ] Refresh page → conversation still visible
- [ ] Header shows "Chat" navigation link
- [ ] Navigate from chat to tasks and back

## Architecture Reference

```
User → ChatKit UI → OpenAI (hosted) → Tool Call → onClientTool → ApiClient → FastAPI → PostgreSQL
```

Key benefits:
- **MCP Tools**: Standardized interface for AI to interact with the app
- **Single Endpoint**: AI handles routing to tools automatically
- **Stateless Server**: Backend remains fully stateless and horizontally scalable
- **Tool Composition**: Agent can chain multiple tools in one turn
