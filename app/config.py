"""Application configuration for the Fleet Maintenance API.

Configuration values are loaded from environment variables or the
project's local .env file. Sensitive configuration should never be
committed directly to source control.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Resolve the project-level .env file regardless of the current
# directory from which the application is started.
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """Validated configuration values used by the application."""

    database_url: str
    test_database_url: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Create one validated settings object for use throughout the application.
settings = Settings()