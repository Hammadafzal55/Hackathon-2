"""
Unit tests for CLI command handlers.

Tests cover all command handlers for the 5 user stories.
"""

import pytest
from io import StringIO
import sys

from src.cli.handlers import (
    cmd_add,
    cmd_view,
    cmd_update,
    cmd_delete,
    cmd_complete,
)
from src.models.task import clear_tasks, view_tasks


@pytest.fixture(autouse=True)
def setup_teardown():
    """Clear tasks before and after each test."""
    clear_tasks()
    yield
    clear_tasks()


def capture_output(func, *args):
    """Helper to capture stdout output from a function."""
    captured = StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        func(*args)
    finally:
        sys.stdout = old_stdout
    return captured.getvalue()


# =============================================================================
# cmd_add Tests
# =============================================================================

class TestCmdAdd:
    """Tests for cmd_add() CLI handler."""

    def test_add_with_title_only(self):
        """Add task with title only."""
        output = capture_output(cmd_add, ["Buy groceries"])

        assert "Task added successfully" in output
        assert "ID: 1" in output
        tasks = view_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Buy groceries"

    def test_add_with_description_flag(self):
        """Add task with --description flag."""
        output = capture_output(cmd_add, ["Buy groceries", "--description", "Milk and eggs"])

        assert "Task added successfully" in output
        tasks = view_tasks()
        assert tasks[0].description == "Milk and eggs"

    def test_add_with_short_description_flag(self):
        """Add task with -d flag."""
        output = capture_output(cmd_add, ["Buy groceries", "-d", "Milk and eggs"])

        tasks = view_tasks()
        assert tasks[0].description == "Milk and eggs"

    def test_add_multiple_word_title(self):
        """Add task with multi-word title (no quotes in CLI)."""
        output = capture_output(cmd_add, ["Buy", "groceries", "today"])

        tasks = view_tasks()
        assert tasks[0].title == "Buy groceries today"

    def test_add_no_args_raises(self):
        """Add with no arguments should raise ValueError."""
        with pytest.raises(ValueError, match="title is required"):
            cmd_add([])

    def test_add_description_flag_without_value_raises(self):
        """Add with --description but no value should raise ValueError."""
        with pytest.raises(ValueError, match="--description requires a value"):
            cmd_add(["Title", "--description"])


# =============================================================================
# cmd_view Tests
# =============================================================================

class TestCmdView:
    """Tests for cmd_view() CLI handler."""

    def test_view_empty_list(self):
        """View with no tasks shows friendly message."""
        output = capture_output(cmd_view, [])

        assert "No tasks found" in output

    def test_view_with_tasks(self):
        """View displays all tasks."""
        cmd_add(["Task 1"])
        cmd_add(["Task 2", "--description", "Description 2"])

        output = capture_output(cmd_view, [])

        assert "[1]" in output
        assert "Task 1" in output
        assert "[2]" in output
        assert "Task 2" in output
        assert "Description 2" in output

    def test_view_shows_status(self):
        """View shows task status."""
        cmd_add(["Task 1"])

        output = capture_output(cmd_view, [])

        assert "[incomplete]" in output


# =============================================================================
# cmd_update Tests
# =============================================================================

class TestCmdUpdate:
    """Tests for cmd_update() CLI handler."""

    def test_update_title(self):
        """Update task title."""
        cmd_add(["Original Title"])

        output = capture_output(cmd_update, ["1", "--title", "New Title"])

        assert "updated successfully" in output
        tasks = view_tasks()
        assert tasks[0].title == "New Title"

    def test_update_description(self):
        """Update task description."""
        cmd_add(["Title", "--description", "Original"])

        output = capture_output(cmd_update, ["1", "--description", "New Description"])

        tasks = view_tasks()
        assert tasks[0].description == "New Description"

    def test_update_both_fields(self):
        """Update both title and description."""
        cmd_add(["Original"])

        capture_output(cmd_update, ["1", "--title", "New", "--description", "Desc"])

        tasks = view_tasks()
        assert tasks[0].title == "New"
        assert tasks[0].description == "Desc"

    def test_update_no_task_id_raises(self):
        """Update without task ID should raise ValueError."""
        with pytest.raises(ValueError, match="Task ID is required"):
            cmd_update([])

    def test_update_invalid_id_raises(self):
        """Update with invalid ID should raise ValueError."""
        with pytest.raises(ValueError, match="must be a number"):
            cmd_update(["abc"])

    def test_update_no_fields_raises(self):
        """Update with no fields to update should raise ValueError."""
        cmd_add(["Title"])

        with pytest.raises(ValueError, match="At least one"):
            cmd_update(["1"])


# =============================================================================
# cmd_delete Tests
# =============================================================================

class TestCmdDelete:
    """Tests for cmd_delete() CLI handler."""

    def test_delete_task(self):
        """Delete task removes it from list."""
        cmd_add(["Task 1"])
        cmd_add(["Task 2"])

        output = capture_output(cmd_delete, ["1"])

        assert "deleted successfully" in output
        tasks = view_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Task 2"

    def test_delete_no_task_id_raises(self):
        """Delete without task ID should raise ValueError."""
        with pytest.raises(ValueError, match="Task ID is required"):
            cmd_delete([])

    def test_delete_invalid_id_raises(self):
        """Delete with invalid ID should raise ValueError."""
        with pytest.raises(ValueError, match="must be a number"):
            cmd_delete(["abc"])


# =============================================================================
# cmd_complete Tests
# =============================================================================

class TestCmdComplete:
    """Tests for cmd_complete() CLI handler."""

    def test_complete_toggles_to_complete(self):
        """Complete toggles status to complete."""
        cmd_add(["Task 1"])

        output = capture_output(cmd_complete, ["1"])

        assert "marked as complete" in output
        tasks = view_tasks()
        assert tasks[0].status == "complete"

    def test_complete_toggles_back_to_incomplete(self):
        """Complete toggles back to incomplete."""
        cmd_add(["Task 1"])
        cmd_complete(["1"])  # Now complete

        output = capture_output(cmd_complete, ["1"])

        assert "marked as incomplete" in output
        tasks = view_tasks()
        assert tasks[0].status == "incomplete"

    def test_complete_no_task_id_raises(self):
        """Complete without task ID should raise ValueError."""
        with pytest.raises(ValueError, match="Task ID is required"):
            cmd_complete([])

    def test_complete_invalid_id_raises(self):
        """Complete with invalid ID should raise ValueError."""
        with pytest.raises(ValueError, match="must be a number"):
            cmd_complete(["abc"])
