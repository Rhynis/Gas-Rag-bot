"""Google Gemini LLM provider for production deployment."""

import time
from collections.abc import AsyncIterator
from typing import Any, ClassVar, cast

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.llm.base import BaseLLMProvider
from app.llm.exceptions import (
    LLMConnectionError,
    LLMInvalidRequestError,
    LLMQuotaExceededError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from app.llm.schemas import EmbeddingResponse, LLMResponse, LLMStreamChunk


class GeminiProvider(BaseLLMProvider):
    """LLM provider using Google Gemini Flash API."""

    PRICING_PER_1M: ClassVar[dict[str, dict[str, float]]] = {
        "gemini-2.0-flash-exp": {"input": 0.075, "output": 0.30},
        "gemini-2.0-flash": {"input": 0.075, "output": 0.30},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    }

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-exp",
        embed_model: str = "text-embedding-004",
    ) -> None:
        super().__init__(model)
        self.embed_model = embed_model
        genai.configure(api_key=api_key)
        self._client = genai.GenerativeModel(model)

    @property
    def provider_name(self) -> str:
        """Provider identifier."""
        return "gemini"

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate generation cost in USD."""
        pricing = self.PRICING_PER_1M.get(self.model, {"input": 0.0, "output": 0.0})
        return (
            input_tokens / 1_000_000 * pricing["input"]
            + output_tokens / 1_000_000 * pricing["output"]
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stop_sequences: list[str] | None = None,
        **kwargs: object,
    ) -> LLMResponse:
        """Generate completion via Gemini API."""
        del kwargs
        async for attempt in AsyncRetrying(
            retry=retry_if_exception_type((LLMConnectionError, LLMTimeoutError)),
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=0.1, min=0.1, max=1),
            reraise=True,
        ):
            with attempt:
                return await self._generate_once(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stop_sequences=stop_sequences,
                )
        raise LLMConnectionError("Gemini generation failed")

    async def _generate_once(
        self,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
        stop_sequences: list[str] | None,
    ) -> LLMResponse:
        """Run one Gemini generation attempt."""
        start = time.monotonic()
        model = (
            genai.GenerativeModel(self.model, system_instruction=system_prompt)
            if system_prompt
            else self._client
        )
        config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            stop_sequences=stop_sequences or [],
        )

        try:
            response = await model.generate_content_async(prompt, generation_config=config)
        except google_exceptions.ResourceExhausted as exc:
            raise LLMQuotaExceededError(f"Gemini quota exceeded: {exc}") from exc
        except google_exceptions.TooManyRequests as exc:
            raise LLMRateLimitError(f"Gemini rate limited: {exc}") from exc
        except google_exceptions.DeadlineExceeded as exc:
            raise LLMTimeoutError(f"Gemini timeout: {exc}") from exc
        except google_exceptions.InvalidArgument as exc:
            raise LLMInvalidRequestError(f"Gemini invalid request: {exc}") from exc
        except (google_exceptions.GoogleAPIError, RuntimeError) as exc:
            raise LLMConnectionError(f"Gemini error: {exc}") from exc

        latency_ms = int((time.monotonic() - start) * 1000)
        usage = getattr(response, "usage_metadata", None)
        prompt_tokens = int(getattr(usage, "prompt_token_count", 0) or 0)
        completion_tokens = int(getattr(usage, "candidates_token_count", 0) or 0)
        candidates = list(getattr(response, "candidates", []) or [])
        finish_reason = str(getattr(candidates[0], "finish_reason", "")) if candidates else None
        return LLMResponse(
            text=str(getattr(response, "text", "")),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=latency_ms,
            model=self.model,
            provider=self.provider_name,
            finish_reason=finish_reason,
            cost_usd=self.calculate_cost(prompt_tokens, completion_tokens),
        )

    async def stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: object,
    ) -> AsyncIterator[LLMStreamChunk]:
        """Stream generation chunks from Gemini."""
        del kwargs
        model = (
            genai.GenerativeModel(self.model, system_instruction=system_prompt)
            if system_prompt
            else self._client
        )
        config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        accumulated = ""
        try:
            response_stream = await model.generate_content_async(
                prompt,
                generation_config=config,
                stream=True,
            )
            async for chunk in response_stream:
                delta = str(getattr(chunk, "text", ""))
                accumulated += delta
                candidates = list(getattr(chunk, "candidates", []) or [])
                finish_reason = (
                    str(getattr(candidates[0], "finish_reason", "")) if candidates else None
                )
                yield LLMStreamChunk(
                    delta=delta,
                    finish_reason=finish_reason,
                    accumulated_text=accumulated,
                )
        except google_exceptions.ResourceExhausted as exc:
            raise LLMQuotaExceededError(f"Gemini quota exceeded: {exc}") from exc
        except google_exceptions.TooManyRequests as exc:
            raise LLMRateLimitError(f"Gemini rate limited: {exc}") from exc
        except google_exceptions.DeadlineExceeded as exc:
            raise LLMTimeoutError(f"Gemini timeout: {exc}") from exc
        except google_exceptions.InvalidArgument as exc:
            raise LLMInvalidRequestError(f"Gemini invalid request: {exc}") from exc
        except (google_exceptions.GoogleAPIError, RuntimeError) as exc:
            raise LLMConnectionError(f"Gemini stream failed: {exc}") from exc

    async def embed(self, text: str) -> EmbeddingResponse:
        """Generate embeddings via Gemini."""
        try:
            response = await genai.embed_content_async(model=self.embed_model, content=text)
        except google_exceptions.ResourceExhausted as exc:
            raise LLMQuotaExceededError(f"Gemini quota exceeded: {exc}") from exc
        except google_exceptions.TooManyRequests as exc:
            raise LLMRateLimitError(f"Gemini rate limited: {exc}") from exc
        except (google_exceptions.GoogleAPIError, RuntimeError) as exc:
            raise LLMConnectionError(f"Gemini embedding failed: {exc}") from exc

        embedding = [float(value) for value in cast(dict[str, Any], response)["embedding"]]
        return EmbeddingResponse(
            embedding=embedding,
            dimensions=len(embedding),
            model=self.embed_model,
        )

    async def health_check(self) -> bool:
        """Check whether Gemini responds to a tiny request."""
        try:
            response = await self._client.generate_content_async(
                "test",
                generation_config=genai.types.GenerationConfig(max_output_tokens=5),
            )
            return getattr(response, "text", None) is not None
        except (google_exceptions.GoogleAPIError, RuntimeError):
            return False
