"""Tests for the Gemini LLM provider."""

from collections.abc import AsyncIterator
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from google.api_core import exceptions as google_exceptions

from app.llm.exceptions import (
    LLMConnectionError,
    LLMQuotaExceededError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from app.llm.providers.gemini_provider import GeminiProvider

pytestmark = pytest.mark.asyncio


class AsyncChunkStream:
    """Small async iterable for Gemini streaming tests."""

    def __init__(self, chunks: list[object]) -> None:
        self._chunks = chunks

    def __aiter__(self) -> AsyncIterator[object]:
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[object]:
        for chunk in self._chunks:
            yield chunk


@pytest.fixture
def gemini_model(monkeypatch: pytest.MonkeyPatch) -> Mock:
    model = Mock()
    monkeypatch.setattr("app.llm.providers.gemini_provider.genai.configure", Mock())
    monkeypatch.setattr(
        "app.llm.providers.gemini_provider.genai.GenerativeModel",
        Mock(return_value=model),
    )
    return model


def provider() -> GeminiProvider:
    return GeminiProvider(api_key="test-key", model="gemini-2.0-flash-exp")


async def test_generate_returns_response(gemini_model: Mock) -> None:
    gemini_model.generate_content_async = AsyncMock(
        return_value=SimpleNamespace(
            text="Xin chào",
            usage_metadata=SimpleNamespace(prompt_token_count=100, candidates_token_count=50),
            candidates=[SimpleNamespace(finish_reason="STOP")],
        )
    )

    response = await provider().generate("Hello")

    assert response.text == "Xin chào"
    assert response.prompt_tokens == 100
    assert response.completion_tokens == 50
    assert response.total_tokens == 150
    assert response.provider == "gemini"
    assert response.finish_reason == "STOP"
    assert response.cost_usd == pytest.approx(0.0000225)


async def test_stream_yields_chunks_in_order(gemini_model: Mock) -> None:
    gemini_model.generate_content_async = AsyncMock(
        return_value=AsyncChunkStream(
            [
                SimpleNamespace(text="Xin", candidates=[]),
                SimpleNamespace(text=" chào", candidates=[SimpleNamespace(finish_reason="STOP")]),
            ]
        )
    )

    chunks = [chunk async for chunk in provider().stream("Hello")]

    assert [chunk.delta for chunk in chunks] == ["Xin", " chào"]
    assert chunks[-1].accumulated_text == "Xin chào"
    assert chunks[-1].finish_reason == "STOP"


async def test_embed_returns_dimensions(
    gemini_model: Mock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del gemini_model
    monkeypatch.setattr(
        "app.llm.providers.gemini_provider.genai.embed_content_async",
        AsyncMock(return_value={"embedding": [0.5, 0.25]}),
    )

    response = await provider().embed("gas")

    assert response.embedding == [0.5, 0.25]
    assert response.dimensions == 2
    assert response.model == "text-embedding-004"


async def test_calculate_cost_correctly(gemini_model: Mock) -> None:
    del gemini_model
    cost = provider().calculate_cost(input_tokens=1_000_000, output_tokens=1_000_000)

    assert cost == pytest.approx(0.375)


async def test_handles_quota_exceeded(gemini_model: Mock) -> None:
    gemini_model.generate_content_async = AsyncMock(
        side_effect=google_exceptions.ResourceExhausted("quota")
    )

    with pytest.raises(LLMQuotaExceededError):
        await provider().generate("Hello")


async def test_handles_rate_limit(gemini_model: Mock) -> None:
    gemini_model.generate_content_async = AsyncMock(
        side_effect=google_exceptions.TooManyRequests("rate")
    )

    with pytest.raises(LLMRateLimitError):
        await provider().generate("Hello")


async def test_handles_timeout(gemini_model: Mock) -> None:
    gemini_model.generate_content_async = AsyncMock(
        side_effect=google_exceptions.DeadlineExceeded("timeout")
    )

    with pytest.raises(LLMTimeoutError):
        await provider().generate("Hello")


async def test_handles_connection_error_after_retries(gemini_model: Mock) -> None:
    gemini_model.generate_content_async = AsyncMock(side_effect=RuntimeError("offline"))

    with pytest.raises(LLMConnectionError):
        await provider().generate("Hello")

    assert gemini_model.generate_content_async.await_count == 3


async def test_health_check_returns_true(gemini_model: Mock) -> None:
    gemini_model.generate_content_async = AsyncMock(return_value=SimpleNamespace(text="ok"))

    assert await provider().health_check() is True


async def test_health_check_returns_false(gemini_model: Mock) -> None:
    gemini_model.generate_content_async = AsyncMock(side_effect=RuntimeError("offline"))

    assert await provider().health_check() is False
