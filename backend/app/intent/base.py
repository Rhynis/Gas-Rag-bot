"""Base classes for intent classifiers."""

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence

from app.intent.schemas import IntentResult


class BaseIntentClassifier(ABC):
    """Abstract contract for classifying customer intent."""

    @abstractmethod
    async def classify(
        self,
        text: str,
        conversation_history: Sequence[Mapping[str, str]] | None = None,
    ) -> IntentResult:
        """Classify text into one intent category."""
