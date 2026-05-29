"""Repository for chatbot conversations."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.models.conversation import Conversation


class ConversationRepository:
    """Data access layer for conversations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[str, Any]) -> Conversation:
        """Create a conversation."""
        conversation = Conversation(**data)
        self.session.add(conversation)
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        """Fetch a conversation with messages."""
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.messages))
        )
        return result.scalar_one_or_none()

    async def get_active_by_user(self, user_id: UUID) -> Conversation | None:
        """Fetch a user's active conversation."""
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id, Conversation.status == "active")
            .order_by(Conversation.updated_at.desc())
            .limit(1)
            .options(selectinload(Conversation.messages))
        )
        return result.scalar_one_or_none()

    async def get_active_by_session(self, session_id: str) -> Conversation | None:
        """Fetch an anonymous session's active conversation."""
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.session_id == session_id, Conversation.status == "active")
            .order_by(Conversation.updated_at.desc())
            .limit(1)
            .options(selectinload(Conversation.messages))
        )
        return result.scalar_one_or_none()

    async def list_for_staff(
        self,
        staff_id: UUID | None,
        status_filter: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Conversation], int]:
        """List conversations assigned to staff or awaiting assignment."""
        query = select(Conversation).options(selectinload(Conversation.messages))
        count_query = select(func.count()).select_from(Conversation)

        if staff_id is not None:
            query = query.where(
                (Conversation.assigned_to == staff_id) | (Conversation.assigned_to.is_(None))
            )
            count_query = count_query.where(
                (Conversation.assigned_to == staff_id) | (Conversation.assigned_to.is_(None))
            )
        if status_filter:
            query = query.where(Conversation.status == status_filter)
            count_query = count_query.where(Conversation.status == status_filter)

        query = query.order_by(Conversation.updated_at.desc()).offset(skip).limit(limit)
        total = (await self.session.execute(count_query)).scalar_one()
        conversations = list((await self.session.execute(query)).scalars().all())
        return conversations, total

    async def list_for_user(
        self,
        user_id: UUID,
        status_filter: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Conversation], int]:
        """List a user's conversations."""
        query = select(Conversation).where(Conversation.user_id == user_id)
        count_query = (
            select(func.count()).select_from(Conversation).where(Conversation.user_id == user_id)
        )
        if status_filter:
            query = query.where(Conversation.status == status_filter)
            count_query = count_query.where(Conversation.status == status_filter)
        query = query.order_by(Conversation.updated_at.desc()).offset(skip).limit(limit)
        total = (await self.session.execute(count_query)).scalar_one()
        conversations = list((await self.session.execute(query)).scalars().all())
        return conversations, total

    async def update_status(self, conversation_id: UUID, status: str) -> Conversation:
        """Update conversation status."""
        conversation = await self._require(conversation_id)
        conversation.status = status
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def assign_to_staff(
        self,
        conversation_id: UUID,
        staff_id: UUID | None,
        reason: str,
    ) -> Conversation:
        """Escalate and optionally assign a conversation."""
        conversation = await self._require(conversation_id)
        conversation.status = "escalated"
        conversation.assigned_to = staff_id
        conversation.escalated_at = datetime.now(UTC)
        conversation.escalation_reason = reason
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def transfer(self, conversation_id: UUID, staff_id: UUID) -> Conversation:
        """Transfer an escalated conversation."""
        conversation = await self._require(conversation_id)
        conversation.assigned_to = staff_id
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def resolve(
        self,
        conversation_id: UUID,
        satisfaction_rating: int | None = None,
    ) -> Conversation:
        """Resolve a conversation."""
        conversation = await self._require(conversation_id)
        conversation.status = "resolved"
        conversation.resolved_at = datetime.now(UTC)
        conversation.satisfaction_rating = satisfaction_rating
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def _require(self, conversation_id: UUID) -> Conversation:
        conversation = await self.get_by_id(conversation_id)
        if conversation is None:
            raise NotFoundException("Conversation not found", error_code="conversation_not_found")
        return conversation
