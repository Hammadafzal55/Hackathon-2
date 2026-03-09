"""
MCP Tool Schemas
This module defines the Pydantic schemas for all MCP task tools.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class BaseMCPRequest(BaseModel):
    """Base schema for all MCP tool requests that require authentication context."""
    user_id: str = Field(..., description="The ID of the authenticated user making the request")


class AddTaskRequest(BaseMCPRequest):
    """Schema for the add_task MCP tool request."""
    title: str = Field(..., min_length=1, max_length=255, description="Title of the task to create")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the task")
    priority: Optional[int] = Field(1, ge=1, le=5, description="Priority level (1-5)")
    due_date: Optional[datetime] = Field(None, description="Due date for the task")


class AddTaskResponse(BaseModel):
    """Response schema for add_task operation."""
    task_id: UUID
    message: str = "Task created successfully"
    task: dict


class ListTasksRequest(BaseMCPRequest):
    """Schema for the list_tasks MCP tool request."""
    status_filter: Optional[str] = Field(None, description="Filter tasks by status")
    limit: Optional[int] = Field(None, ge=1, description="Maximum number of tasks to return")
    offset: Optional[int] = Field(0, ge=0, description="Offset for pagination")


class ListTasksResponse(BaseModel):
    """Response schema for list_tasks operation."""
    tasks: List[dict]
    total_count: int


class UpdateTaskRequest(BaseMCPRequest):
    """Schema for the update_task MCP tool request."""
    task_id: UUID = Field(..., description="ID of the task to update")
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="New title for the task")
    description: Optional[str] = Field(None, max_length=1000, description="New description")
    status: Optional[str] = Field(None, description="New status")
    priority: Optional[int] = Field(None, ge=1, le=5, description="New priority")
    due_date: Optional[datetime] = Field(None, description="New due date")


class UpdateTaskResponse(BaseModel):
    """Response schema for update_task operation."""
    task_id: UUID
    message: str = "Task updated successfully"
    task: dict


class CompleteTaskRequest(BaseMCPRequest):
    """Schema for the complete_task MCP tool request (toggles completion status)."""
    task_id: UUID = Field(..., description="ID of the task to toggle completion")
    complete: bool = Field(True, description="Whether to complete (true) or uncomplete (false) the task")


class CompleteTaskResponse(BaseModel):
    """Response schema for complete_task operation."""
    task_id: UUID
    message: str = "Task completion status updated successfully"
    task: dict


class DeleteTaskRequest(BaseMCPRequest):
    """Schema for the delete_task MCP tool request."""
    task_id: UUID = Field(..., description="ID of the task to delete")


class DeleteTaskResponse(BaseModel):
    """Response schema for delete_task operation."""
    task_id: UUID
    message: str = "Task deleted successfully"


# Enum-like values for task statuses
class TaskStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @classmethod
    def get_allowed_values(cls):
        return [cls.PENDING, cls.IN_PROGRESS, cls.COMPLETED, cls.CANCELLED]