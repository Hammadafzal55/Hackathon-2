# Todo Backend API

A FastAPI-based backend service for managing user tasks with secure authentication and data isolation.

## Overview

This backend provides RESTful API endpoints for managing user tasks. It uses:
- **FastAPI** for the web framework
- **SQLModel** for database modeling and ORM
- **PostgreSQL** with asyncpg for database operations
- **Alembic** for database migrations
- **Better Auth compatible JWT** for authentication

## Features

- Create, read, update, and delete tasks
- Secure user authentication with JWT tokens
- User data isolation (users can only access their own tasks)
- RESTful API design
- **MCP (Model Context Protocol) server for AI agent integration**
- **Stateless MCP tools for safe task operations**
- Comprehensive error handling
- Structured logging

## API Endpoints

- `GET /api/{user_id}/tasks` - Get all tasks for a user
- `POST /api/{user_id}/tasks` - Create a new task for a user
- `GET /api/{user_id}/tasks/{id}` - Get a specific task
- `PUT /api/{user_id}/tasks/{id}` - Update a specific task
- `DELETE /api/{user_id}/tasks/{id}` - Delete a specific task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle task completion status

## Authentication

The API expects JWT tokens in the Authorization header:
```
Authorization: Bearer <jwt-token>
```

The user ID in the URL must match the user ID in the JWT token for authorization.

## MCP Tools (Phase III)

The backend now includes an integrated MCP (Model Context Protocol) server that exposes task operations as MCP tools for AI agents.

### Available MCP Tools

1. **add_task** - Create a new task for the authenticated user
2. **list_tasks** - List all tasks for a user with optional filtering
3. **update_task** - Update an existing task
4. **complete_task** - Toggle task completion status
5. **delete_task** - Delete a task

### MCP Server Configuration

Configure the MCP server in your `.env` file:
```bash
MCP_SERVER_ENABLED=true
MCP_SERVER_PORT=8001
MCP_LOG_LEVEL=INFO
```

### Using MCP Tools

For detailed usage examples and API documentation, see [docs/MCP_TOOLS_USAGE.md](docs/MCP_TOOLS_USAGE.md).

**Example**:
```python
from src.services.mcp_server import get_mcp_server
from src.mcp_tools.schemas import AddTaskRequest

# Get the MCP server instance
mcp_server = get_mcp_server()

# Create a task request
request = AddTaskRequest(
    user_id="user-123",
    title="Buy groceries",
    priority=3
)

# Call the tool
result = await mcp_server.call_tool("add_task", request)
```

### Key Features

- **Stateless operations**: Each tool call uses a fresh database session
- **User isolation**: Tools automatically enforce user data isolation
- **Concurrent execution**: Tools can be called concurrently without interference
- **Comprehensive error handling**: All operations include proper error handling
- **Performance monitoring**: Tool execution is logged for monitoring

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and JWT secret
   ```

3. Run database migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```

## Running the Application

```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## Database Setup

The application uses Alembic for database migrations:

1. To run the initial migration (after setting up PostgreSQL):
   ```bash
   cd backend
   alembic upgrade head
   ```

2. To create a new migration:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

3. To rollback a migration:
   ```bash
   alembic downgrade -1
   ```

The initial migration (001_initial_migration_users_tasks.py) is already created and will set up the users and tasks tables with proper relationships and indexes.

## Environment Variables

- `DATABASE_URL`: PostgreSQL database connection string
- `JWT_SECRET_KEY`: Secret key for JWT token signing
- `JWT_ALGORITHM`: Algorithm for JWT (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)