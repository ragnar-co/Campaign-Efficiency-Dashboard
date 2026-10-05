from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def make_settings(db_path, ai_configured: bool = False) -> Settings:
    return Settings(
        app_env="development",
        database_url=f"sqlite:///{db_path}",
        company_ai_endpoint="https://ai.example.test/v1/brief" if ai_configured else None,
        company_ai_api_key="test-key" if ai_configured else None,
        company_ai_model="test-model" if ai_configured else None,
    )


@pytest.fixture
def app_factory(tmp_path):
    """Returns a callable building a fresh app bound to an isolated SQLite file."""

    def _build(ai_configured: bool = False):
        db_path = tmp_path / "test.db"
        settings = make_settings(db_path, ai_configured=ai_configured)
        return create_app(settings)

    return _build


@pytest.fixture
def app(app_factory):
    return app_factory()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def session_factory(app):
    return app.state.session_factory


VALID_CSV = (
    b"campaign_id,campaign_name,channel,spend_thb,lead_count,qualified_lead_count\n"
    b"C1,Campaign One,Google Search,1000.00,100,10\n"
    b"C2,Campaign Two,Email,500.00,50,5\n"
    b"C3,Campaign Three,Display Ads,300.00,20,0\n"
)

MISSING_COLUMN_CSV = (
    b"campaign_id,campaign_name,spend_thb,lead_count,qualified_lead_count\n"
    b"C1,Campaign One,1000.00,100,10\n"
)

INVALID_ROWS_CSV = (
    b"campaign_id,campaign_name,channel,spend_thb,lead_count,qualified_lead_count\n"
    b"C1,Campaign One,Google Search,-1000.00,100,10\n"
    b"C2,Campaign Two,Email,500.00,5,10\n"
    b"C1,Campaign One Dup,Google Search,100.00,10,1\n"
)
