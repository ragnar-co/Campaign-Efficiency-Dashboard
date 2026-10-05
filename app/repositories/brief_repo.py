"""Persistence access for AI-generated Campaign Review Briefs."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CampaignReviewBrief
from app.repositories.dataset_repo import utc_now_iso


def create_brief(
    session: Session,
    dataset_id: int,
    facts_json: str,
    items_to_verify_json: str,
    experiment_proposals_json: str,
    model_reference: str | None,
) -> CampaignReviewBrief:
    brief = CampaignReviewBrief(
        dataset_id=dataset_id,
        generated_at=utc_now_iso(),
        facts_json=facts_json,
        items_to_verify_json=items_to_verify_json,
        experiment_proposals_json=experiment_proposals_json,
        model_reference=model_reference,
    )
    session.add(brief)
    session.commit()
    session.refresh(brief)
    return brief


def get_latest_brief(session: Session, dataset_id: int) -> CampaignReviewBrief | None:
    stmt = (
        select(CampaignReviewBrief)
        .where(CampaignReviewBrief.dataset_id == dataset_id)
        .order_by(CampaignReviewBrief.id.desc())
        .limit(1)
    )
    return session.execute(stmt).scalars().first()
