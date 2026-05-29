"""Ollama LLM provider for local development and demo mode."""

import json
import time
from collections.abc import AsyncIterator
from typing import Any

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.llm.base import BaseLLMProvider
from app.llm.exceptions import LLMConnectionError, LLMInvalidRequestError, LLMTimeoutError
from app.llm.schemas import EmbeddingResponse, LLMResponse, LLMStreamChunk


class OllamaProvider(BaseLLMProvider):
    """LLM provider using a local Ollama server."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen2.5:7b-instruct-q4_K_M",
        embed_model: str = "nomic-embed-text",
        timeout: int = 60,
    ) -> None:
        super().__init__(model)
        self.base_url = base_url.rstrip("/")
        self.embed_model = embed_model
        self.timeout = timeout

    @property
    def provider_name(self) -> str:
        """Provider identifier."""
        return "ollama"

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stop_sequences: list[str] | None = None,
        **kwargs: object,
    ) -> LLMResponse:
        """Generate completion via Ollama API."""
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
        raise LLMConnectionError("Ollama generation failed")

    async def _generate_once(
        self,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
        stop_sequences: list[str] | None,
    ) -> LLMResponse:
        """Run one Ollama generation attempt."""
        start = time.monotonic()
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "stop": stop_sequences or [],
            },
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            self.logger.warning("ollama_timeout", error=str(exc))
            raise LLMTimeoutError(f"Ollama request timed out: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            self.logger.error("ollama_http_error", status=exc.response.status_code)
            raise LLMInvalidRequestError(
                f"Ollama returned {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            self.logger.warning("ollama_connection_error", error=str(exc))
            raise LLMConnectionError(f"Cannot connect to Ollama: {exc}") from exc

        latency_ms = int((time.monotonic() - start) * 1000)
        prompt_tokens = int(data.get("prompt_eval_count", 0))
        completion_tokens = int(data.get("eval_count", 0))
        return LLMResponse(
            text=str(data["response"]),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=latency_ms,
            model=self.model,
            provider=self.provider_name,
            finish_reason="stop" if data.get("done") else "length",
            cost_usd=0.0,
        )

    async def stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: object,
    ) -> AsyncIterator[LLMStreamChunk]:
        """Stream completion chunks from Ollama."""
        del kwargs
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        if system_prompt:
            payload["system"] = system_prompt

        accumulated = ""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        data = json.loads(line)
                        delta = str(data.get("response", ""))
                        accumulated += delta
                        yield LLMStreamChunk(
                            delta=delta,
                            finish_reason="stop" if data.get("done") else None,
                            accumulated_text=accumulated,
                        )
        except httpx.TimeoutException as exc:
            raise LLMTimeoutError(f"Ollama stream timed out: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise LLMInvalidRequestError(
                f"Ollama returned {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise LLMConnectionError(f"Stream failed: {exc}") from exc

    async def embed(self, text: str) -> EmbeddingResponse:
        """Generate embeddings via Ollama."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.embed_model, "prompt": text},
                )
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise LLMTimeoutError(f"Ollama embedding timed out: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise LLMInvalidRequestError(
                f"Ollama returned {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise LLMConnectionError(f"Embedding failed: {exc}") from exc

        embedding = [float(value) for value in data["embedding"]]
        return EmbeddingResponse(
            embedding=embedding,
            dimensions=len(embedding),
            model=self.embed_model,
        )

    async def health_check(self) -> bool:
        """Check if Ollama server is running."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except httpx.HTTPError:
            return False
