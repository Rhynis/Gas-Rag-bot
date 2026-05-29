"""Repository for chatbot messages."""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.message import Message


class MessageRepository:
    """Data access layer for conversation messages."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[str, Any]) -> Message:
        """Create a message and auto-flag low confidence or negative feedback."""
        payload = dict(data)
        payload.setdefault("created_at", datetime.now(UTC))
        if "intent_confidence" in payload and payload["intent_confidence"] is not None:
            payload["intent_confidence"] = Decimal(str(payload["intent_confidence"]))
        message = Message(**payload)
        if message.should_be_flagged():
            message.flagged_for_review = True
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def get_by_id(self, message_id: UUID) -> Message | None:
        """Fetch a message by ID."""
        result = await self.session.execute(select(Message).where(Message.id == message_id))
        return result.scalar_one_or_none()

    async def list_by_conversation(
        self,
        conversation_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Message]:
        """List messages in chronological order."""
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_recent(self, conversation_id: UUID, limit: int = 10) -> list[Message]:
        """Return recent messages in chronological order."""
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        messages.reverse()
        return messages

    async def update_feedback(self, message_id: UUID, score: int) -> Message:
        """Store customer feedback for a message."""
        message = await self._require(message_id)
        message.feedback_score = score
        if score == -1:
            message.flagged_for_review = True
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def flag_for_review(self, message_id: UUID) -> Message:
        """Flag a message for staff review."""
        message = await self._require(message_id)
        message.flagged_for_review = True
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def get_flagged(self, skip: int = 0, limit: int = 50) -> list[Message]:
        """List messages awaiting review."""
        result = await self.session.execute(
            select(Message)
            .where(Message.flagged_for_review.is_(True))
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_flagged_for_review(
        self,
        skip: int = 0,
        limit: int = 20,
        intent_filter: str | None = None,
    ) -> tuple[list[Message], int]:
        """List flagged messages oldest first with total count."""
        query = select(Message).where(Message.flagged_for_review.is_(True))
        count_query = (
            select(func.count()).select_from(Message).where(Message.flagged_for_review.is_(True))
        )
        if intent_filter:
            query = query.where(Message.intent == intent_filter)
            count_query = count_query.where(Message.intent == intent_filter)

        total = int((await self.session.execute(count_query)).scalar_one())
        result = await self.session.execute(
            query.order_by(Message.created_at.asc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all()), total

    async def get_previous_message(self, message_id: UUID) -> Message | None:
        """Return the nearest previous user message in the same conversation."""
        message = await self.get_by_id(message_id)
        if message is None:
            return None
        result = await self.session.execute(
            select(Message)
            .where(
                Message.conversation_id == message.conversation_id,
                Message.created_at < message.created_at,
                Message.role == "user",
            )
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def update(self, message_id: UUID, data: dict[str, Any]) -> Message:
        """Update a message with review workflow fields."""
        message = await self._require(message_id)
        payload = dict(data)
        if "intent_confidence" in payload and payload["intent_confidence"] is not None:
            payload["intent_confidence"] = Decimal(str(payload["intent_confidence"]))
        for key, value in payload.items():
            if hasattr(message, key):
                setattr(message, key, value)
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def _require(self, message_id: UUID) -> Message:
        message = await self.get_by_id(message_id)
        if message is None:
            raise NotFoundException("Message not found", error_code="message_not_found")
        return message
