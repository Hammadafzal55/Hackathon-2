"""
Event publisher for task mutation events via Dapr pub/sub.
Gracefully skips publishing if Dapr sidecar is unavailable.
"""
import logging
from typing import List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


async def publish_task_event(
    event_type: str,
    task_id: uuid.UUID,
    user_id: str,
    changed_fields: Optional[List[str]] = None,
    has_recurrence: bool = False,
    has_reminders: bool = False,
) -> None:
    """
    Publish a task event to the Dapr pub/sub topic.

    Gracefully skips if Dapr sidecar is unavailable — backend never crashes.
    """
    try:
        import os
        pubsub_name = os.getenv("PUBSUB_NAME", "pubsub")
        topic = os.getenv("TOPIC_TASK_EVENTS", "task-events")

        event_data = {
            "event_type": event_type,
            "task_id": str(task_id),
            "user_id": str(user_id),
            "timestamp": datetime.utcnow().isoformat(),
            "changed_fields": changed_fields or [],
            "has_recurrence": has_recurrence,
            "has_reminders": has_reminders,
        }

        from dapr.clients import DaprClient
        import json
        with DaprClient() as client:
            client.publish_event(
                pubsub_name=pubsub_name,
                topic_name=topic,
                data=json.dumps(event_data),
                data_content_type="application/json",
            )
        logger.info(f"Published {event_type} event for task {task_id}")
    except Exception as e:
        logger.warning(f"Dapr unavailable, event not published: {e}")
