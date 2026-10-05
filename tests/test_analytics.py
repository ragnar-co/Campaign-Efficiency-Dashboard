"""Unit tests for app.services.analytics — TC-04, TC-05, TC-07."""

from __future__ import annotations

from app.services.analytics import ChannelMetrics, Totals, compute_metrics, lowest_eligible_cpql_channel


def test_known_fixture_totals_and_ratios():
    # Spend=1500 THB, Leads=100, Qualified=10 -> CPL=15, CPQL=150, rate=0.10
    metrics = compute_metrics(Totals(spend_satang=150_000, lead_count=100, qualified_lead_count=10))
    assert metrics.spend_thb == 1500.0
    assert metrics.cpl == 15.0
    assert metrics.cpql == 150.0
    assert metrics.qualification_rate == 0.1


def test_lead_denominator_zero_yields_null_cpl_and_qualification_rate():
    metrics = compute_metrics(Totals(spend_satang=50_000, lead_count=0, qualified_lead_count=0))
    assert metrics.cpl is None
    assert metrics.qualification_rate is None
    assert metrics.cpql is None  # qualified leads is also 0 here


def test_qualified_denominator_zero_yields_null_cpql_only():
    # Leads=20 (nonzero) but Qualified=0 -> CPQL null, CPL/rate still defined
    metrics = compute_metrics(Totals(spend_satang=30_000, lead_count=20, qualified_lead_count=0))
    assert metrics.cpl == 15.0
    assert metrics.qualification_rate == 0.0
    assert metrics.cpql is None


def test_channel_aggregation_sums_numerator_denominator_before_dividing():
    # Two campaigns in the same channel: averaging per-campaign CPL would give
    # a wrong answer; aggregate-then-divide is the only correct approach.
    # Campaign A: spend=100, leads=10 -> per-campaign CPL=10
    # Campaign B: spend=1000, leads=1000 -> per-campaign CPL=1
    # Average of per-campaign CPL would be 5.5, which must NOT be the result.
    totals = Totals(spend_satang=(100 + 1000) * 100, lead_count=10 + 1000, qualified_lead_count=0)
    metrics = compute_metrics(totals)
    assert metrics.cpl == round((100 + 1000) / (10 + 1000), 2)
    assert metrics.cpl != 5.5


def test_lowest_eligible_cpql_excludes_zero_qualified_leads_channel():
    channels = [
        ChannelMetrics("Display Ads", compute_metrics(Totals(10_000_00, 100, 0))),  # cheap but ineligible
        ChannelMetrics("Email", compute_metrics(Totals(50_000_00, 500, 50))),
        ChannelMetrics("Google Search", compute_metrics(Totals(100_000_00, 1000, 200))),
    ]
    best = lowest_eligible_cpql_channel(channels)
    assert best is not None
    assert best.channel in {"Email", "Google Search"}
    assert best.metrics.qualified_lead_count > 0


def test_lowest_eligible_cpql_is_none_when_no_channel_has_qualified_leads():
    channels = [
        ChannelMetrics("Display Ads", compute_metrics(Totals(10_000_00, 100, 0))),
        ChannelMetrics("Email", compute_metrics(Totals(5_000_00, 50, 0))),
    ]
    assert lowest_eligible_cpql_channel(channels) is None
