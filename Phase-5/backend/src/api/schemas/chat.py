"""
Pydantic request/response schemas for the AI Chat API.
Matches contracts/chat-api.yaml specification.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class ChatRequest(BaseModel):
    """Request body for POST /api/chat."""
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[UUID] = None


class ToolCallInfo(BaseModel):
    """Information about a single tool call made during AI processing."""
    tool_name: str
    arguments: dict = Field(default_factory=dict)
    result: str = ""
    success: bool = True


class ChatResponse(BaseModel):
    """Response body for POST /api/chat."""
    conversation_id: UUID
    message: str
    tool_calls: List[ToolCallInfo] = Field(default_factory=list)


class ConversationSummary(BaseModel):
    """Summary of a conversation for list endpoint."""
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ConversationListResponse(BaseModel):
    """Response body for GET /api/conversations."""
    conversations: List[ConversationSummary]
    total_count: int


class MessageInfo(BaseModel):
    """Information about a single message in conversation detail."""
    id: UUID
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCallInfo]] = None
    tool_call_id: Optional[str] = None
    tool_name: Optional[str] = None
    created_at: datetime


class ConversationDetailResponse(BaseModel):
    """Response body for GET /api/conversations/{conversation_id}."""
    conversation: ConversationSummary
    messages: List[MessageInfo]
