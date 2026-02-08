# Data Model: MCP Server + Task Tools Foundation

## Overview
This document describes the data models and schemas for the MCP task tools, building upon the existing task model in the system.

## Core Entities

### Task Entity (Reused from Existing Model)
**Description**: Represents a user's task with all the properties defined in the existing system.

**Fields**:
- `id`: UUID (Primary Key) - Unique identifier for the task
- `title`: String (Required, 1-255 chars) - Title of the task
- `description`: String (Optional, max 1000 chars) - Detailed description of the task
- `status`: String (Default: "pending", Enum: pending, in_progress, completed, cancelled) - Current status of the task
- `priority`: Integer (Default: 1, Range: 1-5) - Priority level (1 being lowest)
- `due_date`: DateTime (Optional) - Deadline for the task
- `user_id`: String (Required, Indexed) - ID of the user who owns the task
- `created_at`: DateTime (Required) - Timestamp when task was created
- `updated_at`: DateTime (Required) - Timestamp when task was last updated
- `completed_at`: DateTime (Optional) - Timestamp when task was completed

**Relationships**:
- Belongs to a User (via user_id field)

**Validation Rules**:
- Title must be 1-255 characters
- Description max 1000 characters
- Priority must be between 1-5
- Status must be one of the allowed values
- User_id must be valid and exist in the system

### MCP Tool Request Schema
**Description**: Base schema for all MCP tool requests that require authentication context.

**Fields**:
- `user_id`: String (Required) - The ID of the authenticated user making the request
- `auth_token`: String (Optional) - Authentication token (if needed for verification)

### Add Task Tool Schema
**Description**: Schema for the add_task MCP tool request.

**Fields**:
- `title`: String (Required, 1-255 chars) - Title of the task to create
- `description`: String (Optional, max 1000 chars) - Description of the task
- `priority`: Integer (Optional, 1-5, Default: 1) - Priority level
- `due_date`: String (Optional, ISO format) - Due date for the task
- `user_id`: String (Required) - ID of the user creating the task

**Response**:
- `task_id`: UUID - ID of the created task
- `message`: String - Success message
- `task`: Task object - The created task data

### List Tasks Tool Schema
**Description**: Schema for the list_tasks MCP tool request.

**Fields**:
- `user_id`: String (Required) - ID of the user whose tasks to list
- `status_filter`: String (Optional) - Filter tasks by status
- `limit`: Integer (Optional) - Maximum number of tasks to return
- `offset`: Integer (Optional) - Offset for pagination

**Response**:
- `tasks`: Array of Task objects - List of user's tasks
- `total_count`: Integer - Total number of tasks matching criteria

### Update Task Tool Schema
**Description**: Schema for the update_task MCP tool request.

**Fields**:
- `task_id`: UUID (Required) - ID of the task to update
- `user_id`: String (Required) - ID of the user requesting the update
- `title`: String (Optional, 1-255 chars) - New title for the task
- `description`: String (Optional, max 1000 chars) - New description
- `status`: String (Optional, Enum values) - New status
- `priority`: Integer (Optional, 1-5) - New priority
- `due_date`: String (Optional, ISO format) - New due date

**Response**:
- `task_id`: UUID - ID of the updated task
- `message`: String - Success message
- `task`: Task object - The updated task data

### Complete Task Tool Schema
**Description**: Schema for the complete_task MCP tool request (toggles completion status).

**Fields**:
- `task_id`: UUID (Required) - ID of the task to toggle completion
- `user_id`: String (Required) - ID of the user requesting the change
- `complete`: Boolean (Optional, Default: true) - Whether to complete or uncomplete the task

**Response**:
- `task_id`: UUID - ID of the task that had its completion status changed
- `message`: String - Success message
- `task`: Task object - The task with updated completion status

### Delete Task Tool Schema
**Description**: Schema for the delete_task MCP tool request.

**Fields**:
- `task_id`: UUID (Required) - ID of the task to delete
- `user_id`: String (Required) - ID of the user requesting deletion

**Response**:
- `task_id`: UUID - ID of the deleted task
- `message`: String - Success message

## State Transitions

### Task Status Transitions
Tasks can transition between statuses as follows:
- `pending` → `in_progress`, `completed`, `cancelled`
- `in_progress` → `pending`, `completed`, `cancelled`
- `completed` → `pending`, `in_progress`, `cancelled`
- `cancelled` → `pending`, `in_progress`

### Completion State Transitions
- When status changes to `completed`: `completed_at` field is set to current timestamp
- When status changes from `completed` to any other status: `completed_at` field is cleared to null

## Validation Rules

### Cross-Field Validation
- `due_date` should not be in the past when setting status to `completed` (warning only)
- `priority` must be between 1 and 5 (inclusive)
- `user_id` must match the authenticated user context

### Business Rules
- Users can only operate on tasks they own (enforced by user_id check)
- Completed tasks cannot be modified except to change status back to incomplete
- Tasks with past due dates can still be updated