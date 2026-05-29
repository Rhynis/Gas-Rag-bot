"""Embedding-based Vietnamese intent classifier."""

from collections.abc import Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

from app.intent.base import BaseIntentClassifier
from app.intent.categories import INTENT_EXAMPLES, IntentCategory
from app.intent.schemas import IntentResult
from app.rag.embeddings import EmbeddingService


class EmbeddingIntentClassifier(BaseIntentClassifier):
    """Classify intents by comparing query embeddings to example centroids."""

    def __init__(self, embedding_service: EmbeddingService) -> None:
        self.embedding_service = embedding_service
        self._centroids: dict[IntentCategory, NDArray[np.float32]] | None = None

    async def classify(
        self,
        text: str,
        conversation_history: Sequence[Mapping[str, str]] | None = None,
    ) -> IntentResult:
        """Return the closest example centroid."""
        del conversation_history
        centroids = await self._get_centroids()
        query_vector = np.asarray(await self.embedding_service.embed_text(text), dtype=np.float32)

        best_category = IntentCategory.GENERAL_INFO
        best_score = -1.0
        for category, centroid in centroids.items():
            score = self._cosine_similarity(query_vector, centroid)
            if score > best_score:
                best_category = category
                best_score = score

        confidence = max(0.0, min(1.0, float(best_score)))
        return IntentResult(
            category=best_category,
            confidence=confidence,
            reasoning=f"Nearest example centroid matched {best_category.value}",
            classifier="embedding",
        )

    async def _get_centroids(self) -> dict[IntentCategory, NDArray[np.float32]]:
        if self._centroids is not None:
            return self._centroids

        centroids: dict[IntentCategory, NDArray[np.float32]] = {}
        for category, examples in INTENT_EXAMPLES.items():
            embeddings = await self.embedding_service.embed_batch(examples)
            matrix = np.asarray(embeddings, dtype=np.float32)
            centroids[category] = matrix.mean(axis=0)
        self._centroids = centroids
        return centroids

    @staticmethod
    def _cosine_similarity(left: NDArray[np.float32], right: NDArray[np.float32]) -> float:
        denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
        if denominator == 0:
            return 0.0
        return float(np.dot(left, right) / denominator)
