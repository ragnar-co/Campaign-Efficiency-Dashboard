"""FastAPI dependency providers.

Kept as thin, overridable seams so tests can inject a temp-database session
factory or an AI client stub (TESTING.md: "CP-06 may be exercised with AI
client stub when real quota is unavailable") without touching route/service
code.
"""

from __future__ import annotations

from collections.abc import Generator

from fastapi import Request
from sqlalchemy.orm import Session

from app.config import Settings
from app.services.ai_client import AIClient


def get_session(request: Request) -> Generator[Session, None, None]:
    session_factory = request.app.state.session_factory
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_ai_client() -> AIClient | None:
    """Default is None: production code falls back to building a real
    CompanyAIClient from Settings. Tests override this dependency to inject
    a stub AIClient instead."""
    return None
