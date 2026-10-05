"""Deterministic analytics calculations.

Single owner of metric formulas per CLAUDE.md/PLAN.md Phase 4 and PRD.md
FR-04..FR-08, FR-11. Nothing outside this module computes CPL/CPQL/Qualification
Rate. Channel aggregation always sums numerator/denominator first, then
divides; it never averages per-Campaign ratios.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

MONEY_QUANT = Decimal("0.01")
RATE_QUANT = Decimal("0.0001")


@dataclass(frozen=True)
class Totals:
    spend_satang: int
    lead_count: int
    qualified_lead_count: int


@dataclass(frozen=True)
class Metrics:
    spend_thb: float
    lead_count: int
    qualified_lead_count: int
    cpl: float | None
    cpql: float | None
    qualification_rate: float | None


def satang_to_thb(spend_satang: int) -> Decimal:
    return (Decimal(spend_satang) / Decimal(100)).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def _ratio(numerator: Decimal, denominator: int, quant: Decimal) -> Decimal | None:
    if denominator == 0:
        return None
    return (numerator / Decimal(denominator)).quantize(quant, rounding=ROUND_HALF_UP)


def compute_metrics(totals: Totals) -> Metrics:
    spend_thb = satang_to_thb(totals.spend_satang)
    cpl = _ratio(spend_thb, totals.lead_count, MONEY_QUANT)
    cpql = _ratio(spend_thb, totals.qualified_lead_count, MONEY_QUANT)
    qualification_rate = _ratio(
        Decimal(totals.qualified_lead_count), totals.lead_count, RATE_QUANT
    )
    return Metrics(
        spend_thb=float(spend_thb),
        lead_count=totals.lead_count,
        qualified_lead_count=totals.qualified_lead_count,
        cpl=float(cpl) if cpl is not None else None,
        cpql=float(cpql) if cpql is not None else None,
        qualification_rate=float(qualification_rate) if qualification_rate is not None else None,
    )


def compute_per_campaign_metrics(
    spend_satang: int, lead_count: int, qualified_lead_count: int
) -> Metrics:
    return compute_metrics(Totals(spend_satang, lead_count, qualified_lead_count))


@dataclass(frozen=True)
class ChannelMetrics:
    channel: str
    metrics: Metrics


def lowest_eligible_cpql_channel(
    channel_metrics: list[ChannelMetrics],
) -> ChannelMetrics | None:
    """FR-11: eligible channels have qualified_lead_count > 0. If none are
    eligible, the result is None (serialized as null/N/A). Ties are broken by
    the caller's input order, which must be deterministic (e.g. channel name
    ascending) to keep the result stable."""
    eligible = [cm for cm in channel_metrics if cm.metrics.qualified_lead_count > 0]
    if not eligible:
        return None
    return min(eligible, key=lambda cm: cm.metrics.cpql)
