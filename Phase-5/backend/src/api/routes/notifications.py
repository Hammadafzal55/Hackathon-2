"""
Notification routes: list, mark read, mark all read.
"""
import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from src.database.database import get_async_session
from src.middleware.auth import get_current_user_id
from src.models.notification import Notification
from src.api.schemas.notification import NotificationRead, NotificationListResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/notifications", response_model=NotificationListResponse)
async def list_notifications(
    unread: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session),
):
    """List notifications for the current user."""
    user_id_str = str(current_user_id)

    # Unread count (always computed regardless of filter)
    unread_stmt = select(Notification).where(
        Notification.user_id == user_id_str,
        Notification.read == False,
    )
    unread_result = await session.execute(unread_stmt)
    unread_count = len(unread_result.scalars().all())

    # Base query with optional unread filter
    base_stmt = select(Notification).where(Notification.user_id == user_id_str)
    if unread is True:
        base_stmt = base_stmt.where(Notification.read == False)
    elif unread is False:
        base_stmt = base_stmt.where(Notification.read == True)

    # Total count
    count_result = await session.execute(base_stmt)
    total_count = len(count_result.scalars().all())

    # Paginated results ordered by newest first
    paged_stmt = base_stmt.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
    result = await session.execute(paged_stmt)
    notifications = result.scalars().all()

    return NotificationListResponse(
        notifications=notifications,
        total_count=total_count,
        unread_count=unread_count,
    )


@router.patch("/notifications/{notification_id}/read", response_model=NotificationRead)
async def mark_notification_read(
    notification_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session),
):
    """Mark a single notification as read."""
    stmt = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == str(current_user_id),
    )
    result = await session.execute(stmt)
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.read = True
    session.add(notification)
    await session.commit()
    await session.refresh(notification)
    return notification


@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(
    current_user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session),
):
    """Mark all notifications as read for the current user."""
    stmt = (
        update(Notification)
        .where(Notification.user_id == str(current_user_id), Notification.read == False)
        .values(read=True)
    )
    await session.execute(stmt)
    await session.commit()
    return {"message": "All notifications marked as read"}
