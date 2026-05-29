"""Langfuse observability wrapper for LLM calls."""

from typing import Any, Protocol, cast

from langfuse import Langfuse

from app.core.config import get_settings
from app.core.logging import get_logger
from app.llm.schemas import LLMResponse


class _LangfuseClient(Protocol):
    def generation(self, **kwargs: object) -> object:
        """Record a generation event."""

    def trace(self, **kwargs: object) -> object:
        """Create a trace."""

    def flush(self) -> None:
        """Flush pending events."""


class LLMObservability:
    """Wraps LLM calls with Langfuse tracking."""

    def __init__(self, langfuse: _LangfuseClient | None = None) -> None:
        settings = get_settings()
        self.logger = get_logger(__name__)
        self.langfuse: _LangfuseClient | None
        if langfuse is not None:
            self.langfuse = langfuse
            self.enabled = True
        elif settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
            self.langfuse = cast(
                _LangfuseClient,
                Langfuse(
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    host=settings.LANGFUSE_HOST,
                ),
            )
            self.enabled = True
        else:
            self.langfuse = None
            self.enabled = False
            self.logger.warning("langfuse_not_configured")

    async def track_generation(
        self,
        provider: str,
        model: str,
        prompt: str,
        system_prompt: str | None,
        response: LLMResponse,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Track an LLM generation without failing the caller."""
        if not self.enabled or self.langfuse is None:
            return

        try:
            self.langfuse.generation(
                name=f"{provider}_generation",
                model=model,
                input={"prompt": prompt, "system_prompt": system_prompt},
                output=response.text,
                metadata={
                    **(metadata or {}),
                    "provider": provider,
                    "latency_ms": response.latency_ms,
                    "cost_usd": response.cost_usd,
                    "finish_reason": response.finish_reason,
                },
                usage={
                    "input": response.prompt_tokens,
                    "output": response.completion_tokens,
                    "total": response.total_tokens,
                    "unit": "TOKENS",
                },
            )
        except (RuntimeError, ValueError, TypeError, AttributeError) as exc:
            self.logger.error("langfuse_tracking_failed", error=str(exc))

    def create_trace(
        self,
        name: str,
        user_id: str | None = None,
        **kwargs: object,
    ) -> object | None:
        """Create a trace to group related operations."""
        if not self.enabled or self.langfuse is None:
            return None
        return self.langfuse.trace(name=name, user_id=user_id, **kwargs)

    async def flush(self) -> None:
        """Flush pending events."""
        if self.enabled and self.langfuse is not None:
            self.langfuse.flush()
