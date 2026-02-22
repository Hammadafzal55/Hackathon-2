"""
Message model for the AI Chat feature.
Stores individual messages within conversations.
"""

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON, Index
from datetime import datetime
from typing import Optional, Any
import uuid


class Message(SQLModel, table=True):
    """
    Message model representing a single message in a conversation.
    Supports user, assistant, and tool roles.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(
        foreign_key="conversation.id",
        nullable=False,
        index=True,
    )
    role: str = Field(nullable=False, max_length=20)  # user, assistant, tool
    content: Optional[str] = Field(default=None)
    tool_calls: Optional[Any] = Field(default=None, sa_column=Column(JSON, nullable=True))
    tool_call_id: Optional[str] = Field(default=None, max_length=255)
    tool_name: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_message_conversation_created", "conversation_id", "created_at"),
    )
