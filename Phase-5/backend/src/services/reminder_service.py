"""
Reminder service: checks for due reminders and creates notifications.
Called every 5 minutes by POST /cron/check-reminders.
"""
import logging
from datetime import datetime
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

logger = logging.getLogger(__name__)

LEAD_TIME_LABELS = {
    15: "15 minutes",
    60: "1 hour",
    180: "3 hours",
    1440: "1 day",
    2880: "2 days",
}


async def create_task_reminders(session: AsyncSession, task, reminders_data: list) -> None:
    """
    Create Reminder rows for a task given a list of {lead_time_minutes} dicts.
    Requires task.due_date to be set.
    """
    from src.models.reminder import Reminder
    from datetime import timedelta

    if not task.due_date:
        return

    for reminder in reminders_data:
        lead_time = reminder.get('lead_time_minutes') if isinstance(reminder, dict) else getattr(reminder, 'lead_time_minutes', None)
        if not lead_time:
            continue
        fire_at = task.due_date - timedelta(minutes=lead_time)
        db_reminder = Reminder(
            task_id=task.id,
            lead_time_minutes=lead_time,
            fire_at=fire_at,
            status='pending',
        )
        session.add(db_reminder)


async def check_due_reminders(session: AsyncSession) -> int:
    """
    Find due reminders and create notifications for them.
    Returns count of reminders processed.
    Uses UPDATE WHERE status='pending' for idempotency — only first updater wins.
    """
    from src.models.reminder import Reminder
    from src.models.notification import Notification
    from src.models.task import Task

    now = datetime.utcnow()
    count = 0

    try:
        # Find pending reminders that are due
        statement = select(Reminder).where(
            Reminder.status == "pending",
            Reminder.fire_at <= now,
        )
        result = await session.execute(statement)
        due_reminders = result.scalars().all()

        for reminder in due_reminders:
            try:
                # Idempotent: only update if still pending
                update_stmt = (
                    update(Reminder)
                    .where(Reminder.id == reminder.id, Reminder.status == "pending")
                    .values(status="sent")
                    .returning(Reminder.id)
                )
                update_result = await session.execute(update_stmt)
                updated = update_result.fetchone()

                if not updated:
                    # Another process already handled this reminder
                    continue

                # Get the associated task
                task_stmt = select(Task).where(Task.id == reminder.task_id)
                task_result = await session.execute(task_stmt)
                task = task_result.scalar_one_or_none()

                if not task:
                    continue

                # Create notification
                label = LEAD_TIME_LABELS.get(reminder.lead_time_minutes, f"{reminder.lead_time_minutes} minutes")
                notification = Notification(
                    user_id=task.user_id,
                    task_id=reminder.task_id,
                    message=f"Reminder: '{task.title}' is due in {label}",
                )
                session.add(notification)
                count += 1

            except Exception as e:
                logger.error(f"Error processing reminder {reminder.id}: {e}")
                continue

        await session.commit()
        logger.info(f"Processed {count} due reminders")
        return count

    except Exception as e:
        await session.rollback()
        logger.error(f"Error in check_due_reminders: {e}")
        return 0
