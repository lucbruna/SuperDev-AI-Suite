from __future__ import annotations

import contextvars
import logging
import sys
from typing import Any

from pythonjsonlogger import jsonlogger

from {{project_name}}.config import get_settings


_request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)
_user_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("user_id", default=None)


class RequestIdFilter(logging.Filter):
    """Add request ID to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        request_id = _request_id_var.get()
        user_id = _user_id_var.get()
        
        if request_id:
            record.request_id = request_id
        if user_id:
            record.user_id = user_id
        
        return True


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


def set_request_id(request_id: str) -> None:
    """Set the request ID for the current context."""
    _request_id_var.set(request_id)


def get_request_id() -> str | None:
    """Get the current request ID."""
    return _request_id_var.get()


def set_user_id(user_id: str) -> None:
    """Set the user ID for the current context."""
    _user_id_var.set(user_id)


def get_user_id() -> str | None:
    """Get the current user ID."""
    return _user_id_var.get()


def setup_logging() -> None:
    """Configure application logging."""
    settings = get_settings()
    
    # Clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Add filter for request context
    handler.addFilter(RequestIdFilter())
    
    # Use JSON formatter in production, console in development
    if settings.is_production:
        formatter = jsonlogger.JsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s %(request_id)s %(user_id)s",
            timestamp=True,
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s "
            "[request_id=%(request_id)s] [user_id=%(user_id)s]",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.debug else logging.WARNING
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)