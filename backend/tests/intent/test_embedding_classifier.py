"""Tests for embedding intent classifier."""

import pytest

from app.intent.categories import INTENT_EXAMPLES, IntentCategory
from app.intent.classifiers.embedding_classifier import EmbeddingIntentClassifier


class FakeEmbeddingService:
    """Deterministic keyword vectors for tests."""

    async def embed_text(self, text: str) -> list[float]:
        return self._embed(text)

    async def embed_batch(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        del batch_size
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> list[float]:
        normalized = text.lower()
        categories = list(IntentCategory)
        vector = [0.0] * len(categories)
        keywords = {
            IntentCategory.PRODUCT_INQUIRY: ["gia", "loai", "petrolimex", "san pham"],
            IntentCategory.PLACE_ORDER: ["dat", "mua", "giao"],
            IntentCategory.DELIVERY_STATUS: ["don", "den dau", "khi nao", "shipper"],
            IntentCategory.COMPLAINT: ["khieu nai", "tho lo", "khong hai long", "thieu can"],
            IntentCategory.TECHNICAL_ISSUE: ["lap", "van", "bep", "lua"],
            IntentCategory.SAFETY_EMERGENCY: ["mui gas", "ro ri", "chay", "xi"],
            IntentCategory.PAYMENT_ISSUE: ["hoa don", "thanh toan", "vat", "tien"],
            IntentCategory.GENERAL_INFO: ["dia chi", "mo cua", "hotline", "khu vuc"],
        }
        for index, category in enumerate(categories):
            if any(keyword in normalized for keyword in keywords[category]):
                vector[index] = 1.0
        return vector


@pytest.mark.asyncio
async def test_classifies_product_inquiry() -> None:
    classifier = EmbeddingIntentClassifier(FakeEmbeddingService())  # type: ignore[arg-type]

    result = await classifier.classify("Gia binh gas Petrolimex 12kg?")

    assert result.category == IntentCategory.PRODUCT_INQUIRY
    assert result.confidence > 0.7


@pytest.mark.asyncio
async def test_classifies_safety_emergency() -> None:
    classifier = EmbeddingIntentClassifier(FakeEmbeddingService())  # type: ignore[arg-type]

    result = await classifier.classify("Toi ngui thay mui gas va nghi bi ro ri")

    assert result.category == IntentCategory.SAFETY_EMERGENCY


@pytest.mark.asyncio
async def test_examples_cover_all_intents_without_loading_model() -> None:
    classifier = EmbeddingIntentClassifier(FakeEmbeddingService())  # type: ignore[arg-type]

    for category, examples in INTENT_EXAMPLES.items():
        result = await classifier.classify(examples[0])
        assert result.category == category


@pytest.mark.asyncio
async def test_empty_vector_returns_bounded_confidence() -> None:
    classifier = EmbeddingIntentClassifier(FakeEmbeddingService())  # type: ignore[arg-type]

    result = await classifier.classify("...")

    assert 0 <= result.confidence <= 1


@pytest.mark.asyncio
async def test_centroids_are_cached() -> None:
    service = FakeEmbeddingService()
    classifier = EmbeddingIntentClassifier(service)  # type: ignore[arg-type]

    await classifier.classify("Gia gas")
    first_centroids = classifier._centroids
    await classifier.classify("Gia gas")

    assert classifier._centroids is first_centroids
