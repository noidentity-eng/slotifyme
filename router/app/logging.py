"""Logging configuration for the Router service."""

import sys
import uuid
from typing import Any, Dict

import structlog
from fastapi import Request
from structlog.types import Processor


def add_request_id(_, __, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add request ID to log entries."""
    request_id = getattr(structlog.contextvars, "request_id", None)
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def setup_logging() -> None:
    """Configure structured logging."""
    processors: list[Processor] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        add_request_id,
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def set_request_id(request_id: str) -> None:
    """Set request ID in context for logging."""
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)


def get_request_id() -> str:
    """Get current request ID from context."""
    return getattr(structlog.contextvars, "request_id", str(uuid.uuid4()))


# Initialize logging on module import
setup_logging()
