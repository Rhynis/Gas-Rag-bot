"""FastAPI dependencies for LLM providers and prompt libraries."""

from functools import lru_cache
from pathlib import Path

from app.llm.base import BaseLLMProvider
from app.llm.factory import LLMProviderFactory
from app.llm.observability import LLMObservability
from app.llm.prompts.templates import PromptLibrary


def get_llm_provider() -> BaseLLMProvider:
    """Return the configured cached LLM provider."""
    return LLMProviderFactory.create()


@lru_cache(maxsize=1)
def get_observability() -> LLMObservability:
    """Return a cached observability wrapper."""
    return LLMObservability()


@lru_cache(maxsize=1)
def get_prompt_library() -> PromptLibrary:
    """Return a cached prompt library loaded from bundled templates."""
    library = PromptLibrary()
    template_dir = Path(__file__).parent / "prompts" / "templates"
    library.load_from_directory(template_dir)
    return library
