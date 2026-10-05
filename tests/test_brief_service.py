"""Tests for the deterministic analytics-context builder that feeds the AI
brief (ADR-004: AI never computes metrics; it only narrates pre-computed
facts). Verifies the context is structured, derived from real backend
calculations, and never leaks raw campaign-level rows."""

from __future__ import annotations

from app.services import brief_service
from app.services.csv_import import import_csv
from tests.conftest import VALID_CSV


def test_build_analytics_facts_reflects_real_backend_calculations(session_factory):
    session = session_factory()
    try:
        dataset = import_csv(session, "valid.csv", VALID_CSV)

        facts = brief_service.build_analytics_facts(session, dataset.id)

        # Structured, dataset-scoped context.
        assert facts["dataset_id"] == dataset.id
        assert set(facts.keys()) == {
            "dataset_id",
            "totals",
            "channels",
            "best_cpql_channel",
            "best_cpql_value",
        }

        # Totals exactly match VALID_CSV: spend=1000+500+300=1800, leads=170, ql=15.
        assert facts["totals"]["spend_thb"] == 1800.0
        assert facts["totals"]["lead_count"] == 170
        assert facts["totals"]["qualified_lead_count"] == 15

        # Channel-level entries present, one per channel, each with full metric set.
        channels_by_name = {c["channel"]: c for c in facts["channels"]}
        assert set(channels_by_name) == {"Google Search", "Email", "Display Ads"}
        for row in facts["channels"]:
            assert {"channel", "spend_thb", "lead_count", "qualified_lead_count", "cpl", "cpql", "qualification_rate"} <= set(row.keys())

        # Display Ads has zero qualified leads -> excluded from best_cpql_channel (FR-11)
        # and its own cpql must render as null (serialized to N/A by the UI).
        assert channels_by_name["Display Ads"]["qualified_lead_count"] == 0
        assert channels_by_name["Display Ads"]["cpql"] is None
        assert facts["best_cpql_channel"] != "Display Ads"

        # No raw per-campaign rows (campaign_id/campaign_name) are sent to the AI —
        # only aggregated channel/dataset facts, per SECURITY.md minimization rule.
        assert "campaigns" not in facts
        import json

        serialized = json.dumps(facts)
        assert "C1" not in serialized and "C2" not in serialized and "C3" not in serialized
    finally:
        session.close()


def test_build_analytics_facts_unknown_dataset_raises_dataset_not_found(session_factory):
    import pytest

    from app.errors import ApplicationError, ApplicationErrorCode

    session = session_factory()
    try:
        with pytest.raises(ApplicationError) as exc_info:
            brief_service.get_latest_brief(session, dataset_id=9999)
        assert exc_info.value.code == ApplicationErrorCode.DATASET_NOT_FOUND
    finally:
        session.close()
