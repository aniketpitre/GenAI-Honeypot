"""Run Alembic migrations at start-up. On PostgreSQL a session-level advisory
lock serialises concurrent replicas so only one applies the migration."""
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.engine import Engine

_LOCK_ID = 727_001  # arbitrary app-wide constant


def run_migrations(engine: Engine) -> None:
    root = Path(__file__).resolve().parent.parent
    cfg = Config(str(root / "alembic.ini"))
    cfg.set_main_option("script_location", str(root / "migrations"))
    with engine.connect() as conn:
        locked = engine.dialect.name == "postgresql"
        if locked:
            conn.execute(text("SELECT pg_advisory_lock(:id)"), {"id": _LOCK_ID})
        try:
            cfg.attributes["connection"] = conn
            command.upgrade(cfg, "head")
            conn.commit()
        finally:
            if locked:
                conn.execute(text("SELECT pg_advisory_unlock(:id)"), {"id": _LOCK_ID})
                conn.commit()
