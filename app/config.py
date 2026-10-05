"""Application configuration loaded from environment variables.

Enum ownership: `environment` values (development/staging/production) are owned by
ARCHITECTURE.md. This module only reads the value; it does not invent new values.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

VALID_ENVIRONMENTS = {"development", "staging", "production"}


@dataclass(frozen=True)
class Settings:
    app_env: str
    database_url: str
    company_ai_endpoint: str | None
    company_ai_api_key: str | None
    company_ai_model: str | None

    @property
    def ai_configured(self) -> bool:
        return bool(self.company_ai_endpoint and self.company_ai_api_key)


def load_settings() -> Settings:
    app_env = os.environ.get("APP_ENV", "development")
    if app_env not in VALID_ENVIRONMENTS:
        # Do not invent a new enum value; fall back to the documented default
        # rather than silently accepting an unknown environment name.
        app_env = "development"

    database_url = os.environ.get("DATABASE_URL", "sqlite:///./data/app.db")

    return Settings(
        app_env=app_env,
        database_url=database_url,
        company_ai_endpoint=os.environ.get("COMPANY_AI_ENDPOINT") or None,
        company_ai_api_key=os.environ.get("COMPANY_AI_API_KEY") or None,
        company_ai_model=os.environ.get("COMPANY_AI_MODEL") or None,
    )
