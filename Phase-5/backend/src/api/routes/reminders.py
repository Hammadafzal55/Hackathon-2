"""
Reminder CRUD routes: list, add, delete reminders per task.
"""
import logging
from datetime import datetime, timedelta
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_async_session
from src.middleware.auth import get_current_user_id
from src.models.task import Task
from src.models.reminder import Reminder
from src.api.schemas.reminder import ReminderCreate, ReminderRead

logger = logging.getLogger(__name__)

router = APIRouter()


async def _verify_task_ownership(task_id: UUID, user_id: UUID, session: AsyncSession) -> Task:
    """Verify task exists and belongs to the user."""
    stmt = select(Task).where(Task.id == task_id, Task.user_id == str(user_id))
    result = await session.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/tasks/{task_id}/reminders", response_model=List[ReminderRead])
async def list_reminders(
    task_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session),
):
    """List all reminders for a task."""
    await _verify_task_ownership(task_id, current_user_id, session)
    stmt = select(Reminder).where(Reminder.task_id == task_id)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("/tasks/{task_id}/reminders", response_model=ReminderRead, status_code=201)
async def add_reminder(
    task_id: UUID,
    reminder_data: ReminderCreate,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session),
):
    """Add a reminder to a task. Task must have a due_date set."""
    task = await _verify_task_ownership(task_id, current_user_id, session)

    if not task.due_date:
        raise HTTPException(status_code=422, detail="Task must have a due_date to add a reminder")

    fire_at = task.due_date - timedelta(minutes=reminder_data.lead_time_minutes)
    if fire_at <= datetime.utcnow():
        logger.warning(f"Reminder fire_at {fire_at} is in the past for task {task_id} — still creating")

    reminder = Reminder(
        task_id=task_id,
        lead_time_minutes=reminder_data.lead_time_minutes,
        fire_at=fire_at,
    )
    session.add(reminder)
    await session.commit()
    await session.refresh(reminder)
    return reminder


@router.delete("/reminders/{reminder_id}", status_code=204)
async def delete_reminder(
    reminder_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session),
):
    """Delete a reminder by ID (verifies ownership via task)."""
    stmt = select(Reminder).where(Reminder.id == reminder_id)
    result = await session.execute(stmt)
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    # Verify ownership via task
    await _verify_task_ownership(reminder.task_id, current_user_id, session)

    await session.delete(reminder)
    await session.commit()
