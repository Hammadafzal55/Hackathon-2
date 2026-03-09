"""Reminder request/response schemas."""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator

VALID_LEAD_TIMES = [15, 60, 180, 1440, 2880]


class ReminderCreate(BaseModel):
    lead_time_minutes: int

    @field_validator('lead_time_minutes')
    @classmethod
    def validate_lead_time(cls, v: int) -> int:
        if v not in VALID_LEAD_TIMES:
            raise ValueError(f'lead_time_minutes must be one of {VALID_LEAD_TIMES}')
        return v


class ReminderRead(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    lead_time_minutes: int
    fire_at: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
