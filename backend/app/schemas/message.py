"""Schemas for chatbot messages."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

MessageRole = Literal["user", "assistant", "staff", "system"]


class MessageResponse(BaseModel):
    """Message returned by conversation APIs."""

    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    intent: str | None = None
    intent_confidence: float | None = Field(default=None, ge=0, le=1)
    llm_provider: str | None = None
    llm_model: str | None = None
    tokens_used: int | None = None
    latency_ms: int | None = None
    retrieved_documents: list[dict[str, Any]] | None = None
    feedback_score: int | None = Field(default=None, ge=-1, le=1)
    flagged_for_review: bool = False
    is_emergency: bool = False
    created_at: datetime


class MessageListResponse(BaseModel):
    """Paginated conversation message list."""

    items: list[MessageResponse]
    total: int
    skip: int
    limit: int
