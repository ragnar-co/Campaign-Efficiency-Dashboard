"""Persistence access for datasets and campaigns.

Keeps SQLite/SQLAlchemy specifics out of routes and templates per
AGENTS.md/CLAUDE.md "repository/service separation" convention.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Campaign, Dataset


def utc_now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_dataset_with_campaigns(
    session: Session,
    source_filename: str,
    rows: list[dict],
) -> Dataset:
    """Insert one dataset and all of its campaign rows in a single transaction.

    Caller must have already validated every row; this function performs no
    validation and assumes atomic all-or-nothing persistence per ADR-005.
    """
    dataset = Dataset(
        source_filename=source_filename,
        imported_at=utc_now_iso(),
        row_count=len(rows),
    )
    session.add(dataset)
    session.flush()  # assign dataset.id without committing

    campaigns = [
        Campaign(
            dataset_id=dataset.id,
            campaign_id=row["campaign_id"],
            campaign_name=row["campaign_name"],
            channel=row["channel"],
            spend_satang=row["spend_satang"],
            lead_count=row["lead_count"],
            qualified_lead_count=row["qualified_lead_count"],
        )
        for row in rows
    ]
    session.add_all(campaigns)
    session.commit()
    session.refresh(dataset)
    return dataset


def get_dataset(session: Session, dataset_id: int) -> Dataset | None:
    return session.get(Dataset, dataset_id)


def get_dataset_totals(session: Session, dataset_id: int) -> tuple[int, int, int]:
    row = session.execute(
        select(
            func.coalesce(func.sum(Campaign.spend_satang), 0),
            func.coalesce(func.sum(Campaign.lead_count), 0),
            func.coalesce(func.sum(Campaign.qualified_lead_count), 0),
        ).where(Campaign.dataset_id == dataset_id)
    ).one()
    return int(row[0]), int(row[1]), int(row[2])


def get_channel_totals(session: Session, dataset_id: int) -> list[tuple[str, int, int, int]]:
    rows = session.execute(
        select(
            Campaign.channel,
            func.sum(Campaign.spend_satang),
            func.sum(Campaign.lead_count),
            func.sum(Campaign.qualified_lead_count),
        )
        .where(Campaign.dataset_id == dataset_id)
        .group_by(Campaign.channel)
        .order_by(Campaign.channel.asc())
    ).all()
    return [(r[0], int(r[1]), int(r[2]), int(r[3])) for r in rows]


def get_campaigns(
    session: Session, dataset_id: int, channel: str | None = None
) -> list[Campaign]:
    stmt = select(Campaign).where(Campaign.dataset_id == dataset_id)
    if channel is not None:
        stmt = stmt.where(Campaign.channel == channel)
    stmt = stmt.order_by(Campaign.campaign_id.asc())
    return list(session.execute(stmt).scalars().all())
