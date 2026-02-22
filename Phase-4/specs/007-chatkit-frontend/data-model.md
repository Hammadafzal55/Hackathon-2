# Data Model: ChatKit Frontend Integration & Agent UI

**Feature**: 007-chatkit-frontend
**Date**: 2026-02-11

---

## Overview

**No new database models are required.** ChatKit manages conversation threads via OpenAI's Threads API. The frontend interacts with existing backend task tables only.

## Existing Entities Consumed (no changes)

### Task (from spec 001 — read/write via tool calls)
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| title | string | Task title |
| description | string | Task description (nullable) |
| status | string | "pending", "in_progress", "completed", "cancelled" |
| priority | integer | 1-5 priority level |
| user_id | UUID | Owner (from JWT) |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |
| completed_at | datetime | Completion timestamp (nullable) |
| due_date | date | Due date (nullable) |

### Conversation / Message (from spec 006 — NOT used by ChatKit)

The spec 006 Conversation and Message tables remain in the database but are not used by the ChatKit frontend. They continue to serve the API-only chat endpoint (`POST /api/chat`).

## Frontend-Only State

### ChatKit Internal State (managed by ChatKit + OpenAI)
| Concept | Managed By | Description |
|---------|------------|-------------|
| Thread | OpenAI Threads API | Conversation container with message history |
| Messages | ChatKit | User and assistant messages within a thread |
| Tool calls | ChatKit | Tool invocations and results |

### Local Persistence (localStorage)
| Key | Type | Description |
|-----|------|-------------|
| `chatkit-active-thread` | string (thread ID) or empty | Persists active conversation across page refresh |

## OpenAI Assistant Configuration (external, not in code)

An OpenAI Assistant must be configured on OpenAI's platform with these tools:

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `add_task` | Create a new task | title (required), description, priority |
| `list_tasks` | List the user's tasks | (none) |
| `update_task` | Update an existing task | task_id (required), title, description, priority, status |
| `complete_task` | Toggle task completion | task_id (required) |
| `delete_task` | Delete a task | task_id (required) |
