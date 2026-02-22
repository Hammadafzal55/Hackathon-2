# MCP Tools Usage Guide

## Overview
This document provides examples and usage instructions for all MCP (Model Context Protocol) task tools available in the Todo AI Chatbot backend.

## Available Tools

The MCP server exposes 5 core task management tools:
1. `add_task` - Create a new task
2. `list_tasks` - List all tasks for a user
3. `update_task` - Update an existing task
4. `complete_task` - Toggle task completion status
5. `delete_task` - Delete a task

## Tool Usage Examples

### 1. add_task

**Purpose**: Create a new task for the authenticated user.

**Request Schema**:
```python
{
    "user_id": "string (required)",
    "title": "string (required, 1-255 chars)",
    "description": "string (optional, max 1000 chars)",
    "priority": "integer (optional, 1-5, default: 1)",
    "due_date": "datetime (optional, ISO format)"
}
```

**Example Usage**:
```python
from src.mcp_tools.schemas import AddTaskRequest
from src.services.mcp_server import get_mcp_server

# Create a request
request = AddTaskRequest(
    user_id="user-123",
    title="Buy groceries",
    description="Milk, bread, eggs, and vegetables",
    priority=3,
    due_date="2026-02-10T18:00:00"
)

# Call the tool
mcp_server = get_mcp_server()
result = await mcp_server.call_tool("add_task", request)

# Response
# {
#     "task_id": "uuid",
#     "message": "Task created successfully",
#     "task": {
#         "id": "uuid",
#         "title": "Buy groceries",
#         "description": "Milk, bread, eggs, and vegetables",
#         "status": "pending",
#         "priority": 3,
#         "due_date": "2026-02-10T18:00:00",
#         "user_id": "user-123",
#         "created_at": "2026-02-08T10:00:00",
#         "updated_at": "2026-02-08T10:00:00",
#         "completed_at": null
#     }
# }
```

### 2. list_tasks

**Purpose**: Retrieve all tasks for the authenticated user with optional filtering.

**Request Schema**:
```python
{
    "user_id": "string (required)",
    "status_filter": "string (optional)",
    "limit": "integer (optional)",
    "offset": "integer (optional, default: 0)"
}
```

**Example Usage**:
```python
from src.mcp_tools.schemas import ListTasksRequest
from src.services.mcp_server import get_mcp_server

# List all tasks
request = ListTasksRequest(user_id="user-123")
result = await mcp_server.call_tool("list_tasks", request)

# List only pending tasks with pagination
request = ListTasksRequest(
    user_id="user-123",
    status_filter="pending",
    limit=10,
    offset=0
)
result = await mcp_server.call_tool("list_tasks", request)

# Response
# {
#     "tasks": [
#         {
#             "id": "uuid",
#             "title": "Buy groceries",
#             ...
#         },
#         ...
#     ],
#     "total_count": 5
# }
```

### 3. update_task

**Purpose**: Update an existing task with new values.

**Request Schema**:
```python
{
    "user_id": "string (required)",
    "task_id": "uuid (required)",
    "title": "string (optional, 1-255 chars)",
    "description": "string (optional, max 1000 chars)",
    "status": "string (optional)",
    "priority": "integer (optional, 1-5)",
    "due_date": "datetime (optional)"
}
```

**Example Usage**:
```python
from src.mcp_tools.schemas import UpdateTaskRequest
from src.services.mcp_server import get_mcp_server

# Update task title and priority
request = UpdateTaskRequest(
    user_id="user-123",
    task_id="task-uuid",
    title="Buy groceries (urgent!)",
    priority=5
)
result = await mcp_server.call_tool("update_task", request)

# Response
# {
#     "task_id": "uuid",
#     "message": "Task updated successfully",
#     "task": {
#         "id": "uuid",
#         "title": "Buy groceries (urgent!)",
#         "priority": 5,
#         ...
#     }
# }
```

### 4. complete_task

**Purpose**: Toggle the completion status of a task.

**Request Schema**:
```python
{
    "user_id": "string (required)",
    "task_id": "uuid (required)",
    "complete": "boolean (optional, default: true)"
}
```

**Example Usage**:
```python
from src.mcp_tools.schemas import CompleteTaskRequest
from src.services.mcp_server import get_mcp_server

# Mark task as completed
request = CompleteTaskRequest(
    user_id="user-123",
    task_id="task-uuid",
    complete=True
)
result = await mcp_server.call_tool("complete_task", request)

# Mark task as incomplete
request = CompleteTaskRequest(
    user_id="user-123",
    task_id="task-uuid",
    complete=False
)
result = await mcp_server.call_tool("complete_task", request)

# Response
# {
#     "task_id": "uuid",
#     "message": "Task completion status updated successfully",
#     "task": {
#         "id": "uuid",
#         "status": "completed",
#         "completed_at": "2026-02-08T10:30:00",
#         ...
#     }
# }
```

### 5. delete_task

**Purpose**: Delete a task permanently.

**Request Schema**:
```python
{
    "user_id": "string (required)",
    "task_id": "uuid (required)"
}
```

**Example Usage**:
```python
from src.mcp_tools.schemas import DeleteTaskRequest
from src.services.mcp_server import get_mcp_server

# Delete a task
request = DeleteTaskRequest(
    user_id="user-123",
    task_id="task-uuid"
)
result = await mcp_server.call_tool("delete_task", request)

# Response
# {
#     "task_id": "uuid",
#     "message": "Task deleted successfully"
# }
```

## Error Handling

All tools implement comprehensive error handling:

- **Authentication Errors**: `401 Unauthorized` - Missing or invalid user_id
- **Authorization Errors**: `403 Forbidden` - User doesn't have access to the task
- **Not Found Errors**: `404 Not Found` - Task or user doesn't exist
- **Validation Errors**: `422 Unprocessable Entity` - Invalid input parameters
- **Server Errors**: `500 Internal Server Error` - Database or server errors

## User Isolation

All tools enforce strict user isolation:
- Users can only access their own tasks
- Operations automatically filter by user_id
- Cross-user access attempts are rejected with 403 Forbidden

## Statelessness

All MCP tools are stateless:
- Each tool call uses a fresh database session
- No in-memory state is maintained between calls
- Operations are independent and can run concurrently
- Proper resource cleanup in finally blocks

## Performance

Tool operations are optimized for performance:
- Target response time: < 2 seconds for typical operations
- Database queries use proper indexing
- Efficient session management
- Logging for performance monitoring

## Configuration

MCP server configuration options in `.env`:
```bash
MCP_SERVER_ENABLED=true
MCP_SERVER_PORT=8001
MCP_LOG_LEVEL=INFO
```

## Monitoring and Logging

All tool operations are logged:
- Tool invocation logging
- User identification logging
- Error and exception logging
- Performance metrics logging

Check application logs for detailed information about tool execution.