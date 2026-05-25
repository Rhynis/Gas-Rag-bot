"""Tests for health endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_ok(test_client: AsyncClient) -> None:
    """Basic health endpoint should return ok."""
    response = await test_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
