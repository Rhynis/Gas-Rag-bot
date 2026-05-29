"""Pydantic schemas for LLM operations."""

from typing import Literal

from pydantic import BaseModel


class Message(BaseModel):
    """A single message in a conversation."""

    role: Literal["system", "user", "assistant"]
    content: str


class LLMResponse(BaseModel):
    """Response from an LLM generation call."""

    text: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    latency_ms: int
    model: str
    provider: str
    finish_reason: str | None = None
    cost_usd: float | None = None


class LLMStreamChunk(BaseModel):
    """A single chunk from a streaming generation."""

    delta: str
    finish_reason: str | None = None
    accumulated_text: str


class EmbeddingResponse(BaseModel):
    """Response from an embedding call."""

    embedding: list[float]
    dimensions: int
    model: str
