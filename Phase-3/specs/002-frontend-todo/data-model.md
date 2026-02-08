# Data Model: Todo Frontend Application

## Entity Definitions

### Task
**Description**: Represents a user's todo item displayed in the UI with properties like title, description, completion status, priority, and due date

**Fields**:
- `id`: UUID - Unique identifier for the task (string format)
- `title`: string - Task title (required, 1-255 characters)
- `description`: string | null - Task description (optional, up to 1000 characters)
- `status`: string - Task status (pending, in_progress, completed, cancelled)
- `priority`: number - Task priority level (1-5, 1 being lowest)
- `due_date`: string | null - Due date in ISO format (optional)
- `user_id`: UUID - Associated user identifier (string format)
- `created_at`: string - Creation timestamp in ISO format
- `updated_at`: string - Last update timestamp in ISO format
- `completed_at`: string | null - Completion timestamp in ISO format (when status is completed)

**Validation Rules**:
- `title` is required and must be 1-255 characters
- `description` is optional and limited to 1000 characters
- `status` must be one of: "pending", "in_progress", "completed", "cancelled"
- `priority` must be an integer between 1 and 5
- `due_date` must be a valid ISO 8601 date string if provided
- `id` and `user_id` must be valid UUID format

**State Transitions**:
- Status can transition from any state to any other state
- When status changes to "completed", `completed_at` is set to current timestamp
- When status changes from "completed" to any other state, `completed_at` is set to null

### TaskList
**Description**: Collection of tasks managed by the frontend that reflects the backend state

**Fields**:
- `tasks`: Array<Task> - List of tasks
- `loading`: boolean - Whether data is currently loading
- `error`: string | null - Error message if operation failed
- `filter`: string | null - Current filter applied (all, completed, pending)
- `sort`: string - Current sort order (by date, priority, etc.)

## API Data Structures

### TaskCreate
**Description**: Data structure for creating a new task

**Fields**:
- `title`: string - Task title (required)
- `description`: string | null - Task description (optional)
- `priority`: number - Task priority (1-5, default 1)
- `due_date`: string | null - Due date in ISO format (optional)
- `status`: string - Initial status (default "pending")

### TaskUpdate
**Description**: Data structure for updating an existing task

**Fields**:
- `title`: string | null - Updated title (optional)
- `description`: string | null - Updated description (optional)
- `status`: string | null - Updated status (optional)
- `priority`: number | null - Updated priority (optional)
- `due_date`: string | null - Updated due date (optional)

## Frontend State Objects

### TaskFormData
**Description**: Form data structure for task creation/editing UI

**Fields**:
- `title`: string - Current title value
- `description`: string - Current description value
- `priority`: number - Current priority value
- `due_date`: string - Current due date value (as date string)
- `errors`: Object - Validation errors for each field

### ApiResponse<T>
**Description**: Generic structure for API responses

**Fields**:
- `data`: T | null - Response data if successful
- `error`: string | null - Error message if failed
- `success`: boolean - Whether the request was successful