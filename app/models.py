"""SQLAlchemy ORM models.

Schema owner: DATA_MODEL.md. Table/column names, constraints, and indexes here
must match that document exactly. Do not add columns or enums without updating
DATA_MODEL.md first.
"""

from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_filename: Mapped[str] = mapped_column(Text, nullable=False)
    imported_at: Mapped[str] = mapped_column(Text, nullable=False)  # ISO-8601 UTC
    row_count: Mapped[int] = mapped_column(Integer, nullable=False)

    campaigns: Mapped[list["Campaign"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )
    briefs: Mapped[list["CampaignReviewBrief"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )

    __table_args__ = (CheckConstraint("row_count >= 0", name="ck_datasets_row_count"),)


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    campaign_id: Mapped[str] = mapped_column(Text, nullable=False)
    campaign_name: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[str] = mapped_column(Text, nullable=False)
    spend_satang: Mapped[int] = mapped_column(Integer, nullable=False)
    lead_count: Mapped[int] = mapped_column(Integer, nullable=False)
    qualified_lead_count: Mapped[int] = mapped_column(Integer, nullable=False)

    dataset: Mapped["Dataset"] = relationship(back_populates="campaigns")

    __table_args__ = (
        CheckConstraint("spend_satang >= 0", name="ck_campaigns_spend_nonneg"),
        CheckConstraint("lead_count >= 0", name="ck_campaigns_lead_nonneg"),
        CheckConstraint(
            "qualified_lead_count >= 0 AND qualified_lead_count <= lead_count",
            name="ck_campaigns_qualified_lead_bounds",
        ),
        UniqueConstraint("dataset_id", "campaign_id", name="uq_campaigns_dataset_campaign_id"),
        Index("ix_campaigns_dataset_channel", "dataset_id", "channel"),
    )


class CampaignReviewBrief(Base):
    __tablename__ = "campaign_review_briefs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    generated_at: Mapped[str] = mapped_column(Text, nullable=False)  # ISO-8601 UTC
    facts_json: Mapped[str] = mapped_column(Text, nullable=False)
    items_to_verify_json: Mapped[str] = mapped_column(Text, nullable=False)
    experiment_proposals_json: Mapped[str] = mapped_column(Text, nullable=False)
    model_reference: Mapped[str | None] = mapped_column(Text, nullable=True)

    dataset: Mapped["Dataset"] = relationship(back_populates="briefs")
