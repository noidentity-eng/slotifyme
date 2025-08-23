"""Logging configuration with structured logging and OpenTelemetry."""

import logging
import sys
from typing import Any, Dict
import structlog
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from tenant.app.config import settings


def setup_logging() -> None:
    """Setup structured logging with OpenTelemetry."""
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )


def setup_telemetry() -> None:
    """Setup OpenTelemetry tracing."""
    # Create tracer provider
    tracer_provider = TracerProvider()
    
    # Add console exporter for development
    console_exporter = ConsoleSpanExporter()
    tracer_provider.add_span_processor(BatchSpanProcessor(console_exporter))
    
    # Set the tracer provider
    trace.set_tracer_provider(tracer_provider)
    
    return tracer_provider


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_request_id(request_id: str) -> Dict[str, Any]:
    """Create a context dict with request ID for logging."""
    return {"request_id": request_id}


# Initialize logging and telemetry
setup_logging()
setup_telemetry()

# Global logger
logger = get_logger(__name__)
