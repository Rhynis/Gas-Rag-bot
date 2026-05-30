"""Schemas for continuous-learning review workflows."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.knowledge_base import KnowledgeCategory


class FlaggedMessageResponse(BaseModel):
    """Flagged assistant message with reviewer context."""

    message_id: UUID
    conversation_id: UUID
    bot_response: str
    user_query: str
    intent: str | None = None
    intent_confidence: float | None = Field(default=None, ge=0, le=1)
    feedback_score: int | None = Field(default=None, ge=-1, le=1)
    created_at: datetime
    retrieved_documents: list[dict[str, Any]] | None = None
    reason: str


class FlaggedMessageListResponse(BaseModel):
    """Paginated flagged message list."""

    items: list[FlaggedMessageResponse]
    total: int
    skip: int
    limit: int


class ReviewActionRequest(BaseModel):
    """Approve/reject payload with an optional correction."""

    corrected_content: str | None = Field(default=None, min_length=1)


class AddToKnowledgeBaseRequest(BaseModel):
    """Request to convert an approved chat answer to a KB document."""

    category: KnowledgeCategory
    title: str = Field(min_length=1, max_length=255)


class ReviewerStatistic(BaseModel):
    """Review count by reviewer."""

    reviewer_id: UUID
    reviewed_count: int


class ReviewStatistics(BaseModel):
    """Aggregated review queue and completion metrics."""

    total_flagged: int
    pending: int
    approved: int
    rejected: int
    added_to_kb: int
    by_intent: dict[str, int]
    average_review_time_minutes: float | None = None
    top_reviewers: list[ReviewerStatistic] = Field(default_factory=list)
