"""Notification model for in-app notification delivery."""
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Notification(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(nullable=False, index=True)
    task_id: Optional[uuid.UUID] = Field(default=None, nullable=True)
    message: str = Field(nullable=False)
    read: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
