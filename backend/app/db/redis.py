"""Redis dependency helpers."""

from typing import cast

from fastapi import Request
from redis.asyncio import Redis


async def get_redis(request: Request) -> Redis:
    """Return the application Redis client."""
    return cast(Redis, request.app.state.redis)
