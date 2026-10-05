from __future__ import annotations

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.deps import get_session
from app.schemas import (
    CampaignsResponse,
    ChannelsResponse,
    DatasetSummaryResponse,
    ImportSuccessResponse,
)
from app.services import csv_import, dataset_service

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.post("/import", response_model=ImportSuccessResponse, status_code=201)
async def import_dataset(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> ImportSuccessResponse:
    raw_bytes = await file.read()
    # Never use the client-supplied filename as a filesystem path (SECURITY.md
    # threat model); it is stored only as a display label.
    dataset = csv_import.import_csv(session, file.filename or "upload.csv", raw_bytes)
    return ImportSuccessResponse(dataset_id=dataset.id, row_count=dataset.row_count)


@router.get("/{dataset_id}/summary", response_model=DatasetSummaryResponse)
def dataset_summary(dataset_id: int, session: Session = Depends(get_session)) -> dict:
    return dataset_service.get_summary(session, dataset_id)


@router.get("/{dataset_id}/channels", response_model=ChannelsResponse)
def dataset_channels(dataset_id: int, session: Session = Depends(get_session)) -> dict:
    return dataset_service.get_channels(session, dataset_id)


@router.get("/{dataset_id}/campaigns", response_model=CampaignsResponse)
def dataset_campaigns(
    dataset_id: int,
    channel: str | None = Query(default=None),
    session: Session = Depends(get_session),
) -> dict:
    return dataset_service.get_campaigns(session, dataset_id, channel)
