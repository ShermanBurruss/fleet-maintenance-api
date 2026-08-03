"""Database connection and session configuration.

This module configures SQLAlchemy using the database connection
information supplied through application environment settings.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


# Create the SQLAlchemy engine using configuration loaded from the
# environment rather than credentials stored directly in source code.
engine = create_engine(
    settings.database_url
)


# SessionLocal creates database sessions used by API requests.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """Base class inherited by all SQLAlchemy ORM models."""

    pass


def get_db() -> Generator[Session, None, None]:
    """Provide a database session for a single API request.

    The session is always closed after the request completes, whether
    the request succeeds or raises an exception.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()