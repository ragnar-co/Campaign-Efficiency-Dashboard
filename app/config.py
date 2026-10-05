"""Application configuration loaded from environment variables.

Enum ownership: `environment` values (development/staging/production) are owned by
ARCHITECTURE.md. This module only reads the value; it does not invent new values.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Local-dev convenience only: fills in any var not already set in the real
# environment (override=False, the default) — never overrides Coolify/CI
# environment variables, and silently no-ops if no .env file is present.
load_dotenv()

VALID_ENVIRONMENTS = {"development", "staging", "production"}


DEFAULT_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL = "anthropic/claude-sonnet-4.6"


@dataclass(frozen=True)
class Settings:
    app_env: str
    database_url: str
    openrouter_api_key: str | None
    openrouter_base_url: str
    openrouter_model: str

    @property
    def ai_configured(self) -> bool:
        # Base URL/model have safe non-secret defaults; only the API key gates
        # whether the AI bonus is usable.
        return bool(self.openrouter_api_key)


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
        openrouter_api_key=os.environ.get("OPENROUTER_API_KEY") or None,
        openrouter_base_url=os.environ.get("OPENROUTER_BASE_URL") or DEFAULT_OPENROUTER_BASE_URL,
        openrouter_model=os.environ.get("OPENROUTER_MODEL") or DEFAULT_OPENROUTER_MODEL,
    )
