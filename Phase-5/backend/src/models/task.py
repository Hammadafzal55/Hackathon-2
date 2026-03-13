"""
Task model for the Todo backend.
Defines the Task entity for managing user tasks.
"""

from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
import uuid

if TYPE_CHECKING:
    from .user import User


# Define task status enum
class TaskStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskBase(SQLModel):
    """
    Base fields for Task model, shared across different model variants.
    """
    title: str = Field(nullable=False, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default=TaskStatus.PENDING, max_length=20)
    priority: int = Field(default=1, ge=1, le=5)  # 1-5 scale, 1 being lowest priority
    due_date: Optional[datetime] = Field(default=None)


class Task(TaskBase, table=True):
    """
    Task model representing a task in the todo system.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # User ID field (without foreign key constraint for testing)
    user_id: str = Field(nullable=False, index=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)

    # Advanced features (008)
    tags: List[str] = Field(default=[], sa_column=Column(JSONB, nullable=False, server_default='[]'))
    recurrence_rule: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    recurrence_parent_id: Optional[uuid.UUID] = Field(default=None, nullable=True)
    next_occurrence: Optional[datetime] = Field(default=None, nullable=True)

    # Relationship to User (temporarily removed for testing without authentication)
    # user: "User" = Relationship(back_populates="tasks")

    # Update updated_at timestamp before each update
    def __setattr__(self, name, value):
        if name in ['title', 'description', 'status', 'priority', 'due_date']:
            # Update updated_at when any mutable field changes
            from datetime import datetime
            super().__setattr__('updated_at', datetime.utcnow())

            # Handle completion status changes
            if name == 'status':
                if value == TaskStatus.COMPLETED:
                    # Set completed_at when status becomes completed
                    super().__setattr__('completed_at', datetime.utcnow())
                else:
                    # Clear completed_at when status is changed from completed to any other status
                    if self.status == TaskStatus.COMPLETED and value != TaskStatus.COMPLETED:
                        super().__setattr__('completed_at', None)

        super().__setattr__(name, value)


class TaskCreate(TaskBase):
    """
    Model for creating a new task.
    """
    tags: List[str] = []
    recurrence_rule: Optional[dict] = None
    reminders: List[dict] = []  # List of {lead_time_minutes: int}


class TaskUpdate(SQLModel):
    """
    Model for updating task information.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    recurrence_rule: Optional[dict] = None
    reminders: Optional[List[dict]] = None  # List of {lead_time_minutes: int}


class TaskRead(TaskBase):
    """
    Model for reading task information.
    """
    id: uuid.UUID
    user_id: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    tags: List[str] = []
    recurrence_rule: Optional[dict] = None
    recurrence_parent_id: Optional[uuid.UUID] = None
    next_occurrence: Optional[datetime] = None
    reminders: List[dict] = []  # populated by API route
