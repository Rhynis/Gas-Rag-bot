"""Tests for LLM intent classifier."""

import pytest

from app.intent.categories import IntentCategory
from app.intent.classifiers.llm_classifier import LLMIntentClassifier
from app.llm.exceptions import LLMParsingError
from app.llm.prompts.templates import PromptLibrary, PromptTemplate
from app.llm.schemas import LLMResponse


class FakeLLMProvider:
    provider_name = "fake"
    model = "fake-model"

    def __init__(self, text: str) -> None:
        self.text = text
        self.temperature: float | None = None

    async def generate(self, prompt: str, **kwargs: object) -> LLMResponse:
        del prompt
        self.temperature = kwargs.get("temperature")  # type: ignore[assignment]
        return LLMResponse(
            text=self.text,
            latency_ms=1,
            model=self.model,
            provider=self.provider_name,
        )


def make_prompt_library() -> PromptLibrary:
    library = PromptLibrary()
    library._templates["intent_classification_vi"] = PromptTemplate("${query}")
    return library


@pytest.mark.asyncio
async def test_parses_valid_json_response() -> None:
    provider = FakeLLMProvider(
        '{"intent":"delivery_status","confidence":0.88,"reasoning":"tracking"}'
    )
    classifier = LLMIntentClassifier(provider, make_prompt_library())  # type: ignore[arg-type]

    result = await classifier.classify("Don toi den dau roi?")

    assert result.category == IntentCategory.DELIVERY_STATUS
    assert result.confidence == 0.88
    assert provider.temperature == 0.0


@pytest.mark.asyncio
async def test_rejects_invalid_json() -> None:
    provider = FakeLLMProvider("not json")
    classifier = LLMIntentClassifier(provider, make_prompt_library())  # type: ignore[arg-type]

    with pytest.raises(LLMParsingError):
        await classifier.classify("hello")


@pytest.mark.asyncio
async def test_rejects_unknown_intent() -> None:
    provider = FakeLLMProvider('{"intent":"unknown","confidence":0.9,"reasoning":"x"}')
    classifier = LLMIntentClassifier(provider, make_prompt_library())  # type: ignore[arg-type]

    with pytest.raises(LLMParsingError):
        await classifier.classify("hello")


@pytest.mark.asyncio
async def test_uses_configured_prompt_template() -> None:
    provider = FakeLLMProvider('{"intent":"general_info","confidence":0.7,"reasoning":"general"}')
    classifier = LLMIntentClassifier(provider, make_prompt_library())  # type: ignore[arg-type]

    result = await classifier.classify("Mo cua may gio?")

    assert result.category == IntentCategory.GENERAL_INFO
