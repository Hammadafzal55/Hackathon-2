"""
Dapr event handlers: cron bindings and pub/sub subscription endpoints.
"""
import logging
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_async_session

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/dapr/subscribe")
async def dapr_subscribe():
    """Dapr calls this at startup to discover pub/sub subscriptions."""
    return [
        {
            "pubsubname": "pubsub",
            "topic": "task-events",
            "routes": {"default": "/task-events"},
        }
    ]


@router.post("/task-events")
async def handle_task_event(request: Request):
    """
    Pub/sub consumer for task-events topic.
    Idempotent: safe to call multiple times.
    Must return HTTP 200 for Dapr acknowledgment.
    """
    try:
        body = await request.json()
        # Dapr wraps events in a CloudEvent envelope
        data = body.get("data", body)
        event_type = data.get("event_type", "unknown")
        task_id = data.get("task_id", "unknown")
        logger.info(f"Received task event: {event_type} for task {task_id}")
    except Exception as e:
        logger.warning(f"Could not parse task-event body: {e}")

    return {"status": "SUCCESS"}


@router.post("/cron/generate-recurrences")
async def cron_generate_recurrences(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Dapr cron binding handler: called every 5 minutes.
    Generates new task instances for due recurring tasks.
    """
    try:
        from src.services.recurrence_service import generate_due_recurrences
        generated = await generate_due_recurrences(session)
        logger.info(f"Cron: generated {generated} recurrence instances")
        return {"generated": generated}
    except Exception as e:
        logger.error(f"Error in generate-recurrences cron: {e}")
        return {"generated": 0, "error": str(e)}


@router.post("/cron/check-reminders")
async def cron_check_reminders(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Dapr cron binding handler: called every 5 minutes.
    Checks for due reminders and creates notifications.
    """
    try:
        from src.services.reminder_service import check_due_reminders
        processed = await check_due_reminders(session)
        logger.info(f"Cron: processed {processed} reminders")
        return {"processed": processed}
    except Exception as e:
        logger.error(f"Error in check-reminders cron: {e}")
        return {"processed": 0, "error": str(e)}
