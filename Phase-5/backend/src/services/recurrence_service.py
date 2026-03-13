"""
Recurrence service: generates recurring task instances via Dapr cron.
Called every 5 minutes by POST /cron/generate-recurrences.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
import uuid
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


def compute_next_occurrence(pattern: str, interval: int, current_due_date: datetime) -> Optional[datetime]:
    """Compute the next occurrence date based on recurrence rule."""
    try:
        from dateutil.relativedelta import relativedelta
        pattern = pattern.lower()
        if pattern == "daily":
            return current_due_date + timedelta(days=interval)
        elif pattern == "weekly":
            return current_due_date + timedelta(weeks=interval)
        elif pattern == "monthly":
            return current_due_date + relativedelta(months=interval)
        elif pattern == "yearly":
            return current_due_date + relativedelta(years=interval)
        else:
            logger.warning(f"Unknown recurrence pattern: {pattern}")
            return None
    except Exception as e:
        logger.error(f"Error computing next occurrence: {e}")
        return None


async def generate_due_recurrences(session: AsyncSession) -> int:
    """
    Find tasks with due recurrences and generate new task instances.
    Returns count of instances created.
    Uses INSERT ON CONFLICT DO NOTHING for idempotency.
    """
    from src.models.task import Task
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    now = datetime.utcnow()
    count = 0

    try:
        # Find parent tasks with recurrence rules that are due
        statement = select(Task).where(
            Task.recurrence_rule.isnot(None),
            Task.next_occurrence.isnot(None),
            Task.next_occurrence <= now,
            Task.recurrence_parent_id.is_(None),  # Only generate from parent tasks
        )
        result = await session.execute(statement)
        parent_tasks = result.scalars().all()

        for parent in parent_tasks:
            try:
                rule = parent.recurrence_rule
                pattern = rule.get("pattern", "daily")
                interval = rule.get("interval", 1)
                end_condition = rule.get("end_condition", "never")
                end_by_date = rule.get("end_by_date")

                new_due_date = parent.next_occurrence

                # Check end conditions
                if end_condition == "by_date" and end_by_date:
                    try:
                        end_dt = datetime.fromisoformat(end_by_date.replace("Z", ""))
                        if new_due_date > end_dt:
                            continue
                    except (ValueError, TypeError):
                        pass

                # Create new task instance — idempotent via unique constraint
                new_task_data = {
                    "id": uuid.uuid4(),
                    "title": parent.title,
                    "description": parent.description,
                    "status": "pending",
                    "priority": parent.priority,
                    "due_date": new_due_date,
                    "user_id": parent.user_id,
                    "tags": parent.tags or [],
                    "recurrence_parent_id": parent.id,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }

                insert_stmt = pg_insert(Task.__table__).values(**new_task_data)
                insert_stmt = insert_stmt.on_conflict_do_nothing(
                    constraint='uq_task_recurrence_parent_due_date'
                )
                await session.execute(insert_stmt)
                count += 1

                # Update parent's next_occurrence
                next_occ = compute_next_occurrence(pattern, interval, new_due_date)
                if next_occ:
                    parent.next_occurrence = next_occ
                    session.add(parent)

            except Exception as e:
                logger.error(f"Error generating recurrence for task {parent.id}: {e}")
                continue

        await session.commit()
        logger.info(f"Generated {count} recurring task instances")
        return count

    except Exception as e:
        await session.rollback()
        logger.error(f"Error in generate_due_recurrences: {e}")
        return 0
