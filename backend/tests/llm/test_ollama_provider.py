"""Tests for the Ollama LLM provider."""

import httpx
import pytest
from pytest_httpx import HTTPXMock, IteratorStream

from app.llm.exceptions import LLMConnectionError, LLMInvalidRequestError, LLMTimeoutError
from app.llm.providers.ollama_provider import OllamaProvider

pytestmark = pytest.mark.asyncio


def provider() -> OllamaProvider:
    return OllamaProvider(base_url="http://ollama.test", model="qwen-test", timeout=1)


async def test_generate_returns_response(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        method="POST",
        url="http://ollama.test/api/generate",
        json={
            "response": "Xin chào",
            "done": True,
            "prompt_eval_count": 12,
            "eval_count": 8,
        },
    )

    response = await provider().generate("Hello", system_prompt="Bạn là trợ lý")

    assert response.text == "Xin chào"
    assert response.prompt_tokens == 12
    assert response.completion_tokens == 8
    assert response.total_tokens == 20
    assert response.provider == "ollama"
    assert response.model == "qwen-test"
    assert response.finish_reason == "stop"
    assert response.cost_usd == 0.0


async def test_generate_handles_timeout(httpx_mock: HTTPXMock) -> None:
    for _ in range(3):
        httpx_mock.add_exception(httpx.TimeoutException("slow"))

    with pytest.raises(LLMTimeoutError):
        await provider().generate("Hello")


async def test_generate_handles_connection_error(httpx_mock: HTTPXMock) -> None:
    for _ in range(3):
        httpx_mock.add_exception(httpx.ConnectError("offline"))

    with pytest.raises(LLMConnectionError):
        await provider().generate("Hello")


async def test_generate_retries_3_times_on_timeout(httpx_mock: HTTPXMock) -> None:
    for _ in range(3):
        httpx_mock.add_exception(httpx.TimeoutException("slow"))

    with pytest.raises(LLMTimeoutError):
        await provider().generate("Hello")

    assert len(httpx_mock.get_requests()) == 3


async def test_generate_does_not_retry_on_invalid_request(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        method="POST",
        url="http://ollama.test/api/generate",
        status_code=400,
        text="bad prompt",
    )

    with pytest.raises(LLMInvalidRequestError):
        await provider().generate("Hello")

    assert len(httpx_mock.get_requests()) == 1


async def test_stream_yields_chunks_in_order(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        method="POST",
        url="http://ollama.test/api/generate",
        stream=IteratorStream(
            [
                b'{"response": "Xin", "done": false}\n',
                b'{"response": " chao", "done": false}\n',
                b'{"response": "!", "done": true}\n',
            ]
        ),
    )

    chunks = [chunk async for chunk in provider().stream("Hello")]

    assert [chunk.delta for chunk in chunks] == ["Xin", " chao", "!"]
    assert chunks[-1].finish_reason == "stop"


async def test_stream_accumulates_text_correctly(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        method="POST",
        url="http://ollama.test/api/generate",
        stream=IteratorStream(
            [
                b'{"response": "A", "done": false}\n',
                b'{"response": "B", "done": false}\n',
                b'{"response": "C", "done": true}\n',
            ]
        ),
    )

    chunks = [chunk async for chunk in provider().stream("Hello")]

    assert [chunk.accumulated_text for chunk in chunks] == ["A", "AB", "ABC"]


async def test_embed_returns_correct_dimensions(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        method="POST",
        url="http://ollama.test/api/embeddings",
        json={"embedding": [0.1, 0.2, 0.3]},
    )

    response = await provider().embed("gas")

    assert response.embedding == [0.1, 0.2, 0.3]
    assert response.dimensions == 3
    assert response.model == "nomic-embed-text"


async def test_health_check_returns_true_when_up(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="GET", url="http://ollama.test/api/tags", status_code=200)

    assert await provider().health_check() is True


async def test_health_check_returns_false_when_down(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(httpx.ConnectError("offline"))

    assert await provider().health_check() is False
