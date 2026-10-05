"""FastAPI application entrypoint and app factory."""

from __future__ import annotations

import logging
import pathlib

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import Settings, load_settings
from app.db import create_db_engine, create_session_factory, init_schema
from app.errors import ApplicationError, ApplicationErrorCode
from app.routes import briefs, dashboard, datasets, health

BASE_DIR = pathlib.Path(__file__).resolve().parent

logger = logging.getLogger("campaign_efficiency_dashboard")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()

    app = FastAPI(title="Campaign Efficiency Dashboard")

    engine = create_db_engine(settings.database_url)
    init_schema(engine)
    session_factory = create_session_factory(engine)

    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

    @app.exception_handler(ApplicationError)
    async def application_error_handler(_request: Request, exc: ApplicationError) -> JSONResponse:
        # Structured logs per SECURITY.md Audit Logging Requirements; never log
        # AI secrets or raw CSV bodies.
        logger.info(
            "application_error", extra={"error_code": exc.code.value, "status": exc.http_status}
        )
        return JSONResponse(status_code=exc.http_status, content=exc.to_payload())

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_error")
        payload = ApplicationError(ApplicationErrorCode.INTERNAL_ERROR, "Internal server error").to_payload()
        return JSONResponse(status_code=500, content=payload)

    app.include_router(health.router)
    app.include_router(dashboard.router)
    app.include_router(datasets.router)
    app.include_router(briefs.router)

    return app


app = create_app()
