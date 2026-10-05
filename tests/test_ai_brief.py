"""AI bonus workflow tests — TC-11 (stub success), TC-12 (failure), FR-12..FR-14.

Per TESTING.md: "CP-06 may be exercised with AI client stub when real quota
is unavailable." No real COMPANY_AI_ENDPOINT credentials were available, so
these tests inject a stub AIClient via dependency override.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.deps import get_ai_client
from app.errors import ApplicationError, ApplicationErrorCode
from app.services.ai_client import AIClient, BriefContent
from tests.conftest import VALID_CSV


class StubSuccessAIClient(AIClient):
    def generate_brief(self, facts: dict) -> BriefContent:
        return BriefContent(
            facts=[f"Total spend is {facts['totals']['spend_thb']} THB"],
            items_to_verify=["Confirm qualification criteria with sales ops"],
            next_experiment_proposals=["Shift 10% budget toward the lowest-CPQL channel"],
        )


class StubFailingAIClient(AIClient):
    def generate_brief(self, facts: dict) -> BriefContent:
        raise ApplicationError(ApplicationErrorCode.AI_UPSTREAM_ERROR, "Simulated upstream failure")


def _import(client):
    response = client.post(
        "/api/datasets/import", files={"file": ("valid.csv", VALID_CSV, "text/csv")}
    )
    return response.json()["dataset_id"]


def test_ai_not_configured_returns_503_and_dashboard_still_works(client):
    dataset_id = _import(client)
    response = client.post(f"/api/datasets/{dataset_id}/briefs")
    assert response.status_code == 503
    assert response.json()["application_error_code"] == "AI_NOT_CONFIGURED"

    # Core dashboard must remain usable.
    summary_response = client.get(f"/api/datasets/{dataset_id}/summary")
    assert summary_response.status_code == 200


def test_ai_stub_success_generates_saves_and_reads_brief(app_factory):
    app = app_factory(ai_configured=True)
    app.dependency_overrides[get_ai_client] = lambda: StubSuccessAIClient()
    client = TestClient(app)

    dataset_id = _import(client)

    create_response = client.post(f"/api/datasets/{dataset_id}/briefs")
    assert create_response.status_code == 201
    body = create_response.json()
    assert body["facts"]
    assert body["items_to_verify"]
    assert body["next_experiment_proposals"]

    read_response = client.get(f"/api/datasets/{dataset_id}/briefs/latest")
    assert read_response.status_code == 200
    assert read_response.json()["id"] == body["id"]


def test_ai_upstream_error_returns_controlled_error_and_dashboard_remains_usable(app_factory):
    app = app_factory(ai_configured=True)
    app.dependency_overrides[get_ai_client] = lambda: StubFailingAIClient()
    client = TestClient(app)

    dataset_id = _import(client)

    response = client.post(f"/api/datasets/{dataset_id}/briefs")
    assert response.status_code == 503
    assert response.json()["application_error_code"] == "AI_UPSTREAM_ERROR"

    summary_response = client.get(f"/api/datasets/{dataset_id}/summary")
    assert summary_response.status_code == 200
