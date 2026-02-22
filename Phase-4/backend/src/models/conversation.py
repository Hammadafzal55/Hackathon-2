"""
Conversation model for the AI Chat feature.
Stores conversation sessions between users and the AI assistant.
"""

from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional
import uuid


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a chat session.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(nullable=False, index=True)
    title: str = Field(default="New Conversation", max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
