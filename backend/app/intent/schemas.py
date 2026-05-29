"""Schemas for intent classification."""

from pydantic import BaseModel, Field

from app.intent.categories import IntentCategory


class IntentResult(BaseModel):
    """Result returned by an intent classifier."""

    category: IntentCategory
    confidence: float = Field(ge=0, le=1)
    reasoning: str
    classifier: str
