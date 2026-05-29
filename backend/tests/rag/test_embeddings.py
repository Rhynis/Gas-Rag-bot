"""Tests for Vietnamese embedding service."""

import asyncio
from unittest.mock import MagicMock

import numpy as np
import pytest

from app.rag.embeddings import EmbeddingService

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def mock_sentence_transformer(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    EmbeddingService.reset()
    mock_model = MagicMock()

    def encode(value: object, **kwargs: object) -> np.ndarray:
        del kwargs
        if isinstance(value, list):
            return np.vstack(
                [np.full(768, index + 1, dtype=np.float32) for index, _ in enumerate(value)]
            )
        return np.full(768, 0.5, dtype=np.float32)

    mock_model.encode.side_effect = encode
    monkeypatch.setattr(
        "app.rag.embeddings.SentenceTransformer",
        lambda *args, **kwargs: mock_model,
    )
    yield mock_model
    EmbeddingService.reset()


async def test_embed_text_returns_768_dim_vector() -> None:
    embedding = await EmbeddingService().embed_text("Bình gas Petrolimex")

    assert len(embedding) == 768


async def test_embed_text_consistent() -> None:
    service = EmbeddingService()

    first = await service.embed_text("Bình gas Petrolimex")
    second = await service.embed_text("Bình gas Petrolimex")

    assert first == second


async def test_embed_batch_efficiency() -> None:
    embeddings = await EmbeddingService().embed_batch(["a", "b", "c"])

    assert len(embeddings) == 3
    assert all(len(embedding) == 768 for embedding in embeddings)


async def test_embed_handles_empty_text() -> None:
    embedding = await EmbeddingService().embed_text("")

    assert embedding == [0.0] * 768


async def test_embed_handles_long_text(mock_sentence_transformer: MagicMock) -> None:
    long_text = "gas " * 1000

    await EmbeddingService().embed_text(long_text)

    encoded_text = mock_sentence_transformer.encode.call_args.args[0]
    assert isinstance(encoded_text, str)
    assert len(encoded_text) <= 1500


async def test_embed_handles_vietnamese_diacritics() -> None:
    embedding = await EmbeddingService().embed_text("Bình gas Petrolimex")

    assert len(embedding) == 768


async def test_embed_singleton(mock_sentence_transformer: MagicMock) -> None:
    first = EmbeddingService()
    second = EmbeddingService()
    await asyncio.gather(first.embed_text("a"), second.embed_text("b"))

    assert first is second
    assert mock_sentence_transformer.encode.call_count == 2
