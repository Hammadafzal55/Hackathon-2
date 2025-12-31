"""
Unit tests for the Task model and operations.

Tests cover all 5 user stories:
- US1: Add Task
- US2: View Tasks
- US3: Update Task
- US4: Delete Task
- US5: Mark Complete/Incomplete
"""

import pytest
from src.models.task import (
    Task,
    add_task,
    view_tasks,
    update_task,
    delete_task,
    toggle_status,
    validate_title,
    clear_tasks,
    get_task,
)


@pytest.fixture(autouse=True)
def setup_teardown():
    """Clear tasks before and after each test."""
    clear_tasks()
    yield
    clear_tasks()


# =============================================================================
# User Story 1: Add Task Tests
# =============================================================================

class TestValidateTitle:
    """Tests for validate_title() function."""

    def test_valid_title_passes(self):
        """Valid non-empty title should not raise."""
        validate_title("Buy groceries")  # Should not raise

    def test_empty_title_raises(self):
        """Empty title should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_title("")

    def test_whitespace_only_title_raises(self):
        """Whitespace-only title should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_title("   ")

    def test_none_title_raises(self):
        """None title should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_title(None)


class TestAddTask:
    """Tests for add_task() function."""

    def test_add_task_with_title_only(self):
        """Add task with title only, description defaults to empty."""
        task = add_task("Buy groceries")

        assert task.task_id == 1
        assert task.title == "Buy groceries"
        assert task.description == ""
        assert task.status == "incomplete"

    def test_add_task_with_title_and_description(self):
        """Add task with both title and description."""
        task = add_task("Buy groceries", "Milk, eggs, bread")

        assert task.task_id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.status == "incomplete"

    def test_add_task_strips_whitespace(self):
        """Title and description should be stripped of leading/trailing whitespace."""
        task = add_task("  Buy groceries  ", "  Milk, eggs  ")

        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs"

    def test_add_task_sequential_ids(self):
        """Multiple tasks should have sequential IDs starting at 1."""
        task1 = add_task("Task 1")
        task2 = add_task("Task 2")
        task3 = add_task("Task 3")

        assert task1.task_id == 1
        assert task2.task_id == 2
        assert task3.task_id == 3

    def test_add_task_empty_title_raises(self):
        """Adding task with empty title should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            add_task("")

    def test_add_task_whitespace_title_raises(self):
        """Adding task with whitespace-only title should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            add_task("   ")


# =============================================================================
# User Story 2: View Tasks Tests
# =============================================================================

class TestViewTasks:
    """Tests for view_tasks() function."""

    def test_view_tasks_empty_list(self):
        """View tasks when list is empty returns empty list."""
        tasks = view_tasks()
        assert tasks == []

    def test_view_tasks_returns_all_tasks(self):
        """View tasks returns all added tasks."""
        add_task("Task 1")
        add_task("Task 2")
        add_task("Task 3")

        tasks = view_tasks()

        assert len(tasks) == 3
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"
        assert tasks[2].title == "Task 3"

    def test_view_tasks_returns_copy(self):
        """View tasks returns a copy, not the original list."""
        add_task("Task 1")
        tasks = view_tasks()
        tasks.clear()  # Modify the returned list

        # Original should still have the task
        assert len(view_tasks()) == 1


# =============================================================================
# User Story 3: Update Task Tests
# =============================================================================

class TestUpdateTask:
    """Tests for update_task() function."""

    def test_update_task_title(self):
        """Update only the task title."""
        add_task("Original Title", "Description")

        updated = update_task(1, title="New Title")

        assert updated.title == "New Title"
        assert updated.description == "Description"  # Unchanged

    def test_update_task_description(self):
        """Update only the task description."""
        add_task("Title", "Original Description")

        updated = update_task(1, description="New Description")

        assert updated.title == "Title"  # Unchanged
        assert updated.description == "New Description"

    def test_update_task_both_fields(self):
        """Update both title and description."""
        add_task("Original Title", "Original Description")

        updated = update_task(1, title="New Title", description="New Description")

        assert updated.title == "New Title"
        assert updated.description == "New Description"

    def test_update_task_strips_whitespace(self):
        """Updated title and description should be stripped."""
        add_task("Title", "Description")

        updated = update_task(1, title="  New Title  ", description="  New Desc  ")

        assert updated.title == "New Title"
        assert updated.description == "New Desc"

    def test_update_task_invalid_id_raises(self):
        """Updating non-existent task should raise IndexError."""
        add_task("Task 1")

        with pytest.raises(IndexError, match="not found"):
            update_task(99, title="New Title")

    def test_update_task_empty_title_raises(self):
        """Updating with empty title should raise ValueError."""
        add_task("Original Title")

        with pytest.raises(ValueError, match="cannot be empty"):
            update_task(1, title="")


# =============================================================================
# User Story 4: Delete Task Tests
# =============================================================================

class TestDeleteTask:
    """Tests for delete_task() function."""

    def test_delete_task_removes_from_list(self):
        """Delete task removes it from the list."""
        add_task("Task 1")
        add_task("Task 2")

        delete_task(1)

        tasks = view_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Task 2"

    def test_delete_task_reassigns_ids(self):
        """After deletion, IDs are reassigned sequentially."""
        add_task("Task 1")
        add_task("Task 2")
        add_task("Task 3")

        delete_task(2)  # Delete middle task

        tasks = view_tasks()
        assert tasks[0].task_id == 1
        assert tasks[0].title == "Task 1"
        assert tasks[1].task_id == 2  # Was 3, now reassigned to 2
        assert tasks[1].title == "Task 3"

    def test_delete_task_invalid_id_raises(self):
        """Deleting non-existent task should raise IndexError."""
        add_task("Task 1")

        with pytest.raises(IndexError, match="not found"):
            delete_task(99)

    def test_delete_task_returns_deleted_task(self):
        """Delete task returns the deleted task object."""
        add_task("Task to delete")

        deleted = delete_task(1)

        assert deleted.title == "Task to delete"


# =============================================================================
# User Story 5: Mark Complete/Incomplete Tests
# =============================================================================

class TestToggleStatus:
    """Tests for toggle_status() function."""

    def test_toggle_incomplete_to_complete(self):
        """Toggle incomplete task to complete."""
        add_task("Task 1")  # Default status is "incomplete"

        toggled = toggle_status(1)

        assert toggled.status == "complete"

    def test_toggle_complete_to_incomplete(self):
        """Toggle complete task back to incomplete."""
        add_task("Task 1")
        toggle_status(1)  # Now complete

        toggled = toggle_status(1)  # Toggle again

        assert toggled.status == "incomplete"

    def test_toggle_status_invalid_id_raises(self):
        """Toggling non-existent task should raise IndexError."""
        add_task("Task 1")

        with pytest.raises(IndexError, match="not found"):
            toggle_status(99)

    def test_toggle_preserves_other_fields(self):
        """Toggle status should not affect other task fields."""
        add_task("My Task", "My Description")

        toggled = toggle_status(1)

        assert toggled.title == "My Task"
        assert toggled.description == "My Description"
        assert toggled.task_id == 1


# =============================================================================
# Helper Function Tests
# =============================================================================

class TestGetTask:
    """Tests for get_task() helper function."""

    def test_get_task_valid_id(self):
        """Get task with valid ID returns the task."""
        add_task("Task 1")

        task = get_task(1)

        assert task.title == "Task 1"

    def test_get_task_invalid_id_raises(self):
        """Get task with invalid ID raises IndexError."""
        add_task("Task 1")

        with pytest.raises(IndexError, match="not found"):
            get_task(99)

    def test_get_task_zero_id_raises(self):
        """Get task with ID 0 raises IndexError."""
        add_task("Task 1")

        with pytest.raises(IndexError, match="not found"):
            get_task(0)

    def test_get_task_negative_id_raises(self):
        """Get task with negative ID raises IndexError."""
        add_task("Task 1")

        with pytest.raises(IndexError, match="not found"):
            get_task(-1)
