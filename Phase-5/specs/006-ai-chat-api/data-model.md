# Data Model: Stateless AI Chat API

**Feature**: 006-ai-chat-api | **Date**: 2026-02-09

## New Entities

### Conversation

Represents a chat session between a user and the AI assistant. A user may have multiple conversations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Unique conversation identifier |
| user_id | String | NOT NULL, INDEX, FK(user.id) | Owner of the conversation |
| title | String(255) | DEFAULT "New Conversation" | Auto-generated or user-set title |
| created_at | DateTime | NOT NULL, default utcnow | When conversation was created |
| updated_at | DateTime | NOT NULL, default utcnow | Last activity timestamp |

**Relationships**:
- `user_id` references `User.id` (Many conversations per user)
- One-to-many with `Message`

**Indexes**:
- `ix_conversation_user_id` on `user_id` (frequent filter)
- `ix_conversation_updated_at` on `updated_at` (ordering by recent)

### Message

A single exchange within a conversation. Covers user messages, assistant responses, and tool call/result messages.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Unique message identifier |
| conversation_id | UUID | NOT NULL, INDEX, FK(conversation.id) | Parent conversation |
| role | String(20) | NOT NULL | One of: "user", "assistant", "tool" |
| content | Text | NULLABLE | Message text content (null for pure tool calls) |
| tool_calls | JSON | NULLABLE | Array of tool call objects (for assistant messages) |
| tool_call_id | String(255) | NULLABLE | ID linking tool result to its call (for tool messages) |
| tool_name | String(100) | NULLABLE | Name of the tool that was called (for tool messages) |
| created_at | DateTime | NOT NULL, default utcnow | When message was created |

**Relationships**:
- `conversation_id` references `Conversation.id` with CASCADE delete
- No direct relationship to Task (tool calls reference tasks by ID in their content)

**Indexes**:
- `ix_message_conversation_id` on `conversation_id` (frequent filter)
- `ix_message_created_at` on `created_at` (ordering within conversation)
- Composite: `ix_message_conv_created` on (`conversation_id`, `created_at`) for efficient history loading

**Role Values**:
- `"user"`: Human user input message
- `"assistant"`: AI assistant response (may include tool_calls JSON)
- `"tool"`: Tool execution result (has tool_call_id and tool_name)

**tool_calls JSON Schema** (for assistant messages):
```json
[
  {
    "id": "call_abc123",
    "type": "function",
    "function": {
      "name": "add_task",
      "arguments": "{\"title\": \"Buy groceries\", \"priority\": 3}"
    }
  }
]
```

## Existing Entities (Referenced)

### User (no changes)
- `id`: String (PK) - Better Auth string ID
- `email`: String (unique, indexed)
- Existing model at `backend/src/models/user.py`

### Task (no changes)
- `id`: UUID (PK)
- `user_id`: String (indexed)
- `title`, `description`, `status`, `priority`, `due_date`
- Existing model at `backend/src/models/task.py`

## Entity Relationship Diagram

```
User (1) ───< (N) Conversation (1) ───< (N) Message
  │                                          │
  │                                     [role: user | assistant | tool]
  └───< (N) Task                        [tool_calls: JSON for assistant]
                                        [tool_call_id: for tool results]
```

## SQLModel Implementation Pattern

Following the existing codebase pattern (`backend/src/models/task.py`):

```python
# backend/src/models/conversation.py
class Conversation(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(nullable=False, index=True)
    title: str = Field(default="New Conversation", max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

# backend/src/models/message.py
class Message(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(nullable=False, index=True, foreign_key="conversation.id")
    role: str = Field(nullable=False, max_length=20)  # "user", "assistant", "tool"
    content: Optional[str] = Field(default=None)
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tool_call_id: Optional[str] = Field(default=None, max_length=255)
    tool_name: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

## Context Window Loading Query

On each request, load the last N messages for the conversation:

```sql
SELECT * FROM message
WHERE conversation_id = :conv_id
ORDER BY created_at ASC
LIMIT :context_window_size;
```

Default `context_window_size`: 50 messages (configurable via settings).

## Migration Notes

- New tables: `conversation`, `message`
- No changes to existing `task` or `user` tables
- Foreign key from `message.conversation_id` to `conversation.id` with ON DELETE CASCADE
- No foreign key from `conversation.user_id` to `user.id` (following existing Task pattern which omits FK for flexibility)
