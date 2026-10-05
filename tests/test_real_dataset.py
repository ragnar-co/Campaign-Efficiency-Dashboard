"""Integration test against the real provided dataset (20,966 rows) in
`Raw Data/`. TESTING.md names this exact file as the performance benchmark
dataset. This proves the import/analytics pipeline holds up at full scale,
not just on small synthetic fixtures.
"""

from __future__ import annotations

import pathlib

import pytest

REAL_CSV_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "Raw Data"
    / "ant_campaign_efficiency_mock_2_55MB.csv"
)

pytestmark = pytest.mark.skipif(
    not REAL_CSV_PATH.exists(), reason="Raw Data reference CSV not present in this checkout"
)


def test_real_dataset_imports_and_matches_expected_channel_aggregates(client):
    with open(REAL_CSV_PATH, "rb") as f:
        raw_bytes = f.read()

    response = client.post(
        "/api/datasets/import",
        files={"file": ("ant_campaign_efficiency_mock_2_55MB.csv", raw_bytes, "text/csv")},
    )
    assert response.status_code == 201
    body = response.json()
    dataset_id = body["dataset_id"]
    assert body["row_count"] == 20966

    channels_resp = client.get(f"/api/datasets/{dataset_id}/channels").json()["channels"]
    by_channel = {c["channel"]: c for c in channels_resp}

    expected = {
        "Display Ads": {"spend_thb": 10863744.00, "lead_count": 135462, "qualified_lead_count": 0, "cpl": 80.20, "cpql": None},
        "Partner Referral": {"spend_thb": 15274410.19, "lead_count": 49277, "qualified_lead_count": 28097, "cpl": 309.97, "cpql": 543.63},
        "Webinar": {"spend_thb": 52919018.45, "lead_count": 161786, "qualified_lead_count": 75287, "cpl": 327.09, "cpql": 702.90},
        "Meta Ads": {"spend_thb": 37647369.04, "lead_count": 683948, "qualified_lead_count": 29876, "cpl": 55.04, "cpql": 1260.12},
        "Google Search": {"spend_thb": 92809231.77, "lead_count": 458553, "qualified_lead_count": 147601, "cpl": 202.40, "cpql": 628.78},
        "Email": {"spend_thb": 9997869.20, "lead_count": 121032, "qualified_lead_count": 32684, "cpl": 82.61, "cpql": 305.89},
        "LinkedIn Ads": {"spend_thb": 88567087.43, "lead_count": 595971, "qualified_lead_count": 81118, "cpl": 148.61, "cpql": 1091.83},
    }

    assert set(by_channel.keys()) == set(expected.keys())
    for channel, exp in expected.items():
        actual = by_channel[channel]
        assert actual["spend_thb"] == pytest.approx(exp["spend_thb"], abs=0.02)
        assert actual["lead_count"] == exp["lead_count"]
        assert actual["qualified_lead_count"] == exp["qualified_lead_count"]
        assert actual["cpl"] == pytest.approx(exp["cpl"], abs=0.02)
        if exp["cpql"] is None:
            assert actual["cpql"] is None
        else:
            assert actual["cpql"] == pytest.approx(exp["cpql"], abs=0.02)

    summary = client.get(f"/api/datasets/{dataset_id}/summary").json()
    # Email has the lowest CPQL (305.89) among channels with qualified leads > 0;
    # Display Ads has zero qualified leads and must never be picked as best.
    assert summary["best_cpql_channel"] == "Email"
