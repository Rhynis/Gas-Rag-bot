"""Hybrid intent classifier combining embedding and LLM results."""

from collections.abc import Mapping, Sequence

from app.intent.base import BaseIntentClassifier
from app.intent.categories import IntentCategory
from app.intent.schemas import IntentResult


class HybridIntentClassifier(BaseIntentClassifier):
    """Use embeddings first, with LLM fallback for uncertain or safety cases."""

    def __init__(
        self,
        embedding_classifier: BaseIntentClassifier,
        llm_classifier: BaseIntentClassifier,
        confidence_threshold: float = 0.7,
    ) -> None:
        self.embedding_classifier = embedding_classifier
        self.llm_classifier = llm_classifier
        self.confidence_threshold = confidence_threshold

    async def classify(
        self,
        text: str,
        conversation_history: Sequence[Mapping[str, str]] | None = None,
    ) -> IntentResult:
        """Classify with embedding, then double-check when required."""
        embedding_result = await self.embedding_classifier.classify(text, conversation_history)
        must_check_llm = (
            embedding_result.category == IntentCategory.SAFETY_EMERGENCY
            or embedding_result.confidence < self.confidence_threshold
        )
        if not must_check_llm:
            return IntentResult(
                category=embedding_result.category,
                confidence=embedding_result.confidence,
                reasoning=embedding_result.reasoning,
                classifier="hybrid_embedding",
            )

        llm_result = await self.llm_classifier.classify(text, conversation_history)
        if (
            embedding_result.category == IntentCategory.SAFETY_EMERGENCY
            or llm_result.category == IntentCategory.SAFETY_EMERGENCY
        ):
            return IntentResult(
                category=IntentCategory.SAFETY_EMERGENCY,
                confidence=max(embedding_result.confidence, llm_result.confidence),
                reasoning="Safety emergency confirmed by hybrid double-check",
                classifier="hybrid_safety",
            )

        return IntentResult(
            category=llm_result.category,
            confidence=llm_result.confidence,
            reasoning=llm_result.reasoning,
            classifier="hybrid_llm",
        )
