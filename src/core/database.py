"""Database session and base configuration."""

from contextlib import contextmanager
from typing import Generator
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from src.core.config import get_settings

settings = get_settings()

# Silence SQLAlchemy loggers BEFORE creating engine
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)
logging.getLogger('sqlalchemy.engine.Engine').setLevel(logging.CRITICAL)
logging.getLogger('sqlalchemy.pool').setLevel(logging.CRITICAL)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.CRITICAL)
logging.getLogger('sqlalchemy.orm').setLevel(logging.CRITICAL)

# Create engine with optimized pool settings for parallel scraping
engine = create_engine(
    settings.database_url,
    echo=False,  # Disable SQL logging for cleaner output
    pool_pre_ping=True,  # Verify connections before using
    pool_size=20,  # Larger pool for parallel operations (was 10)
    max_overflow=40,  # More overflow connections (was 20)
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_timeout=30,  # Wait up to 30 seconds for a connection
    connect_args={
        'connect_timeout': 10,  # Connection timeout
        'options': '-c statement_timeout=60000'  # 60 second query timeout
    }
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database sessions in non-FastAPI code."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
