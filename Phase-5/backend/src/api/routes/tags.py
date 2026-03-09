"""
Tags route: returns distinct tags for the current user's tasks.
Used for autocomplete in the frontend TagInput component.
"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID

from src.database.database import get_async_session
from src.middleware.auth import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/tags")
async def get_tags(
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session),
):
    """Return all distinct tags used by the current user across all tasks."""
    try:
        result = await session.execute(
            text(
                "SELECT DISTINCT jsonb_array_elements_text(tags) AS tag "
                "FROM task WHERE user_id = :user_id AND tags != '[]'::jsonb "
                "ORDER BY tag"
            ),
            {"user_id": str(current_user_id)},
        )
        tags = [row[0] for row in result.fetchall()]
        return {"tags": tags}
    except Exception as e:
        logger.error(f"Error fetching tags for user {current_user_id}: {e}")
        return {"tags": []}
