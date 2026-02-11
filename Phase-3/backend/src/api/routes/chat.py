"""
Chat API routes for AI-powered task management.
Implements stateless conversational chat using the OpenAI Agents SDK.
"""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func, col

from src.config import get_settings
from src.database.database import get_async_session
from src.middleware.auth import get_current_user_id
from src.models.conversation import Conversation
from src.models.message import Message
from src.api.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ToolCallInfo,
    ConversationListResponse,
    ConversationSummary,
    ConversationDetailResponse,
    MessageInfo,
)
from src.services.ai_agent import run_chat_agent, convert_to_sdk_format
from src.exceptions import ConversationNotFoundError, AIProviderError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session),
) -> ChatResponse:
    """
    Send a chat message and receive an AI response.
    Fully stateless — agent created fresh per request.
    """
    settings = get_settings()

    # T018: Input validation
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if len(request.message) > settings.chat_max_message_length:
        raise HTTPException(
            status_code=400,
            detail=f"Message exceeds maximum length of {settings.chat_max_message_length} characters",
        )

    # T015: Load or create conversation
    if request.conversation_id:
        # Load existing conversation
        stmt = select(Conversation).where(
            Conversation.id == request.conversation_id,
            Conversation.user_id == str(current_user_id),
        )
        result = await session.execute(stmt)
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise ConversationNotFoundError(str(request.conversation_id))
    else:
        # Create new conversation with title from first message
        title = request.message[:50].strip()
        if len(request.message) > 50:
            title += "..."
        conversation = Conversation(
            user_id=str(current_user_id),
            title=title,
        )
        session.add(conversation)
        await session.flush()  # Get the ID without committing

    # Persist user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )
    session.add(user_message)
    await session.flush()

    # T014: Load context window (last N messages)
    context_stmt = (
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(col(Message.created_at).asc())
        .limit(settings.chat_context_window)
    )
    result = await session.execute(context_stmt)
    context_messages = result.scalars().all()

    # Convert to SDK format
    sdk_messages = convert_to_sdk_format(context_messages)

    # T019: Run agent with error handling
    try:
        agent_result = await run_chat_agent(
            user_id=str(current_user_id),
            messages=sdk_messages,
            session=session,
        )
    except AIProviderError:
        # Commit user message so it's not lost
        conversation.updated_at = datetime.utcnow()
        await session.commit()
        raise
    except Exception as e:
        # Commit user message so it's not lost
        conversation.updated_at = datetime.utcnow()
        await session.commit()
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while processing your message")

    # Persist assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=agent_result["response"],
        tool_calls=agent_result["tool_calls"] if agent_result["tool_calls"] else None,
    )
    session.add(assistant_message)

    # T016: Update conversation timestamp
    conversation.updated_at = datetime.utcnow()

    await session.commit()

    # Build response
    tool_calls = [
        ToolCallInfo(
            tool_name=tc.get("tool_name", "unknown"),
            arguments=tc.get("arguments", {}),
            result=tc.get("result", ""),
            success=tc.get("success", True),
        )
        for tc in agent_result.get("tool_calls", [])
    ]

    return ChatResponse(
        conversation_id=conversation.id,
        message=agent_result["response"],
        tool_calls=tool_calls,
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    current_user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session),
) -> ConversationListResponse:
    """
    List conversations for the authenticated user, ordered by most recent activity.
    """
    # Clamp parameters
    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    # Get total count
    count_stmt = (
        select(func.count())
        .select_from(Conversation)
        .where(Conversation.user_id == str(current_user_id))
    )
    count_result = await session.execute(count_stmt)
    total_count = count_result.scalar() or 0

    # Get conversations
    conv_stmt = (
        select(Conversation)
        .where(Conversation.user_id == str(current_user_id))
        .order_by(col(Conversation.updated_at).desc())
        .offset(offset)
        .limit(limit)
    )
    conv_result = await session.execute(conv_stmt)
    conversations = conv_result.scalars().all()

    # Build summaries with message counts
    summaries = []
    for conv in conversations:
        msg_count_stmt = (
            select(func.count())
            .select_from(Message)
            .where(Message.conversation_id == conv.id)
        )
        msg_count_result = await session.execute(msg_count_stmt)
        msg_count = msg_count_result.scalar() or 0

        summaries.append(
            ConversationSummary(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=msg_count,
            )
        )

    return ConversationListResponse(
        conversations=summaries,
        total_count=total_count,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: UUID,
    limit: int = 50,
    current_user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session),
) -> ConversationDetailResponse:
    """
    Get conversation details with message history.
    """
    limit = max(1, min(limit, 200))

    # Load conversation with ownership check
    conv_stmt = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == str(current_user_id),
    )
    conv_result = await session.execute(conv_stmt)
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise ConversationNotFoundError(str(conversation_id))

    # Get message count
    msg_count_stmt = (
        select(func.count())
        .select_from(Message)
        .where(Message.conversation_id == conversation_id)
    )
    msg_count_result = await session.execute(msg_count_stmt)
    msg_count = msg_count_result.scalar() or 0

    # Load messages
    msg_stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(col(Message.created_at).asc())
        .limit(limit)
    )
    msg_result = await session.execute(msg_stmt)
    messages = msg_result.scalars().all()

    # Build response
    summary = ConversationSummary(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=msg_count,
    )

    message_infos = []
    for msg in messages:
        tool_calls = None
        if msg.tool_calls:
            tool_calls = [
                ToolCallInfo(
                    tool_name=tc.get("tool_name", "unknown"),
                    arguments=tc.get("arguments", {}),
                    result=tc.get("result", ""),
                    success=tc.get("success", True),
                )
                for tc in msg.tool_calls
            ]

        message_infos.append(
            MessageInfo(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                tool_calls=tool_calls,
                tool_call_id=msg.tool_call_id,
                tool_name=msg.tool_name,
                created_at=msg.created_at,
            )
        )

    return ConversationDetailResponse(
        conversation=summary,
        messages=message_infos,
    )
