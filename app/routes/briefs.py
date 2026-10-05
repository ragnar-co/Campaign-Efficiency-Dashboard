from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import Settings
from app.deps import get_ai_client, get_session, get_settings
from app.schemas import BriefResponse
from app.services import brief_service
from app.services.ai_client import AIClient

router = APIRouter(prefix="/api/datasets", tags=["briefs"])


@router.post("/{dataset_id}/briefs", response_model=BriefResponse, status_code=201)
def create_brief(
    dataset_id: int,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
    ai_client: AIClient | None = Depends(get_ai_client),
) -> dict:
    brief = brief_service.generate_and_save_brief(
        session, settings, dataset_id, ai_client=ai_client
    )
    return brief_service.serialize_brief(brief)


@router.get("/{dataset_id}/briefs/latest", response_model=BriefResponse)
def latest_brief(dataset_id: int, session: Session = Depends(get_session)) -> dict:
    brief = brief_service.get_latest_brief(session, dataset_id)
    if brief is None:
        # Dataset exists but no brief has been generated yet. This is not one
        # of API_SPEC.md's application_error_code values (no code fits "brief
        # not yet generated"), so a plain 404 is returned rather than
        # misusing DATASET_NOT_FOUND or inventing a new enum value.
        raise HTTPException(status_code=404, detail="No brief has been generated for this dataset yet")
    return brief_service.serialize_brief(brief)
