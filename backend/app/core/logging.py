"""Structured logging configuration using structlog."""

import logging
import sys
from typing import Any, cast

import structlog
from structlog.types import EventDict, WrappedLogger

from app.core.config import get_settings
from app.core.input_validation import PIIMasker


def _pii_masking_processor(
    logger: WrappedLogger,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Mask PII in structured log entries."""
    return PIIMasker.mask_dict(dict(event_dict))


def configure_logging() -> None:
    """Configure structlog based on environment."""
    settings = get_settings()

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
    )

    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        _pii_masking_processor,
    ]

    if settings.is_production:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.DEBUG if settings.DEBUG else logging.INFO
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a logger instance with the given name."""
    return cast(structlog.BoundLogger, structlog.get_logger(name))
