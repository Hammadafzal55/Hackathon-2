"""Reminder model for task due-date notifications."""
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Reminder(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    task_id: uuid.UUID = Field(nullable=False, foreign_key="task.id")
    lead_time_minutes: int = Field(nullable=False)  # 15, 60, 180, 1440, or 2880
    fire_at: datetime = Field(nullable=False)
    status: str = Field(default="pending", max_length=20)  # pending, sent, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
