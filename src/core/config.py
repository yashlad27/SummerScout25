"""Application configuration and settings."""

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = Field(
        default="postgresql+psycopg://user:password@localhost:5432/job_tracker"
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")

    # Notifications
    slack_webhook_url: str | None = None
    smtp_server: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_pass: str | None = None
    smtp_from: str | None = None
    smtp_to: str | None = None
    pushover_token: str | None = None
    pushover_user: str | None = None

    # Scraping
    playwright_headless: bool = True
    requests_timeout: int = 25
    http_max_rps: float = 2.0

    # Sentry
    sentry_dsn: str | None = None

    # General
    environment: str = "development"
    log_level: str = "INFO"

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure database URL uses psycopg (not psycopg2)."""
        if "postgresql://" in v:
            v = v.replace("postgresql://", "postgresql+psycopg://")
        return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


class ConfigLoader:
    """Load and manage YAML configuration files."""

    def __init__(self, config_dir: Path | None = None):
        if config_dir is None:
            # Default to project root/config
            project_root = Path(__file__).parent.parent.parent
            config_dir = project_root / "config"
        self.config_dir = Path(config_dir)

    def load_yaml(self, filename: str) -> dict[str, Any]:
        """Load a YAML configuration file."""
        filepath = self.config_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def load_watchlist(self) -> dict[str, Any]:
        """Load watchlist.yaml configuration."""
        return self.load_yaml("watchlist.yaml")

    def load_filters(self) -> dict[str, Any]:
        """Load filters.yaml configuration."""
        return self.load_yaml("filters.yaml")


@lru_cache()
def get_config_loader() -> ConfigLoader:
    """Get cached config loader instance."""
    return ConfigLoader()
