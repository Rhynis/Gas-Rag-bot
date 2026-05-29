"""LLM-backed intent classifier."""

import json
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import ValidationError

from app.intent.base import BaseIntentClassifier
from app.intent.categories import IntentCategory
from app.intent.schemas import IntentResult
from app.llm.base import BaseLLMProvider
from app.llm.exceptions import LLMParsingError
from app.llm.prompts.templates import PromptLibrary


class LLMIntentClassifier(BaseIntentClassifier):
    """Classify intents with the configured LLM provider."""

    def __init__(self, llm_provider: BaseLLMProvider, prompt_library: PromptLibrary) -> None:
        self.llm_provider = llm_provider
        self.prompt_library = prompt_library

    async def classify(
        self,
        text: str,
        conversation_history: Sequence[Mapping[str, str]] | None = None,
    ) -> IntentResult:
        """Ask the LLM for a strict JSON intent result."""
        del conversation_history
        prompt = self.prompt_library.get("intent_classification_vi").render(query=text)
        response = await self.llm_provider.generate(
            prompt=prompt,
            temperature=0.0,
            max_tokens=160,
        )
        return self._parse_response(response.text)

    def _parse_response(self, text: str) -> IntentResult:
        try:
            payload = json.loads(text.strip())
            return self._payload_to_result(payload)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, ValidationError) as exc:
            raise LLMParsingError("Could not parse intent classification response") from exc

    @staticmethod
    def _payload_to_result(payload: dict[str, Any]) -> IntentResult:
        return IntentResult(
            category=IntentCategory(payload["intent"]),
            confidence=float(payload["confidence"]),
            reasoning=str(payload.get("reasoning") or ""),
            classifier="llm",
        )
