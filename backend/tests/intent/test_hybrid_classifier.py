"""Tests for hybrid intent classifier."""

import pytest

from app.intent.base import BaseIntentClassifier
from app.intent.categories import IntentCategory
from app.intent.classifiers.hybrid_classifier import HybridIntentClassifier
from app.intent.schemas import IntentResult


class StaticClassifier(BaseIntentClassifier):
    def __init__(self, result: IntentResult) -> None:
        self.result = result
        self.calls = 0

    async def classify(self, text: str, conversation_history=None) -> IntentResult:  # type: ignore[no-untyped-def]
        del text, conversation_history
        self.calls += 1
        return self.result


def result(category: IntentCategory, confidence: float, classifier: str) -> IntentResult:
    return IntentResult(
        category=category,
        confidence=confidence,
        reasoning="test",
        classifier=classifier,
    )


@pytest.mark.asyncio
async def test_high_confidence_embedding_short_circuits_llm() -> None:
    embedding = StaticClassifier(result(IntentCategory.PRODUCT_INQUIRY, 0.91, "embedding"))
    llm = StaticClassifier(result(IntentCategory.GENERAL_INFO, 0.9, "llm"))
    classifier = HybridIntentClassifier(embedding, llm, confidence_threshold=0.7)

    classified = await classifier.classify("Gia gas?")

    assert classified.category == IntentCategory.PRODUCT_INQUIRY
    assert llm.calls == 0


@pytest.mark.asyncio
async def test_low_confidence_uses_llm() -> None:
    embedding = StaticClassifier(result(IntentCategory.PRODUCT_INQUIRY, 0.5, "embedding"))
    llm = StaticClassifier(result(IntentCategory.PLACE_ORDER, 0.82, "llm"))
    classifier = HybridIntentClassifier(embedding, llm, confidence_threshold=0.7)

    classified = await classifier.classify("Toi muon mua")

    assert classified.category == IntentCategory.PLACE_ORDER
    assert llm.calls == 1


@pytest.mark.asyncio
async def test_safety_emergency_always_double_checks_llm() -> None:
    embedding = StaticClassifier(result(IntentCategory.SAFETY_EMERGENCY, 0.95, "embedding"))
    llm = StaticClassifier(result(IntentCategory.TECHNICAL_ISSUE, 0.8, "llm"))
    classifier = HybridIntentClassifier(embedding, llm, confidence_threshold=0.7)

    classified = await classifier.classify("Co mui gas")

    assert classified.category == IntentCategory.SAFETY_EMERGENCY
    assert llm.calls == 1


@pytest.mark.asyncio
async def test_llm_safety_overrides_embedding() -> None:
    embedding = StaticClassifier(result(IntentCategory.TECHNICAL_ISSUE, 0.4, "embedding"))
    llm = StaticClassifier(result(IntentCategory.SAFETY_EMERGENCY, 0.93, "llm"))
    classifier = HybridIntentClassifier(embedding, llm, confidence_threshold=0.7)

    classified = await classifier.classify("Ngui mui la")

    assert classified.category == IntentCategory.SAFETY_EMERGENCY
