"""Tests for continuous-learning review service."""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest

from app.core.exceptions import ForbiddenException
from app.models.knowledge_base import KnowledgeBase
from app.models.message import Message
from app.models.user import User
from app.services.review_service import ReviewService


def make_user(role: str = "staff") -> User:
    return User(
        id=uuid.uuid4(),
        email=f"{uuid.uuid4()}@example.com",
        role=role,
        is_active=True,
    )


def make_message(
    *,
    conversation_id: uuid.UUID,
    role: str = "assistant",
    content: str = "Bot response",
    created_at: datetime,
    flagged: bool = True,
    intent: str = "product_inquiry",
    confidence: Decimal | None = Decimal("0.50"),
    feedback_score: int | None = None,
) -> Message:
    return Message(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        role=role,
        content=content,
        created_at=created_at,
        flagged_for_review=flagged,
        intent=intent,
        intent_confidence=confidence,
        feedback_score=feedback_score,
        retrieved_documents=[{"title": "Doc"}],
    )


class FakeScalarResult:
    def __init__(self, value: object) -> None:
        self.value = value

    def scalar_one_or_none(self) -> object:
        return self.value


class FakeRowResult:
    def __init__(self, rows: list[tuple[object, int]]) -> None:
        self.rows = rows

    def all(self) -> list[tuple[object, int]]:
        return self.rows


class FakeAggregateRow:
    total_flagged = 4
    pending = 1
    approved = 1
    rejected = 1
    added_to_kb = 1


class FakeAggregateResult:
    def one(self) -> FakeAggregateRow:
        return FakeAggregateRow()


class FakeSession:
    def __init__(self, reviewer_id: uuid.UUID) -> None:
        self.reviewer_id = reviewer_id
        self.calls = 0

    async def execute(self, statement: object) -> object:
        del statement
        self.calls += 1
        if self.calls == 1:
            return FakeAggregateResult()
        if self.calls == 2:
            return FakeRowResult([("product_inquiry", 2), ("safety_emergency", 1)])
        if self.calls == 3:
            return FakeScalarResult(12.5)
        return FakeRowResult([(self.reviewer_id, 3)])


class FakeMessageRepository:
    def __init__(self, messages: list[Message], reviewer_id: uuid.UUID | None = None) -> None:
        self.messages = messages
        self.session = FakeSession(reviewer_id or uuid.uuid4())

    async def get_flagged_for_review(
        self,
        skip: int = 0,
        limit: int = 20,
        intent_filter: str | None = None,
    ) -> tuple[list[Message], int]:
        items = [message for message in self.messages if message.flagged_for_review]
        if intent_filter:
            items = [message for message in items if message.intent == intent_filter]
        items = sorted(items, key=lambda message: message.created_at)
        return items[skip : skip + limit], len(items)

    async def get_previous_message(self, message_id: uuid.UUID) -> Message | None:
        message = await self.get_by_id(message_id)
        if message is None:
            return None
        previous = [
            item
            for item in self.messages
            if item.conversation_id == message.conversation_id
            and item.role == "user"
            and item.created_at < message.created_at
        ]
        return (
            sorted(previous, key=lambda item: item.created_at, reverse=True)[0]
            if previous
            else None
        )

    async def get_by_id(self, message_id: uuid.UUID) -> Message | None:
        return next((message for message in self.messages if message.id == message_id), None)

    async def update(self, message_id: uuid.UUID, data: dict[str, Any]) -> Message:
        message = await self.get_by_id(message_id)
        assert message is not None
        for key, value in data.items():
            setattr(message, key, value)
        return message


class FakeKnowledgeBaseRepository:
    def __init__(self) -> None:
        self.created: list[dict[str, Any]] = []

    async def create(self, data: dict[str, Any], embedding: list[float]) -> KnowledgeBase:
        self.created.append({"data": data, "embedding": embedding})
        return KnowledgeBase(id=uuid.uuid4(), embedding=embedding, **data)


class FakeEmbeddingService:
    async def embed_text(self, text: str) -> list[float]:
        assert text
        return [0.1] * 768


def make_service(
    messages: list[Message],
    reviewer_id: uuid.UUID | None = None,
) -> tuple[ReviewService, FakeMessageRepository, FakeKnowledgeBaseRepository]:
    msg_repo = FakeMessageRepository(messages, reviewer_id)
    kb_repo = FakeKnowledgeBaseRepository()
    service = ReviewService(
        msg_repo=msg_repo,  # type: ignore[arg-type]
        kb_repo=kb_repo,  # type: ignore[arg-type]
        embedding_service=FakeEmbeddingService(),  # type: ignore[arg-type]
    )
    return service, msg_repo, kb_repo


@pytest.mark.asyncio
async def test_get_flagged_returns_oldest_first() -> None:
    conversation_id = uuid.uuid4()
    now = datetime.now(UTC)
    user_message = make_message(
        conversation_id=conversation_id,
        role="user",
        content="Gia gas?",
        created_at=now - timedelta(minutes=3),
        flagged=False,
    )
    newer = make_message(conversation_id=conversation_id, created_at=now)
    older = make_message(conversation_id=conversation_id, created_at=now - timedelta(minutes=2))
    service, _repo, _kb = make_service([user_message, newer, older])

    items, total = await service.get_flagged_messages()

    assert total == 2
    assert [item.message_id for item in items] == [older.id, newer.id]
    assert items[0].user_query == "Gia gas?"


@pytest.mark.asyncio
async def test_approve_marks_as_approved() -> None:
    message = make_message(conversation_id=uuid.uuid4(), created_at=datetime.now(UTC))
    staff = make_user()
    service, _repo, _kb = make_service([message])

    result = await service.approve_message(message.id, None, staff)

    assert result is True
    assert message.review_action == "approved"
    assert message.flagged_for_review is False
    assert message.reviewed_by == staff.id


@pytest.mark.asyncio
async def test_approve_with_correction_stores_corrected_content() -> None:
    message = make_message(conversation_id=uuid.uuid4(), created_at=datetime.now(UTC))
    service, _repo, _kb = make_service([message])

    await service.approve_message(message.id, "Corrected answer", make_user())

    assert message.corrected_content == "Corrected answer"


@pytest.mark.asyncio
async def test_reject_unflags_message() -> None:
    message = make_message(conversation_id=uuid.uuid4(), created_at=datetime.now(UTC))
    service, _repo, _kb = make_service([message])

    result = await service.reject_message(message.id, make_user())

    assert result is True
    assert message.review_action == "rejected"
    assert message.flagged_for_review is False


@pytest.mark.asyncio
async def test_add_to_kb_creates_entry_with_embedding() -> None:
    message = make_message(conversation_id=uuid.uuid4(), created_at=datetime.now(UTC))
    message.corrected_content = "Corrected KB answer"
    service, _repo, kb_repo = make_service([message])

    kb_id = await service.add_to_knowledge_base(message.id, "faq", "Corrected FAQ", make_user())

    assert kb_id is not None
    assert kb_repo.created[0]["embedding"] == [0.1] * 768
    assert kb_repo.created[0]["data"]["content"] == "Corrected KB answer"


@pytest.mark.asyncio
async def test_add_to_kb_links_source_message() -> None:
    message = make_message(conversation_id=uuid.uuid4(), created_at=datetime.now(UTC))
    service, _repo, kb_repo = make_service([message])

    await service.add_to_knowledge_base(message.id, "technical", "Technical note", make_user())

    payload = kb_repo.created[0]["data"]
    assert payload["source"] == "user_chat_approved"
    assert payload["source_message_id"] == message.id
    assert message.review_action == "added_to_kb"


@pytest.mark.asyncio
async def test_only_staff_can_review() -> None:
    message = make_message(conversation_id=uuid.uuid4(), created_at=datetime.now(UTC))
    service, _repo, _kb = make_service([message])

    with pytest.raises(ForbiddenException):
        await service.approve_message(message.id, None, make_user(role="customer"))


@pytest.mark.asyncio
async def test_statistics_aggregates_correctly() -> None:
    reviewer_id = uuid.uuid4()
    service, _repo, _kb = make_service([], reviewer_id)

    stats = await service.get_statistics()

    assert stats.total_flagged == 4
    assert stats.pending == 1
    assert stats.approved == 1
    assert stats.rejected == 1
    assert stats.added_to_kb == 1
    assert stats.by_intent["product_inquiry"] == 2
    assert stats.average_review_time_minutes == 12.5
    assert stats.top_reviewers[0].reviewer_id == reviewer_id
