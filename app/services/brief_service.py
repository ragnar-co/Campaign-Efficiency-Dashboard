"""Orchestrates Campaign Review Brief generation, persistence, and reading.

FR-12..FR-14: input to AI is structured deterministic analytics facts only
(no raw campaign rows, no secrets). Output is normalized and persisted before
being considered successful.
"""

from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.config import Settings
from app.errors import ApplicationError, ApplicationErrorCode
from app.models import CampaignReviewBrief
from app.repositories import brief_repo, dataset_repo
from app.services.ai_client import AIClient, BriefContent, build_ai_client
from app.services.analytics import ChannelMetrics, Totals, compute_metrics, lowest_eligible_cpql_channel


def _require_dataset(session: Session, dataset_id: int):
    dataset = dataset_repo.get_dataset(session, dataset_id)
    if dataset is None:
        raise ApplicationError(
            ApplicationErrorCode.DATASET_NOT_FOUND, f"Dataset {dataset_id} not found"
        )
    return dataset


def build_analytics_facts(session: Session, dataset_id: int) -> dict:
    spend_satang, leads, qualified_leads = dataset_repo.get_dataset_totals(session, dataset_id)
    dataset_metrics = compute_metrics(Totals(spend_satang, leads, qualified_leads))

    channel_rows = dataset_repo.get_channel_totals(session, dataset_id)
    channel_metrics = [
        ChannelMetrics(channel=name, metrics=compute_metrics(Totals(s, l, q)))
        for name, s, l, q in channel_rows
    ]
    best = lowest_eligible_cpql_channel(channel_metrics)

    return {
        "dataset_id": dataset_id,
        "totals": {
            "spend_thb": dataset_metrics.spend_thb,
            "lead_count": dataset_metrics.lead_count,
            "qualified_lead_count": dataset_metrics.qualified_lead_count,
            "cpl": dataset_metrics.cpl,
            "cpql": dataset_metrics.cpql,
            "qualification_rate": dataset_metrics.qualification_rate,
        },
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
        "best_cpql_channel": best.channel if best else None,
        "best_cpql_value": best.metrics.cpql if best else None,
    }


def generate_and_save_brief(
    session: Session,
    settings: Settings,
    dataset_id: int,
    ai_client: AIClient | None = None,
) -> CampaignReviewBrief:
    _require_dataset(session, dataset_id)
    facts = build_analytics_facts(session, dataset_id)

    client = ai_client if ai_client is not None else build_ai_client(settings)
    content: BriefContent = client.generate_brief(facts)

    return brief_repo.create_brief(
        session,
        dataset_id=dataset_id,
        facts_json=json.dumps(content.facts),
        items_to_verify_json=json.dumps(content.items_to_verify),
        experiment_proposals_json=json.dumps(content.next_experiment_proposals),
        model_reference=settings.openrouter_model,
    )


def get_latest_brief(session: Session, dataset_id: int) -> CampaignReviewBrief | None:
    _require_dataset(session, dataset_id)
    return brief_repo.get_latest_brief(session, dataset_id)


def serialize_brief(brief: CampaignReviewBrief) -> dict:
    return {
        "id": brief.id,
        "dataset_id": brief.dataset_id,
        "generated_at": brief.generated_at,
        "facts": json.loads(brief.facts_json),
        "items_to_verify": json.loads(brief.items_to_verify_json),
        "next_experiment_proposals": json.loads(brief.experiment_proposals_json),
        "model_reference": brief.model_reference,
    }
