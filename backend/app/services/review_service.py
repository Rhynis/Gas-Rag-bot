"""Review service for continuous learning from flagged messages."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import case, func, select

from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.logging import get_logger
from app.models.message import Message
from app.models.user import User
from app.rag.embeddings import EmbeddingService
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.review import FlaggedMessageResponse, ReviewerStatistic, ReviewStatistics


class ReviewService:
    """Manage review workflow for flagged chat messages."""

    def __init__(
        self,
        msg_repo: MessageRepository,
        kb_repo: KnowledgeBaseRepository,
        embedding_service: EmbeddingService,
    ) -> None:
        self.msg_repo = msg_repo
        self.kb_repo = kb_repo
        self.embedding_service = embedding_service
        self.logger = get_logger(__name__)

    async def get_flagged_messages(
        self,
        skip: int = 0,
        limit: int = 20,
        intent_filter: str | None = None,
    ) -> tuple[list[FlaggedMessageResponse], int]:
        """List flagged messages awaiting review, oldest first."""
        messages, total = await self.msg_repo.get_flagged_for_review(
            skip=skip,
            limit=limit,
            intent_filter=intent_filter,
        )
        responses = []
        for message in messages:
            previous = await self.msg_repo.get_previous_message(message.id)
            responses.append(
                FlaggedMessageResponse(
                    message_id=message.id,
                    conversation_id=message.conversation_id,
                    bot_response=message.content,
                    user_query=previous.content if previous else "",
                    intent=message.intent,
                    intent_confidence=self._confidence_to_float(message.intent_confidence),
                    feedback_score=message.feedback_score,
                    created_at=message.created_at,
                    retrieved_documents=message.retrieved_documents,
                    reason=self._infer_reason(message),
                )
            )
        return responses, total

    async def approve_message(
        self,
        message_id: UUID,
        corrected_content: str | None,
        current_user: User,
    ) -> bool:
        """Approve a flagged message, optionally storing a correction."""
        self._ensure_staff(current_user)
        message = await self.msg_repo.get_by_id(message_id)
        if message is None:
            raise NotFoundException(f"Message not found: {message_id}")

        await self.msg_repo.update(
            message_id,
            {
                "review_action": "approved",
                "reviewed_by": current_user.id,
                "reviewed_at": datetime.now(UTC),
                "corrected_content": corrected_content,
                "flagged_for_review": False,
            },
        )
        self.logger.info(
            "message_approved",
            message_id=str(message_id),
            reviewer_id=str(current_user.id),
            had_correction=corrected_content is not None,
        )
        return True

    async def reject_message(self, message_id: UUID, current_user: User) -> bool:
        """Reject a flagged message so it is not reused for learning."""
        self._ensure_staff(current_user)
        message = await self.msg_repo.get_by_id(message_id)
        if message is None:
            raise NotFoundException(f"Message not found: {message_id}")

        await self.msg_repo.update(
            message_id,
            {
                "review_action": "rejected",
                "reviewed_by": current_user.id,
                "reviewed_at": datetime.now(UTC),
                "flagged_for_review": False,
            },
        )
        return True

    async def add_to_knowledge_base(
        self,
        message_id: UUID,
        category: str,
        title: str,
        current_user: User,
    ) -> UUID:
        """Convert a reviewed message into a knowledge base document."""
        self._ensure_staff(current_user)
        message = await self.msg_repo.get_by_id(message_id)
        if message is None:
            raise NotFoundException(f"Message not found: {message_id}")

        content = message.corrected_content or message.content
        embedding = await self.embedding_service.embed_text(f"{title}\n\n{content}")
        document = await self.kb_repo.create(
            data={
                "title": title,
                "content": content,
                "category": category,
                "source": "user_chat_approved",
                "source_message_id": message_id,
            },
            embedding=embedding,
        )
        await self.msg_repo.update(
            message_id,
            {
                "review_action": "added_to_kb",
                "reviewed_by": current_user.id,
                "reviewed_at": datetime.now(UTC),
                "flagged_for_review": False,
            },
        )
        self.logger.info(
            "message_added_to_kb",
            message_id=str(message_id),
            kb_id=str(document.id),
            category=category,
        )
        return document.id

    async def get_statistics(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> ReviewStatistics:
        """Get review queue and completion statistics."""
        filters = []
        if date_from:
            filters.append(Message.created_at >= date_from)
        if date_to:
            filters.append(Message.created_at <= date_to)

        base = select(
            func.count(
                case(
                    (
                        (Message.flagged_for_review.is_(True))
                        | (Message.review_action.is_not(None)),
                        1,
                    )
                )
            ).label("total_flagged"),
            func.count(case((Message.flagged_for_review.is_(True), 1))).label("pending"),
            func.count(case((Message.review_action == "approved", 1))).label("approved"),
            func.count(case((Message.review_action == "rejected", 1))).label("rejected"),
            func.count(case((Message.review_action == "added_to_kb", 1))).label("added_to_kb"),
        ).where(*filters)
        row = (await self.msg_repo.session.execute(base)).one()

        by_intent_result = await self.msg_repo.session.execute(
            select(Message.intent, func.count())
            .where(
                ((Message.flagged_for_review.is_(True)) | (Message.review_action.is_not(None))),
                *filters,
            )
            .group_by(Message.intent)
        )
        by_intent = {
            str(intent or "unknown"): int(count) for intent, count in by_intent_result.all()
        }

        reviewed_filter = [
            Message.reviewed_at.is_not(None),
            Message.review_action.is_not(None),
            *filters,
        ]
        avg_result = await self.msg_repo.session.execute(
            select(
                func.avg(func.extract("epoch", Message.reviewed_at - Message.created_at) / 60.0)
            ).where(*reviewed_filter)
        )
        average = avg_result.scalar_one_or_none()

        reviewers_result = await self.msg_repo.session.execute(
            select(Message.reviewed_by, func.count())
            .where(Message.reviewed_by.is_not(None), *filters)
            .group_by(Message.reviewed_by)
            .order_by(func.count().desc())
            .limit(5)
        )

        return ReviewStatistics(
            total_flagged=int(row.total_flagged or 0),
            pending=int(row.pending or 0),
            approved=int(row.approved or 0),
            rejected=int(row.rejected or 0),
            added_to_kb=int(row.added_to_kb or 0),
            by_intent=by_intent,
            average_review_time_minutes=(float(average) if average is not None else None),
            top_reviewers=[
                ReviewerStatistic(reviewer_id=reviewer_id, reviewed_count=int(count))
                for reviewer_id, count in reviewers_result.all()
                if reviewer_id is not None
            ],
        )

    def _infer_reason(self, message: Message) -> str:
        if message.feedback_score == -1:
            return "Khách hàng đánh giá tiêu cực"
        confidence = self._confidence_to_float(message.intent_confidence)
        if confidence is not None and confidence < 0.6:
            return f"Confidence thấp ({confidence:.2f})"
        return "Cần review"

    @staticmethod
    def _confidence_to_float(value: Decimal | None) -> float | None:
        return float(value) if value is not None else None

    @staticmethod
    def _ensure_staff(user: User) -> None:
        if not user.is_staff():
            raise ForbiddenException("Only staff can review messages")
