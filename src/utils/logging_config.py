"""Logging configuration."""

import logging
import sys
from typing import Any

from src.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """Configure application logging."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Configure root logger with cleaner format
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    # Silence third-party loggers completely
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    logging.getLogger("requests").setLevel(logging.CRITICAL)
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)
    logging.getLogger("sqlalchemy").setLevel(logging.CRITICAL)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.CRITICAL)
    logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.CRITICAL)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.CRITICAL)
    logging.getLogger("sqlalchemy.dialects").setLevel(logging.CRITICAL)
    logging.getLogger("sqlalchemy.orm").setLevel(logging.CRITICAL)
    logging.getLogger("playwright").setLevel(logging.CRITICAL)
    
    # Disable SQLAlchemy echo completely
    logging.getLogger("sqlalchemy.engine.Engine").propagate = False


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
