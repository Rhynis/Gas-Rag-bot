"""Admin review endpoints for continuous learning."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import get_current_staff
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models.user import User
from app.rag.dependencies import get_embedding_service
from app.rag.embeddings import EmbeddingService
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.review import (
    AddToKnowledgeBaseRequest,
    FlaggedMessageListResponse,
    ReviewActionRequest,
    ReviewStatistics,
)
from app.services.review_service import ReviewService

router = APIRouter()


def get_review_service(
    session: Annotated[AsyncSession, Depends(get_db)],
    embedding_service: Annotated[EmbeddingService, Depends(get_embedding_service)],
) -> ReviewService:
    """Build the request-scoped review service."""
    return ReviewService(
        msg_repo=MessageRepository(session),
        kb_repo=KnowledgeBaseRepository(session),
        embedding_service=embedding_service,
    )


@router.get(
    "/admin/review/flagged",
    response_model=FlaggedMessageListResponse,
    summary="List flagged messages",
)
@limiter.limit("60/minute")
async def list_flagged_messages(
    request: Request,
    staff: Annotated[User, Depends(get_current_staff)],
    service: Annotated[ReviewService, Depends(get_review_service)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    intent: Annotated[str | None, Query(max_length=50)] = None,
) -> FlaggedMessageListResponse:
    """Return flagged messages awaiting review."""
    del request, staff
    items, total = await service.get_flagged_messages(skip=skip, limit=limit, intent_filter=intent)
    return FlaggedMessageListResponse(items=items, total=total, skip=skip, limit=limit)


@router.post(
    "/admin/review/{message_id}/approve",
    response_model=bool,
    summary="Approve a flagged message",
)
@limiter.limit("60/minute")
async def approve_message(
    request: Request,
    message_id: UUID,
    payload: ReviewActionRequest,
    staff: Annotated[User, Depends(get_current_staff)],
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> bool:
    """Approve a message, optionally storing corrected content."""
    del request
    return await service.approve_message(message_id, payload.corrected_content, staff)


@router.post(
    "/admin/review/{message_id}/reject",
    response_model=bool,
    summary="Reject a flagged message",
)
@limiter.limit("60/minute")
async def reject_message(
    request: Request,
    message_id: UUID,
    staff: Annotated[User, Depends(get_current_staff)],
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> bool:
    """Reject a message so it is not reused for learning."""
    del request
    return await service.reject_message(message_id, staff)


@router.post(
    "/admin/review/{message_id}/add-to-kb",
    response_model=UUID,
    summary="Add reviewed message to knowledge base",
)
@limiter.limit("30/minute")
async def add_message_to_kb(
    request: Request,
    message_id: UUID,
    payload: AddToKnowledgeBaseRequest,
    staff: Annotated[User, Depends(get_current_staff)],
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> UUID:
    """Create a knowledge base entry from reviewed chat content."""
    del request
    return await service.add_to_knowledge_base(message_id, payload.category, payload.title, staff)


@router.get(
    "/admin/review/statistics",
    response_model=ReviewStatistics,
    summary="Get review statistics",
)
@limiter.limit("60/minute")
async def get_review_statistics(
    request: Request,
    staff: Annotated[User, Depends(get_current_staff)],
    service: Annotated[ReviewService, Depends(get_review_service)],
    date_from: Annotated[datetime | None, Query()] = None,
    date_to: Annotated[datetime | None, Query()] = None,
) -> ReviewStatistics:
    """Return review workflow statistics."""
    del request, staff
    return await service.get_statistics(date_from=date_from, date_to=date_to)
