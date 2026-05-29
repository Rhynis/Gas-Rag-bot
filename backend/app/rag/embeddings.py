"""Vietnamese text embedding service using SBERT."""

import asyncio
import unicodedata
from typing import Any, ClassVar, cast

import numpy as np

from app.core.logging import get_logger

SentenceTransformer: Any | None = None


class EmbeddingService:
    """Generate embeddings for Vietnamese text using a lazily loaded SBERT model."""

    _instance: ClassVar["EmbeddingService | None"] = None
    _model: ClassVar[Any | None] = None

    def __new__(cls, *args: object, **kwargs: object) -> "EmbeddingService":
        """Return the singleton service instance."""
        del args, kwargs
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model_name: str = "keepitreal/vietnamese-sbert") -> None:
        if not hasattr(self, "_initialized"):
            self.model_name = model_name
            self.logger = get_logger(__name__)
            self._initialized = True

    @classmethod
    def reset(cls) -> None:
        """Reset singleton state for tests."""
        cls._instance = None
        cls._model = None

    def _get_model(self) -> Any:
        """Load model lazily on first use."""
        if EmbeddingService._model is None:
            global SentenceTransformer
            if SentenceTransformer is None:
                from sentence_transformers import SentenceTransformer as LoadedSentenceTransformer

                SentenceTransformer = LoadedSentenceTransformer

            self.logger.info("loading_embedding_model", model=self.model_name)
            EmbeddingService._model = SentenceTransformer(self.model_name)
            self.logger.info("embedding_model_loaded")
        return EmbeddingService._model

    def _normalize_text(self, text: str) -> str:
        """Normalize Vietnamese text before embedding."""
        if not text:
            return ""
        normalized = unicodedata.normalize("NFC", text)
        normalized = " ".join(normalized.split())
        return normalized[:1500]

    async def embed_text(self, text: str) -> list[float]:
        """Embed one text in a thread pool."""
        normalized = self._normalize_text(text)
        if not normalized:
            return [0.0] * self.get_dimensions()

        loop = asyncio.get_running_loop()
        embedding = await loop.run_in_executor(
            None,
            lambda: self._get_model().encode(normalized, convert_to_numpy=True),
        )
        return cast(list[float], np.asarray(embedding, dtype=np.float32).tolist())

    async def embed_batch(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        """Embed multiple texts efficiently using batching in a thread pool."""
        if not texts:
            return []

        normalized = [self._normalize_text(text) for text in texts]
        loop = asyncio.get_running_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: self._get_model().encode(
                normalized,
                convert_to_numpy=True,
                batch_size=batch_size,
                show_progress_bar=False,
            ),
        )
        return [np.asarray(item, dtype=np.float32).tolist() for item in embeddings]

    def get_dimensions(self) -> int:
        """Return embedding dimensionality."""
        return 768
