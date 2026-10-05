"""API contract tests for every API_SPEC.md endpoint — TC-06, TC-08, AC-03, AC-04."""

from __future__ import annotations

from tests.conftest import VALID_CSV


def _import(client):
    response = client.post(
        "/api/datasets/import", files={"file": ("valid.csv", VALID_CSV, "text/csv")}
    )
    assert response.status_code == 201
    return response.json()["dataset_id"]


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] is True


def test_dashboard_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Campaign Efficiency Dashboard" in response.text


def test_summary_not_found_returns_404(client):
    response = client.get("/api/datasets/42/summary")
    assert response.status_code == 404
    assert response.json()["application_error_code"] == "DATASET_NOT_FOUND"


def test_channels_not_found_returns_404(client):
    response = client.get("/api/datasets/42/channels")
    assert response.status_code == 404


def test_campaigns_not_found_returns_404(client):
    response = client.get("/api/datasets/42/campaigns")
    assert response.status_code == 404


def test_channel_table_values_match_chart_payload_aggregation(client):
    dataset_id = _import(client)
    channels_resp = client.get(f"/api/datasets/{dataset_id}/channels").json()["channels"]
    summary_resp = client.get(f"/api/datasets/{dataset_id}/summary").json()

    # Same aggregation contract: dataset totals equal sum across channel rows.
    assert sum(c["spend_thb"] for c in channels_resp) == summary_resp["spend_thb"]
    assert sum(c["lead_count"] for c in channels_resp) == summary_resp["lead_count"]
    assert sum(c["qualified_lead_count"] for c in channels_resp) == summary_resp["qualified_lead_count"]

    # best_cpql_channel must be present among channels and match its reported cpql.
    best_channel = next(c for c in channels_resp if c["channel"] == summary_resp["best_cpql_channel"])
    assert best_channel["cpql"] == summary_resp["best_cpql_value"]


def test_channel_filter_returns_only_selected_channel(client):
    dataset_id = _import(client)
    response = client.get(f"/api/datasets/{dataset_id}/campaigns?channel=Email")
    body = response.json()
    assert body["channel_filter"] == "Email"
    assert all(c["channel"] == "Email" for c in body["campaigns"])
    assert len(body["campaigns"]) == 1


def test_no_channel_filter_returns_all_campaigns(client):
    dataset_id = _import(client)
    response = client.get(f"/api/datasets/{dataset_id}/campaigns")
    body = response.json()
    assert body["channel_filter"] is None
    assert len(body["campaigns"]) == 3


def test_lowest_cpql_excludes_zero_qualified_lead_channel(client):
    dataset_id = _import(client)
    # VALID_CSV: Display Ads has qualified_lead_count=0, must never be best_cpql_channel.
    summary = client.get(f"/api/datasets/{dataset_id}/summary").json()
    assert summary["best_cpql_channel"] != "Display Ads"
