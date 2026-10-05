"""Read-side orchestration for dataset summary/channel/campaign endpoints."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.errors import ApplicationError, ApplicationErrorCode
from app.models import Campaign
from app.repositories import dataset_repo
from app.services.analytics import (
    ChannelMetrics,
    Totals,
    compute_metrics,
    lowest_eligible_cpql_channel,
)


def _require_dataset(session: Session, dataset_id: int):
    dataset = dataset_repo.get_dataset(session, dataset_id)
    if dataset is None:
        raise ApplicationError(
            ApplicationErrorCode.DATASET_NOT_FOUND, f"Dataset {dataset_id} not found"
        )
    return dataset


def get_summary(session: Session, dataset_id: int) -> dict:
    _require_dataset(session, dataset_id)

    spend_satang, leads, qualified_leads = dataset_repo.get_dataset_totals(session, dataset_id)
    metrics = compute_metrics(Totals(spend_satang, leads, qualified_leads))

    channel_metrics = _get_channel_metrics(session, dataset_id)
    best = lowest_eligible_cpql_channel(channel_metrics)

    return {
        "dataset_id": dataset_id,
        "spend_thb": metrics.spend_thb,
        "lead_count": metrics.lead_count,
        "qualified_lead_count": metrics.qualified_lead_count,
        "cpl": metrics.cpl,
        "cpql": metrics.cpql,
        "qualification_rate": metrics.qualification_rate,
        "best_cpql_channel": best.channel if best else None,
        "best_cpql_value": best.metrics.cpql if best else None,
    }


def _get_channel_metrics(session: Session, dataset_id: int) -> list[ChannelMetrics]:
    rows = dataset_repo.get_channel_totals(session, dataset_id)
    return [
        ChannelMetrics(channel=name, metrics=compute_metrics(Totals(s, l, q)))
        for name, s, l, q in rows
    ]


def get_channels(session: Session, dataset_id: int) -> dict:
    _require_dataset(session, dataset_id)
    channel_metrics = _get_channel_metrics(session, dataset_id)
    return {
        "dataset_id": dataset_id,
        "channels": [
            {
                "channel": cm.channel,
                "spend_thb": cm.metrics.spend_thb,
                "lead_count": cm.metrics.lead_count,
                "qualified_lead_count": cm.metrics.qualified_lead_count,
                "cpl": cm.metrics.cpl,
                "cpql": cm.metrics.cpql,
                "qualification_rate": cm.metrics.qualification_rate,
            }
            for cm in channel_metrics
        ],
    }


def _serialize_campaign(campaign: Campaign) -> dict:
    metrics = compute_metrics(
        Totals(campaign.spend_satang, campaign.lead_count, campaign.qualified_lead_count)
    )
    return {
        "campaign_id": campaign.campaign_id,
        "campaign_name": campaign.campaign_name,
        "channel": campaign.channel,
        "spend_thb": metrics.spend_thb,
        "lead_count": metrics.lead_count,
        "qualified_lead_count": metrics.qualified_lead_count,
        "cpl": metrics.cpl,
        "cpql": metrics.cpql,
        "qualification_rate": metrics.qualification_rate,
    }


def get_campaigns(session: Session, dataset_id: int, channel: str | None) -> dict:
    _require_dataset(session, dataset_id)
    campaigns = dataset_repo.get_campaigns(session, dataset_id, channel)
    return {
        "dataset_id": dataset_id,
        "channel_filter": channel,
        "campaigns": [_serialize_campaign(c) for c in campaigns],
    }
