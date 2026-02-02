# Data Model: Todo Backend Service

## Entities

### Task
Represents a user's todo item with properties such as ID, title, description, completion status, and user association.

**Fields**:
- `id`: Integer (Primary Key, Auto-generated)
- `title`: String (Required, Max length: 255)
- `description`: String (Optional, Max length: 1000)
- `completed`: Boolean (Default: False)
- `user_id`: Integer (Foreign Key reference to User)
- `created_at`: DateTime (Auto-generated timestamp)
- `updated_at`: DateTime (Auto-generated timestamp, updated on change)

**Validation rules**:
- Title must be between 1 and 255 characters
- Description can be empty or up to 1000 characters
- Completed defaults to False when creating a new task
- user_id is required and must reference an existing user

**State transitions**:
- `incomplete` → `completed` (when PATCH /api/{user_id}/tasks/{id}/complete is called on an incomplete task)
- `completed` → `incomplete` (when PATCH /api/{user_id}/tasks/{id}/complete is called on a completed task)

### User
Represents the owner of tasks with an identifier that associates tasks to the correct user.

**Fields**:
- `id`: Integer (Primary Key, Auto-generated)
- `user_id`: String/Integer (Unique identifier for the user)
- `created_at`: DateTime (Auto-generated timestamp)

**Relationships**:
- One User to Many Tasks (One-to-Many relationship)

## Database Schema

### tasks table
```
id: INTEGER (PRIMARY KEY, AUTO_INCREMENT)
title: VARCHAR(255) NOT NULL
description: TEXT (NULLABLE)
completed: BOOLEAN DEFAULT FALSE
user_id: INTEGER NOT NULL (FOREIGN KEY REFERENCES users(id))
created_at: TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
updated_at: TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

### users table
```
id: INTEGER (PRIMARY KEY, AUTO_INCREMENT)
user_id: VARCHAR(255) UNIQUE NOT NULL
created_at: TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
```

## Indexes
- Index on `user_id` in tasks table for efficient filtering
- Index on `completed` in tasks table for efficient querying by completion status
- Unique index on `user_id` in users table