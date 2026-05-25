"""Shared pytest fixtures."""

import os
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from fakeredis.aioredis import FakeRedis
from httpx import ASGITransport, AsyncClient

os.environ["DATABASE_URL"] = (
    "postgresql+asyncpg://gasbot:gasbot_dev_password@localhost:5432/gasbot_dev"
)
os.environ["JWT_SECRET_KEY"] = "test_secret_key_at_least_32_characters_long"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["ENVIRONMENT"] = "development"
os.environ["DEBUG"] = "false"


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Use asyncio for async tests."""
    return "asyncio"


@pytest_asyncio.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


class FakeUserRepository:
    """In-memory user repository for auth tests."""

    def __init__(self) -> None:
        self.users_by_id: dict[UUID, object] = {}
        self.users_by_email: dict[str, object] = {}

    async def create(self, data: Any, hashed_password: str) -> object:
        """Create a user from a schema-like object."""
        from app.models.user import User

        now = datetime.now(UTC)
        user = User(
            id=uuid4(),
            email=data.email.lower(),
            hashed_password=hashed_password,
            full_name=data.full_name,
            phone=data.phone,
            role="customer",
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self.users_by_id[user.id] = user
        self.users_by_email[user.email] = user
        return user

    async def get_by_id(self, user_id: UUID) -> object | None:
        """Find a user by ID."""
        return self.users_by_id.get(user_id)

    async def get_by_email(self, email: str) -> object | None:
        """Find a user by email."""
        return self.users_by_email.get(email.lower())

    async def update(self, user_id: UUID, data: dict[str, object]) -> object | None:
        """Update user fields."""
        user = self.users_by_id.get(user_id)
        if not user:
            return None
        for key, value in data.items():
            setattr(user, key, value)
        return user


@pytest.fixture
def fake_user_repository() -> FakeUserRepository:
    """Return an isolated fake user repository."""
    return FakeUserRepository()


@pytest_asyncio.fixture
async def mock_redis() -> AsyncGenerator[FakeRedis, None]:
    """Return an isolated fake Redis client."""
    redis = FakeRedis(decode_responses=True)
    await redis.flushall()
    try:
        yield redis
    finally:
        await redis.flushall()
        await redis.aclose()
