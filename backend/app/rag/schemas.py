"""Schemas for RAG pipeline."""

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.llm.schemas import LLMResponse
from app.schemas.knowledge_base import KnowledgeCategory


class RetrievedDocument(BaseModel):
    """A document retrieved from knowledge base."""

    id: UUID
    title: str
    content: str
    category: str
    similarity: float = Field(ge=0, le=1)
    source_type: Literal["vector", "keyword", "hybrid", "bm25"]
    metadata: dict[str, Any] = Field(default_factory=dict)


class SafetyResult(BaseModel):
    """Result of safety check."""

    is_emergency: bool
    severity: Literal["none", "low", "medium", "critical"]
    suggested_action: Literal["normal_response", "emergency_response", "escalate"]
    detected_via: Literal["keyword", "llm", "combined", "none"]
    matched_pattern: str | None = None


class RAGResponse(BaseModel):
    """Full response from RAG pipeline."""

    answer: str
    sources: list[RetrievedDocument]
    query: str
    processed_query: str
    llm_response: LLMResponse | None = None
    retrieval_count: int
    is_safety_critical: bool
    safety_result: SafetyResult | None = None
    confidence_score: float = Field(ge=0, le=1)
    total_latency_ms: int


class RAGQueryRequest(BaseModel):
    """Request payload for a RAG query."""

    query: str = Field(min_length=1, max_length=1000)
    conversation_history: list[dict[str, str]] = Field(default_factory=list)
    category_filter: KnowledgeCategory | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    conversation_id: UUID | None = None


class RetrievalTestRequest(BaseModel):
    """Request payload for retrieval-only debugging."""

    query: str = Field(min_length=1, max_length=1000)
    category_filter: KnowledgeCategory | None = None
    top_k: int = Field(default=5, ge=1, le=20)
