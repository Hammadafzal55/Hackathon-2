# API Client Library

This directory contains the API client module for interacting with the Todo backend API.

## Overview

The API client provides a set of functions to interact with the Todo backend API, including:

- Fetching all tasks for a user
- Creating new tasks
- Updating existing tasks
- Deleting tasks
- Toggling task completion status

## Files

- `api.ts`: Main API client implementation with all CRUD operations
- `index.ts`: Export file that exposes the API client and related types

## Usage

```typescript
import { apiClient, fetchTasks, createTask, updateTask, deleteTask, toggleTaskCompletion } from '@/lib';

// Fetch all tasks for a user
const tasks = await fetchTasks('user-id');

// Create a new task
const newTask = await createTask('user-id', { title: 'New task', description: 'Task description' });

// Update a task
const updatedTask = await updateTask('user-id', 'task-id', { title: 'Updated title', completed: true });

// Delete a task
await deleteTask('user-id', 'task-id');

// Toggle task completion
const toggledTask = await toggleTaskCompletion('user-id', 'task-id');
```

## Environment Variables

The API client uses the following environment variable:

- `NEXT_PUBLIC_API_URL`: The base URL for the API (defaults to `http://localhost:8000`)

## Authentication

The API client automatically includes the JWT token from `localStorage` in the `Authorization` header if available.

## Error Handling

The API client throws `ApiError` instances when API requests fail, containing the status code and response information.