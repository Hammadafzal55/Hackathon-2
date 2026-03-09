"""Notification response schemas."""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class NotificationRead(BaseModel):
    id: uuid.UUID
    user_id: str
    task_id: Optional[uuid.UUID] = None
    message: str
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    notifications: List[NotificationRead]
    total_count: int
    unread_count: int
