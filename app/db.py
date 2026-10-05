"""SQLite engine/session setup.

DATA_MODEL.md is the schema owner; this module only wires SQLAlchemy to the
configured DATABASE_URL and enables foreign key enforcement, which SQLite
disables by default.
"""

from __future__ import annotations

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_db_engine(database_url: str) -> Engine:
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    engine = create_engine(database_url, connect_args=connect_args)
    if database_url.startswith("sqlite"):
        event.listen(engine, "connect", _enable_sqlite_foreign_keys)
    return engine


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_schema(engine: Engine) -> None:
    # Deterministic initial schema bootstrap per DATA_MODEL.md Migration Strategy:
    # "Initial MVP may bootstrap an empty database from migration 001_initial".
    from app import models  # noqa: F401  (ensures models are registered on Base)

    Base.metadata.create_all(bind=engine)


def database_is_reachable(engine: Engine) -> bool:
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        return True
    except Exception:
        return False
