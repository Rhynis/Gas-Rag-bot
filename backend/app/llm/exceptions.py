"""Custom exceptions for LLM provider operations."""

from app.core.exceptions import GasBotException


class LLMProviderError(GasBotException):
    """Base exception for LLM provider failures."""

    status_code = 503
    error_code = "llm_provider_error"


class LLMConnectionError(LLMProviderError):
    """Network connection failed."""

    error_code = "llm_connection_error"


class LLMTimeoutError(LLMProviderError):
    """Provider request timed out."""

    error_code = "llm_timeout"


class LLMRateLimitError(LLMProviderError):
    """Provider rate limited the request."""

    error_code = "llm_rate_limited"


class LLMInvalidRequestError(LLMProviderError):
    """Provider rejected the request as invalid."""

    status_code = 400
    error_code = "llm_invalid_request"


class LLMQuotaExceededError(LLMProviderError):
    """Provider quota or free tier is exhausted."""

    status_code = 429
    error_code = "llm_quota_exceeded"


class LLMParsingError(LLMProviderError):
    """Provider response could not be parsed."""

    error_code = "llm_parsing_error"
