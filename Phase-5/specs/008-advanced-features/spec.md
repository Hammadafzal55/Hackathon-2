# Feature Specification: Advanced Features — Recurring Tasks, Reminders, Tags, Search/Filter/Sort & Event-Driven Architecture

**Feature Branch**: `008-advanced-features`
**Created**: 2026-03-05
**Status**: Draft
**Input**: User description: "Part A: Advanced Features — Implement all Advanced Level features (Recurring Tasks, Due Dates & Reminders), Implement Intermediate Level features (Priorities, Tags, Search, Filter, Sort), Add event-driven architecture with Kafka, Implement Dapr for distributed application runtime"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Create a Recurring Task (Priority: P1)

An authenticated user wants to create a task that repeats automatically on a schedule. They set the task title, description, priority, and choose a recurrence pattern (daily, weekly, monthly, or a custom interval). Once saved, the system automatically creates a new instance of the task each time the previous one is due, so the user never has to manually recreate repeating obligations.

**Why this priority**: Recurring tasks are the most requested advanced feature in task management. Without it, users must manually recreate tasks every cycle — the most direct productivity pain point. It also exercises the event-driven scheduling architecture end-to-end.

**Independent Test**: Can be tested by creating a daily recurring task, advancing the simulated clock by one day, and verifying a new task instance appears automatically.

**Acceptance Scenarios**:

1. **Given** an authenticated user on the task creation form, **When** they enable recurrence and select "weekly" with a start date, **Then** the task is saved with a recurrence schedule and appears in their task list with a visual recurrence indicator.
2. **Given** a recurring task whose due date has passed, **When** the scheduled recurrence trigger fires, **Then** a new task instance is automatically created with the next due date calculated from the recurrence pattern.
3. **Given** a recurring task, **When** the user marks the current instance as complete, **Then** the completed instance is preserved in history and the next instance is scheduled according to the recurrence rule.
4. **Given** a recurring task, **When** the user chooses to stop recurrence, **Then** no further instances are generated and existing instances remain unaffected.

---

### User Story 2 — Receive a Due Date Reminder (Priority: P1)

An authenticated user sets a due date and a reminder window (e.g., "remind me 1 hour before", "remind me 1 day before") on any task. At the specified time before the due date, the system delivers a visible in-app notification alerting the user that the task is approaching its deadline.

**Why this priority**: Reminders transform due dates from passive labels into active accountability tools. Without reminders, due dates are informational only and fail to drive user action. This is the single biggest differentiator between a basic and a useful task manager.

**Independent Test**: Can be tested by creating a task with a near-future due date and a short reminder window, waiting for the trigger time, and verifying a notification appears in the application.

**Acceptance Scenarios**:

1. **Given** a user creates a task with a due date and selects "remind me 1 day before," **When** the reminder time is reached, **Then** a notification badge or alert appears in the application indicating the upcoming task.
2. **Given** a task with an active reminder, **When** the user marks the task as complete before the reminder fires, **Then** the reminder is automatically cancelled and no notification is sent.
3. **Given** the user is not actively using the application when a reminder fires, **When** they next open the application, **Then** the notification is visible in an unread notifications list.
4. **Given** a task has multiple reminders set, **When** each reminder time arrives, **Then** each reminder fires independently in the correct order.

---

### User Story 3 — Organize Tasks with Tags (Priority: P2)

An authenticated user can attach one or more tags (short labels such as "work", "personal", "urgent", "shopping") to any task. Tags allow the user to group and categorize tasks across different projects or contexts without a rigid folder structure.

**Why this priority**: Tags provide flexible, lightweight organization that complements priorities and statuses. They enable cross-cutting categorization (e.g., all "urgent" tasks regardless of project) that cannot be achieved with status or priority alone.

**Independent Test**: Can be tested by creating tasks with various tags, then filtering the task list by a specific tag and verifying only tagged tasks appear.

**Acceptance Scenarios**:

1. **Given** a user is creating or editing a task, **When** they type a tag name and confirm it, **Then** the tag is attached to the task and displayed as a visible label on the task card.
2. **Given** a user has tasks with multiple tags, **When** they select a tag to filter by, **Then** only tasks containing that tag are shown in the task list.
3. **Given** a task has tags, **When** the user removes a tag from the task, **Then** the tag is removed from that task only and other tasks retain their tags.
4. **Given** a user has created tags across many tasks, **When** they open the tag filter, **Then** a list of all their existing tags is presented for selection.

---

### User Story 4 — Search, Filter, and Sort Tasks (Priority: P2)

An authenticated user can quickly find specific tasks using a search bar (which searches across task title, description, and tags), filter the list by one or more criteria (status, priority level, tag, due date range), and sort the results by their preferred ordering (due date, priority, creation date, or alphabetical).

**Why this priority**: As the number of tasks grows, discoverability becomes critical. Search, filter, and sort together form the core task navigation experience and are essential for any user managing more than a handful of tasks.

**Independent Test**: Can be tested by populating a list with 20+ diverse tasks, then applying a search term combined with a filter and verifying the correct subset of tasks appears in the specified order.

**Acceptance Scenarios**:

1. **Given** a user types a keyword in the search bar, **When** the search executes, **Then** only tasks whose title, description, or tags contain the keyword are displayed, and results appear within 1 second.
2. **Given** a user applies a priority filter (e.g., "High Priority only"), **When** the filter is active, **Then** only tasks matching that priority are shown and the active filter is visually indicated.
3. **Given** a user selects "Sort by Due Date (ascending)", **When** the sort is applied, **Then** tasks are ordered from soonest to latest due date, with tasks having no due date appearing last.
4. **Given** a user combines a search term with a status filter and a sort preference, **When** the combination is applied, **Then** the result shows only tasks matching both the search and filter, ordered by the chosen sort.
5. **Given** a user clears all filters, **When** the reset action is taken, **Then** the full unfiltered task list is restored.

---

### User Story 5 — Task Events Are Processed Reliably (Priority: P3)

When a user creates, updates, completes, or deletes a task, the system internally publishes a structured event describing what happened. Background processes subscribe to these events to trigger downstream actions such as scheduling reminders, generating recurring task instances, and updating derived data — all without the user needing to wait for these operations to complete.

**Why this priority**: The event-driven architecture is the infrastructure layer that makes recurring tasks and reminders reliable and decoupled from the main user interaction. It is not directly visible to the user but is required for the other stories to work correctly at scale. It is P3 because users experience its effects through P1 and P2 stories.

**Independent Test**: Can be tested by creating a task with a reminder and verifying the reminder fires without the user re-submitting any form — confirming background processing occurred.

**Acceptance Scenarios**:

1. **Given** a user creates a task with a due date and reminder, **When** the task is saved, **Then** the system internally records a reminder event and schedules it for future delivery without any additional user action.
2. **Given** a recurring task's due date passes, **When** the scheduled event fires, **Then** a new task instance is created automatically and the user sees it in their task list on their next visit.
3. **Given** a high volume of task events is generated (e.g., 100 tasks created simultaneously), **When** the events are processed, **Then** all reminders and recurrence triggers are executed without loss or duplication.
4. **Given** the event processing system experiences a temporary outage, **When** it recovers, **Then** unprocessed events are retried and eventually delivered without manual intervention.

---

### Edge Cases

- What happens when a recurring task's next due date falls on a day the recurrence pattern skips (e.g., monthly task on the 31st in a month with 30 days)? The system should adjust to the last valid day of that month.
- What happens when a user deletes a task that has pending reminders? All pending reminders for that task must be cancelled immediately.
- What happens when two recurrence events fire for the same task simultaneously? The system must be idempotent — only one new instance should be created.
- What happens when a user searches with an empty string? The full unfiltered list should be displayed (no results should not appear for empty search).
- What happens when a user adds a tag that already exists on the same task? The tag should not be duplicated.
- What happens when a reminder is set for a task whose due date is in the past? The system should warn the user that the reminder time has already passed and prevent saving.
- What happens when the task list contains thousands of entries and a filter is applied? Results must appear within a reasonable time (under 2 seconds) regardless of total task count.
- What happens when a user applies conflicting filters (e.g., status = completed AND status = pending simultaneously)? The system should treat these as an OR (show tasks matching any selected status) or prevent conflicting single-value filters.

---

## Requirements *(mandatory)*

### Functional Requirements

**Recurring Tasks**

- **FR-001**: System MUST allow users to mark any task as recurring when creating or editing it.
- **FR-002**: System MUST support the following recurrence patterns: daily, weekly, monthly, and yearly.
- **FR-003**: System MUST automatically create a new task instance when a recurring task's due date passes, using the next calculated date from the recurrence pattern.
- **FR-004**: System MUST display a visual indicator on task cards that have an active recurrence schedule.
- **FR-005**: System MUST allow users to stop recurrence on a recurring task without deleting existing instances.
- **FR-006**: System MUST allow users to edit the recurrence pattern of an existing recurring task; changes must apply to all future instances only.

**Due Date Reminders**

- **FR-007**: System MUST allow users to set one or more reminders on any task that has a due date.
- **FR-008**: System MUST support reminder lead times of: 15 minutes, 1 hour, 3 hours, 1 day, and 2 days before the due date.
- **FR-009**: System MUST deliver in-app notifications when a reminder fires, visible as a notification badge and accessible through a notification panel.
- **FR-010**: System MUST automatically cancel all pending reminders for a task when that task is marked as complete or deleted.
- **FR-011**: System MUST preserve unread notifications in a notification history so users can view them after they next open the application.

**Tags**

- **FR-012**: System MUST allow users to add one or more free-text tags to any task.
- **FR-013**: System MUST display tags as visible labels on task cards in all list views.
- **FR-014**: System MUST allow users to remove individual tags from a task without affecting other tasks.
- **FR-015**: System MUST provide tag auto-complete suggestions based on tags the user has previously used when typing a new tag.

**Search**

- **FR-016**: System MUST provide a search input that filters the task list in real time as the user types.
- **FR-017**: Search MUST match against task title, description, and tags.
- **FR-018**: Search results MUST be returned within 1 second for any task list up to 10,000 tasks.
- **FR-019**: System MUST highlight the matching search term within displayed task titles and descriptions.

**Filter**

- **FR-020**: System MUST allow users to filter tasks by one or more of: status, priority level, tag, due date range (before / after / between specific dates).
- **FR-021**: System MUST allow multiple filters to be active simultaneously and combine them with AND logic.
- **FR-022**: System MUST display a clear visual indicator when one or more filters are active.
- **FR-023**: System MUST provide a single-action "Clear all filters" control.

**Sort**

- **FR-024**: System MUST allow users to sort the task list by: due date (ascending/descending), priority (highest/lowest first), creation date (newest/oldest first), and title (alphabetical A–Z / Z–A).
- **FR-025**: System MUST apply the selected sort to the currently filtered/searched result set (not the full list).
- **FR-026**: System MUST persist the user's sort preference for the duration of their session.

**Event-Driven Architecture**

- **FR-027**: System MUST publish a structured event to the event bus whenever a task is created, updated, completed, or deleted.
- **FR-028**: System MUST have a dedicated event consumer responsible for scheduling and firing reminders based on task reminder events.
- **FR-029**: System MUST have a dedicated event consumer responsible for generating new recurring task instances based on recurrence events.
- **FR-030**: Event consumers MUST process events in a reliable, at-least-once manner with idempotency guarantees to prevent duplicate task creation or duplicate reminder delivery.
- **FR-031**: System MUST expose a distributed application runtime (Dapr) sidecar for service invocation, pub/sub messaging, state management, secret retrieval, and cron-based bindings.

### Key Entities

- **Task**: The primary unit of work. Attributes include title, description, status, priority (1–5 scale with named levels: Low, Medium, High, Critical), due date, completion timestamp, recurrence schedule (optional), and tags (zero or more string labels).
- **RecurrenceRule**: Defines how a recurring task repeats. Attributes: pattern (daily / weekly / monthly / yearly), interval (every N occurrences of the pattern), start date, end condition (indefinite, after N occurrences, or by a specific date).
- **Reminder**: A scheduled notification tied to a task. Attributes: task reference, lead time (how far before due date), status (pending / sent / cancelled), scheduled delivery time.
- **Notification**: An in-app alert delivered to the user. Attributes: message, task reference, delivery timestamp, read/unread status.
- **Tag**: A short free-text label. Scoped to the owning user. Multiple tasks can share the same tag string.
- **TaskEvent**: A structured record of something that happened to a task (created, updated, completed, deleted). Published to the event bus for asynchronous processing. Attributes: event type, task ID, user ID, timestamp, relevant changed fields.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a recurring task in under 60 seconds from opening the task form to saving.
- **SC-002**: 100% of scheduled reminders fire within 5 minutes of their target delivery time under normal operating conditions.
- **SC-003**: Recurring task instances are created within 5 minutes of their scheduled recurrence trigger time.
- **SC-004**: Search results across a task list of up to 10,000 items are displayed in under 1 second.
- **SC-005**: Filter and sort operations on any task list are applied and reflected in the UI in under 500 milliseconds.
- **SC-006**: Zero duplicate recurring task instances are created even when recurrence triggers fire concurrently.
- **SC-007**: Zero reminder notifications are delivered for tasks that have been completed or deleted.
- **SC-008**: Users can apply a search + filter + sort combination and see correctly narrowed, ordered results with no missing or extra tasks.
- **SC-009**: The system recovers from a temporary event processing outage and delivers all queued reminders and recurrence events without manual intervention within 10 minutes of recovery.
- **SC-010**: Users can tag, search, filter, and sort tasks entirely through the existing task management interface without navigating to a separate page or tool.

---

## Scope

### In Scope

- Recurring task creation, management, and automatic instance generation
- In-app reminder notifications with configurable lead times
- Tags on tasks with auto-complete and filter support
- Full-text search across title, description, and tags
- Multi-criteria filtering (status, priority, tag, due date range)
- Multi-field sorting with session persistence
- Event publishing for all task lifecycle events
- Asynchronous event consumers for reminders and recurrence
- Distributed application runtime sidecar integration for pub/sub, state, secrets, cron bindings, and service invocation

### Out of Scope

- Email, SMS, or push notification delivery (in-app notifications only)
- Shared or collaborative tasks (tasks remain single-user)
- Subtasks or task hierarchies
- Drag-and-drop task reordering
- Calendar view or Gantt chart
- Natural language due date parsing (e.g., typing "tomorrow")
- Third-party calendar integration (Google Calendar, Outlook)
- Mobile native app notifications

---

## Dependencies

- Existing task management backend and database must be operational
- Existing user authentication system must issue valid tokens for all event consumers to identify task owners
- A message broker (event bus) must be accessible for publishing and consuming task events
- The application runtime sidecar must be co-deployed alongside the backend service

---

## Assumptions

- Reminder delivery is in-app only; no external notification channel (email, SMS, push) is required for this iteration.
- Tags are free-text strings scoped to the owning user; no global or shared tag taxonomy is required.
- Recurrence patterns cover daily, weekly, monthly, and yearly; custom cron expressions are not exposed to end users in this iteration.
- The reminder lead time options are fixed (15 min, 1 hr, 3 hr, 1 day, 2 days); users cannot enter arbitrary lead times.
- Search is substring/keyword-based; fuzzy matching and relevance ranking are not required.
- Multiple filters combine with AND logic (a task must match all active filters to appear).
- The event bus and runtime sidecar are infrastructure concerns handled during the deployment phase; this spec describes the application-level behavior only.
- Priority labels map to the existing 1–5 integer scale: 1 = Low, 2 = Medium-Low, 3 = Medium, 4 = High, 5 = Critical.
- Notifications are scoped to the current user's session; cross-device notification sync is not required.

---

## Risks

- **Reminder timing accuracy**: In-app reminders depend on the event processing system being healthy. If the consumer is delayed, reminders may arrive late. Mitigation: implement a catch-up query on application load to surface any missed reminders.
- **Recurrence complexity at edge dates**: Monthly recurrence on dates like the 29th–31st requires careful handling for months with fewer days. Mitigation: define a clear rule (use last day of month when target date does not exist) and test against all edge months.
- **Event volume at scale**: High task creation rates could flood the event bus. Mitigation: ensure consumers are horizontally scalable and the event bus supports back-pressure or consumer group partitioning.
