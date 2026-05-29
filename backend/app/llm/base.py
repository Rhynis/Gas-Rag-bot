"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.core.logging import get_logger
from app.llm.schemas import EmbeddingResponse, LLMResponse, LLMStreamChunk


class BaseLLMProvider(ABC):
    """Abstract base for all LLM providers."""

    def __init__(self, model: str) -> None:
        self.model = model
        self.logger = get_logger(self.__class__.__name__)

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider identifier."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stop_sequences: list[str] | None = None,
        **kwargs: object,
    ) -> LLMResponse:
        """Generate a text completion."""

    @abstractmethod
    def stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: object,
    ) -> AsyncIterator[LLMStreamChunk]:
        """Stream a text completion chunk by chunk."""

    async def embed(self, text: str) -> EmbeddingResponse:
        """Generate embedding for text. Optional method."""
        raise NotImplementedError(f"{self.provider_name} does not support embeddings")

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is reachable and responding."""

    def estimate_tokens(self, text: str) -> int:
        """Return a rough token count estimate for Vietnamese text."""
        return len(text) // 3
