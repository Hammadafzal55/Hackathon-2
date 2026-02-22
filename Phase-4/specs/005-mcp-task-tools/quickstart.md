# Quickstart Guide: MCP Server + Task Tools Foundation

## Overview
This guide explains how to set up and use the MCP (Model Context Protocol) server with task tools in the Todo AI Chatbot application.

## Prerequisites
- Python 3.11+
- FastAPI application running
- Better Auth configured for authentication
- Neon PostgreSQL database connected
- Official MCP SDK installed

## Installation

### 1. Add MCP SDK Dependency
Add the Official MCP SDK to your `requirements.txt`:
```bash
pip install model-context-protocol  # or whatever the actual package name is
```

### 2. Project Structure
Ensure your project has the following structure:
```
backend/
├── src/
│   ├── models/
│   │   ├── task.py
│   │   └── user.py
│   ├── services/
│   │   └── mcp_server.py
│   ├── mcp_tools/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   └── handlers.py
│   └── main.py
```

## Configuration

### 1. Update main.py
Modify your main FastAPI application to initialize the MCP server alongside your existing application:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

# Import MCP server initialization
from src.services.mcp_server import initialize_mcp_server

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    await initialize_database()

    # Initialize MCP server
    await initialize_mcp_server()

    yield  # Application runs here

    # Cleanup on shutdown
    logger.info("Shutting down the application...")

# Create FastAPI app instance
app = FastAPI(lifespan=lifespan)
```

### 2. Environment Variables
Ensure your environment variables include any necessary MCP configuration:
```
MCP_SERVER_ENABLED=true
MCP_SERVER_PORT=8001  # Or whatever port is appropriate
```

## MCP Tools Usage

### Available Tools
The MCP server exposes the following tools for AI agents to use:

#### 1. add_task
Creates a new task for the authenticated user.

**Parameters**:
- `title` (string, required): Title of the task
- `description` (string, optional): Description of the task
- `priority` (integer, optional): Priority level (1-5)
- `due_date` (string, optional): Due date in ISO format
- `user_id` (string, required): ID of the user creating the task

**Example**:
```json
{
  "tool_name": "add_task",
  "parameters": {
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "priority": 3,
    "user_id": "user-123"
  }
}
```

#### 2. list_tasks
Retrieves all tasks for the authenticated user.

**Parameters**:
- `user_id` (string, required): ID of the user whose tasks to list
- `status_filter` (string, optional): Filter by status (pending, completed, etc.)

**Example**:
```json
{
  "tool_name": "list_tasks",
  "parameters": {
    "user_id": "user-123",
    "status_filter": "pending"
  }
}
```

#### 3. update_task
Updates an existing task for the authenticated user.

**Parameters**:
- `task_id` (string, required): ID of the task to update
- `user_id` (string, required): ID of the user requesting the update
- `title` (string, optional): New title
- `description` (string, optional): New description
- `status` (string, optional): New status
- `priority` (integer, optional): New priority
- `due_date` (string, optional): New due date

**Example**:
```json
{
  "tool_name": "update_task",
  "parameters": {
    "task_id": "task-456",
    "user_id": "user-123",
    "status": "completed",
    "priority": 5
  }
}
```

#### 4. complete_task
Toggles the completion status of a task.

**Parameters**:
- `task_id` (string, required): ID of the task to toggle
- `user_id` (string, required): ID of the user requesting the change
- `complete` (boolean, optional): Whether to complete (true) or uncomplete (false) the task

**Example**:
```json
{
  "tool_name": "complete_task",
  "parameters": {
    "task_id": "task-456",
    "user_id": "user-123",
    "complete": true
  }
}
```

#### 5. delete_task
Deletes a task for the authenticated user.

**Parameters**:
- `task_id` (string, required): ID of the task to delete
- `user_id` (string, required): ID of the user requesting deletion

**Example**:
```json
{
  "tool_name": "delete_task",
  "parameters": {
    "task_id": "task-456",
    "user_id": "user-123"
  }
}
```

## Testing the MCP Server

### 1. Start the Server
Run your FastAPI application as usual:
```bash
uvicorn src.main:app --reload
```

### 2. Verify MCP Tools
Once the server starts, verify that the MCP tools are available and responding correctly. The tools should be registered and accessible to AI agents.

### 3. Test Individual Tools
Test each tool individually to ensure they work correctly:
- Create a task using `add_task`
- List tasks using `list_tasks`
- Update a task using `update_task`
- Toggle completion using `complete_task`
- Delete a task using `delete_task`

## Troubleshooting

### Common Issues

1. **Tool not found**: Verify that the MCP server is properly initialized and tools are registered.

2. **Authentication errors**: Ensure the `user_id` parameter is correctly passed and authenticated.

3. **Database connection issues**: Check that your database connection is active and the SQLModel session is properly configured.

4. **User isolation not working**: Verify that all tools properly check the `user_id` against the task's `user_id` field.

## Next Steps

1. Integrate the MCP tools with your AI agent
2. Implement error handling for edge cases
3. Add monitoring and logging for tool usage
4. Set up automated tests for all MCP tools