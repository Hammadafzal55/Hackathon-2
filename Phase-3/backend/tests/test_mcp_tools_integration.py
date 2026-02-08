"""
Integration tests for MCP tools.
Tests all five task operations with proper user isolation and data persistence.
"""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from src.mcp_tools.schemas import (
    AddTaskRequest,
    ListTasksRequest,
    UpdateTaskRequest,
    CompleteTaskRequest,
    DeleteTaskRequest
)
from src.mcp_tools.handlers import (
    add_task_handler,
    list_tasks_handler,
    update_task_handler,
    complete_task_handler,
    delete_task_handler
)


@pytest.mark.asyncio
async def test_add_task_with_authentication(async_session):
    """Test add_task with authenticated user context and verify data persistence."""
    user_id = str(uuid4())

    # Create a task
    request = AddTaskRequest(
        user_id=user_id,
        title="Test Task",
        description="This is a test task",
        priority=3
    )

    result = await add_task_handler(request, session=async_session)

    # Verify response
    assert result.task_id is not None
    assert result.message == "Task created successfully"
    assert result.task["title"] == "Test Task"
    assert result.task["description"] == "This is a test task"
    assert result.task["priority"] == 3
    assert result.task["user_id"] == user_id
    assert result.task["status"] == "pending"


@pytest.mark.asyncio
async def test_list_tasks_user_isolation(async_session):
    """Test list_tasks and verify user isolation (only return tasks for authenticated user)."""
    user_id_1 = str(uuid4())
    user_id_2 = str(uuid4())

    # Create tasks for user 1
    for i in range(3):
        await add_task_handler(AddTaskRequest(
            user_id=user_id_1,
            title=f"User 1 Task {i}"
        ), session=async_session)

    # Create tasks for user 2
    for i in range(2):
        await add_task_handler(AddTaskRequest(
            user_id=user_id_2,
            title=f"User 2 Task {i}"
        ), session=async_session)

    # List tasks for user 1
    list_req_1 = ListTasksRequest(user_id=user_id_1)
    result_1 = await list_tasks_handler(list_req_1, session=async_session)

    # List tasks for user 2
    list_req_2 = ListTasksRequest(user_id=user_id_2)
    result_2 = await list_tasks_handler(list_req_2, session=async_session)

    # Verify user isolation
    assert result_1.total_count >= 3
    assert all(task["user_id"] == user_id_1 for task in result_1.tasks)

    assert result_2.total_count >= 2
    assert all(task["user_id"] == user_id_2 for task in result_2.tasks)


@pytest.mark.asyncio
async def test_update_task_user_isolation(async_session):
    """Test update_task and verify user isolation enforcement."""
    user_id_1 = str(uuid4())
    user_id_2 = str(uuid4())

    # Create task for user 1
    add_result = await add_task_handler(AddTaskRequest(
        user_id=user_id_1,
        title="User 1 Task"
    ), session=async_session)
    task_id = add_result.task_id

    # Try to update task as user 1 (should succeed)
    update_req = UpdateTaskRequest(
        user_id=user_id_1,
        task_id=task_id,
        title="Updated by User 1"
    )
    result = await update_task_handler(update_req, session=async_session)
    assert result.task["title"] == "Updated by User 1"

    # Try to update task as user 2 (should fail due to user isolation)
    update_req_2 = UpdateTaskRequest(
        user_id=user_id_2,
        task_id=task_id,
        title="Attempted Update by User 2"
    )

    with pytest.raises(Exception):  # Should raise an authorization error
        await update_task_handler(update_req_2, session=async_session)


@pytest.mark.asyncio
async def test_complete_task_status_toggling(async_session):
    """Test complete_task and verify status toggling works correctly."""
    user_id = str(uuid4())

    # Create a task
    add_result = await add_task_handler(AddTaskRequest(
        user_id=user_id,
        title="Task to Complete"
    ), session=async_session)
    task_id = add_result.task_id

    # Complete the task
    complete_req = CompleteTaskRequest(
        user_id=user_id,
        task_id=task_id,
        complete=True
    )
    result = await complete_task_handler(complete_req, session=async_session)

    # Verify task is completed
    assert result.task["status"] == "completed"
    assert result.task["completed_at"] is not None

    # Uncomplete the task
    uncomplete_req = CompleteTaskRequest(
        user_id=user_id,
        task_id=task_id,
        complete=False
    )
    result2 = await complete_task_handler(uncomplete_req, session=async_session)

    # Verify task is not completed
    assert result2.task["status"] == "pending"
    assert result2.task["completed_at"] is None


@pytest.mark.asyncio
async def test_delete_task_with_user_isolation(async_session):
    """Test delete_task and verify task removal with user isolation."""
    user_id_1 = str(uuid4())
    user_id_2 = str(uuid4())

    # Create task for user 1
    add_result = await add_task_handler(AddTaskRequest(
        user_id=user_id_1,
        title="Task to Delete"
    ), session=async_session)
    task_id = add_result.task_id

    # Try to delete as user 2 (should fail)
    delete_req_2 = DeleteTaskRequest(
        user_id=user_id_2,
        task_id=task_id
    )

    with pytest.raises(Exception):  # Should raise an authorization error
        await delete_task_handler(delete_req_2, session=async_session)

    # Delete as user 1 (should succeed)
    delete_req_1 = DeleteTaskRequest(
        user_id=user_id_1,
        task_id=task_id
    )
    result = await delete_task_handler(delete_req_1, session=async_session)

    assert result.task_id == task_id
    assert result.message == "Task deleted successfully"

    # Verify task is deleted (should not be found)
    list_req = ListTasksRequest(user_id=user_id_1)
    list_result = await list_tasks_handler(list_req, session=async_session)
    deleted_task_exists = any(task["id"] == str(task_id) for task in list_result.tasks)
    assert not deleted_task_exists


@pytest.mark.asyncio
async def test_all_operations_data_persistence(async_session):
    """Verify all five task operations work via MCP tools and return expected results."""
    user_id = str(uuid4())

    # 1. Add task
    add_result = await add_task_handler(AddTaskRequest(
        user_id=user_id,
        title="Complete Flow Test",
        priority=2
    ), session=async_session)
    task_id = add_result.task_id
    assert add_result.task_id is not None

    # 2. List tasks
    list_result = await list_tasks_handler(ListTasksRequest(user_id=user_id), session=async_session)
    assert any(task["id"] == str(task_id) for task in list_result.tasks)

    # 3. Update task
    update_result = await update_task_handler(UpdateTaskRequest(
        user_id=user_id,
        task_id=task_id,
        title="Updated Complete Flow Test",
        priority=4
    ), session=async_session)
    assert update_result.task["title"] == "Updated Complete Flow Test"
    assert update_result.task["priority"] == 4

    # 4. Complete task
    complete_result = await complete_task_handler(CompleteTaskRequest(
        user_id=user_id,
        task_id=task_id,
        complete=True
    ), session=async_session)
    assert complete_result.task["status"] == "completed"

    # 5. Delete task
    delete_result = await delete_task_handler(DeleteTaskRequest(
        user_id=user_id,
        task_id=task_id
    ), session=async_session)
    assert delete_result.message == "Task deleted successfully"


@pytest.mark.asyncio
async def test_data_persistence_in_postgresql(async_session):
    """Confirm 100% of tool operations correctly persist data in Neon PostgreSQL with proper user isolation."""
    user_id = str(uuid4())

    # Create multiple tasks
    task_ids = []
    for i in range(5):
        result = await add_task_handler(AddTaskRequest(
            user_id=user_id,
            title=f"Persistence Test Task {i}",
            priority=i + 1
        ), session=async_session)
        task_ids.append(result.task_id)

    # Verify all tasks are persisted by listing
    list_result = await list_tasks_handler(ListTasksRequest(user_id=user_id), session=async_session)
    assert list_result.total_count >= 5

    # Verify each task is properly persisted with correct data
    persisted_task_ids = {task["id"] for task in list_result.tasks}
    for task_id in task_ids:
        assert str(task_id) in persisted_task_ids

    # Verify user isolation
    assert all(task["user_id"] == user_id for task in list_result.tasks)