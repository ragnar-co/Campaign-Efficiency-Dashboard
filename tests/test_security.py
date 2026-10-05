"""Security-oriented validation per TESTING.md Security Test Results:
filename/path traversal, SQL injection resistance, secret absence, malformed
CSV handling. HTML escaping is enforced client-side via textContent in
app.js (no campaign/channel data is ever server-rendered into HTML), so here
we confirm the API layer never writes the client filename to disk and never
leaks configured secrets.
"""

from __future__ import annotations

import os

from tests.conftest import VALID_CSV


def test_path_traversal_filename_is_never_used_as_filesystem_path(client, tmp_path):
    malicious_name = "../../../../etc/passwd.csv"
    response = client.post(
        "/api/datasets/import", files={"file": (malicious_name, VALID_CSV, "text/csv")}
    )
    assert response.status_code == 201
    # The dataset import must succeed purely from file content; no file should
    # ever be written to disk using the client-supplied name.
    assert not os.path.exists("/etc/passwd.csv")


def test_sql_injection_style_channel_filter_is_safely_parameterized(client):
    _import_valid(client)
    dataset_id = 1
    response = client.get(
        f"/api/datasets/{dataset_id}/campaigns",
        params={"channel": "Email' OR '1'='1"},
    )
    assert response.status_code == 200
    # No literal channel matches the injected string; ORM parameterization
    # means it is treated as a plain value, not SQL, so zero rows return.
    assert response.json()["campaigns"] == []


def test_malformed_non_csv_upload_is_rejected_without_500(client):
    garbage = bytes(range(256))
    response = client.post(
        "/api/datasets/import", files={"file": ("binary.csv", garbage, "application/octet-stream")}
    )
    assert response.status_code in (400, 422)
    assert response.status_code != 500


def test_ai_secret_never_appears_in_any_response(app_factory):
    from fastapi.testclient import TestClient

    from app.deps import get_ai_client
    from app.errors import ApplicationError, ApplicationErrorCode
    from app.services.ai_client import AIClient, BriefContent

    class _StubClient(AIClient):
        def generate_brief(self, facts: dict) -> BriefContent:
            raise ApplicationError(ApplicationErrorCode.AI_UPSTREAM_ERROR, "simulated failure")

    app = app_factory(ai_configured=True)
    app.dependency_overrides[get_ai_client] = lambda: _StubClient()
    client = TestClient(app)
    secret = app.state.settings.openrouter_api_key
    assert secret == "test-key"

    dataset_id = _import_valid(client)
    responses = [
        client.get("/health"),
        client.get("/"),
        client.get(f"/api/datasets/{dataset_id}/summary"),
        client.post(f"/api/datasets/{dataset_id}/briefs"),  # stub raises AI_UPSTREAM_ERROR, no network call
    ]
    for response in responses:
        assert secret not in response.text


def _import_valid(client) -> int:
    response = client.post(
        "/api/datasets/import", files={"file": ("valid.csv", VALID_CSV, "text/csv")}
    )
    return response.json()["dataset_id"]
