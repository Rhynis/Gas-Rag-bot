"""Shared pytest fixtures."""

import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
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
