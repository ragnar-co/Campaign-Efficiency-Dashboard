from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.db import database_is_reachable

router = APIRouter()


@router.get("/health")
def health(request: Request) -> JSONResponse:
    db_ok = database_is_reachable(request.app.state.engine)
    payload = {"status": "ok" if db_ok else "degraded", "database": db_ok}
    return JSONResponse(status_code=200 if db_ok else 503, content=payload)
