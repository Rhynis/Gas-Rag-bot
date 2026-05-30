"""Schemas for RAG evaluation reports."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class TestCase(BaseModel):
    """One evaluation test case."""

    id: str
    query: str
    is_safety_critical: bool | None = None
    expected_keywords: list[str] = Field(default_factory=list)
    expected_category: str | None = None


class EvaluationMetrics(BaseModel):
    """Aggregate evaluation metrics."""

    total_cases: int
    safety_detection_rate: float = Field(ge=0, le=1)
    false_positive_rate: float = Field(ge=0, le=1)
    context_precision: float = Field(default=0.0, ge=0, le=1)
    context_recall: float = Field(default=0.0, ge=0, le=1)
    faithfulness: float = Field(default=0.0, ge=0, le=1)
    answer_relevancy: float = Field(default=0.0, ge=0, le=1)
    intent_accuracy: float | None = Field(default=None, ge=0, le=1)
    intent_macro_f1: float | None = Field(default=None, ge=0, le=1)
    per_intent_f1: dict[str, float] = Field(default_factory=dict)


class EvaluationReport(BaseModel):
    """Serializable report for an evaluation run."""

    suite_name: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metrics: EvaluationMetrics
    failed_case_ids: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
