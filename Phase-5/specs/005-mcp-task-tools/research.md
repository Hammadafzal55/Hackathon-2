# Research: MCP Server + Task Tools Foundation

## Overview
This research document covers the investigation of MCP (Model Context Protocol) SDK integration, task model analysis, and implementation approach for the MCP task tools in the existing FastAPI backend.

## MCP SDK Analysis

### Decision: Use Official MCP SDK for Python
**Rationale**: The specification requires the use of the Official MCP SDK to implement the MCP server within the existing FastAPI backend. This ensures standardization and compatibility with AI agents that expect MCP tools.

**Alternatives considered**:
- Custom protocol implementation: Would not be compatible with standard AI agents
- Third-party MCP libraries: Might not follow the official specification
- Direct database access: Violates the MCP tool requirement

### MCP Server Integration Approach

### Decision: Embed MCP Server within FastAPI Application
**Rationale**: The specification requires integrating the MCP server within the existing FastAPI backend without creating a separate service. This approach ensures no breaking changes to existing APIs while providing the required MCP functionality.

**Alternatives considered**:
- Separate MCP server process: Would require new deployment considerations
- Standalone MCP service: Would break the requirement of integration within existing backend
- Middleware approach: Doesn't properly separate concerns for MCP tools

## Task Model and CRUD Logic Analysis

### Decision: Reuse Existing Task Model and SQLModel Layer
**Rationale**: The existing task model in `/backend/src/models/task.py` already contains the required fields and relationships for task management. Reusing the model ensures consistency and leverages existing validation and business logic.

**Key findings**:
- Task model has proper user_id field for isolation
- Includes proper timestamps (created_at, updated_at, completed_at)
- Status field supports completion operations
- Priority and due_date fields for enhanced task management

### Decision: Leverage Existing CRUD Functions from API Routes
**Rationale**: The existing API routes in `/backend/src/api/routes/tasks.py` already implement the required operations (add, list, update, complete, delete). These can be extracted and reused in the MCP tool handlers to ensure consistency and reduce duplication.

**Operations identified**:
- add_task: Create task functionality (POST /tasks)
- list_tasks: Get tasks functionality (GET /tasks)
- update_task: Update task functionality (PUT /tasks/{task_id})
- complete_task: Toggle completion functionality (PATCH /tasks/{task_id}/complete)
- delete_task: Delete task functionality (DELETE /tasks/{task_id})

## User Isolation Strategy

### Decision: Use Existing Better Auth Integration
**Rationale**: The existing authentication middleware in `/backend/src/middleware/auth.py` already provides user ID extraction and verification. The MCP tools will leverage this same mechanism to enforce user isolation.

**Key points**:
- Authentication function `get_current_user_id()` returns user ID as string
- User isolation is already enforced in existing API routes using `user_id` field
- The same pattern can be applied to MCP tools for consistent security

## Database Access Patterns

### Decision: Use Existing SQLModel Session Management
**Rationale**: The existing database layer in `/backend/src/database/database.py` provides AsyncSession management. MCP tools will use the same session pattern to ensure consistency and proper transaction handling.

**Implementation approach**:
- Each tool handler will accept a database session parameter
- Use existing select statements and session operations
- Follow the same error handling patterns as existing routes

## Statelessness Requirements

### Decision: Stateless Tool Implementation
**Rationale**: The constitution and specification require MCP tools to be stateless with no in-memory state. Each tool call will be a self-contained operation with no persistent state between calls.

**Implementation strategy**:
- Tools accept all required parameters explicitly
- No caching or session state maintained between calls
- Each tool performs its operation independently
- Authentication and user context passed explicitly to each tool

## Error Handling Approach

### Decision: Adopt Existing Error Handling Patterns
**Rationale**: The existing API routes use well-defined exception handling patterns defined in `/backend/src/exceptions.py`. MCP tools will follow the same patterns for consistency.

**Error handling for**:
- Invalid task IDs (Task not found)
- Unauthorized access (User isolation enforcement)
- Database operation failures
- Input validation errors