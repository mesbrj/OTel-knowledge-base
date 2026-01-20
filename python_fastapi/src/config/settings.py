"""
Application settings and configuration management.
Uses pydantic-settings to load configuration from environment variables.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    APP_URL: str
    ENVIRONMENT: str

    PSQL_DATABASE_URL: str
    DEV_SQLITE_URL: str
    TEST_SQLITE_URL: str
    DEBUG_SQLALCHEMY: str

    OTEL_EXPORTER_OTLP_ENDPOINT: str

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        validate_assignment=True
    )

settings = Settings()
