"""Pydantic request/response models per API_SPEC.md."""

from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    database: bool


class ImportSuccessResponse(BaseModel):
    dataset_id: int
    row_count: int


class MetricsBlock(BaseModel):
    spend_thb: float
    lead_count: int
    qualified_lead_count: int
    cpl: float | None
    cpql: float | None
    qualification_rate: float | None


class DatasetSummaryResponse(MetricsBlock):
    dataset_id: int
    best_cpql_channel: str | None
    best_cpql_value: float | None


class ChannelMetric(MetricsBlock):
    channel: str


class ChannelsResponse(BaseModel):
    dataset_id: int
    channels: list[ChannelMetric]


class CampaignDetail(BaseModel):
    campaign_id: str
    campaign_name: str
    channel: str
    spend_thb: float
    lead_count: int
    qualified_lead_count: int
    cpl: float | None
    cpql: float | None
    qualification_rate: float | None


class CampaignsResponse(BaseModel):
    dataset_id: int
    channel_filter: str | None
    campaigns: list[CampaignDetail]


class BriefResponse(BaseModel):
    id: int
    dataset_id: int
    generated_at: str
    facts: list[str]
    items_to_verify: list[str]
    next_experiment_proposals: list[str]
    model_reference: str | None
