import sqlalchemy as sa

from app.db import Base, init_engine, get_engine
from app.migrate import run_migrations


def test_migrations_match_models(tmp_path):
    init_engine(f"sqlite:///{tmp_path}/m.db")
    engine = get_engine()
    run_migrations(engine)
    run_migrations(engine)  # idempotent
    insp = sa.inspect(engine)
    assert set(Base.metadata.tables) <= set(insp.get_table_names())
    for name, table in Base.metadata.tables.items():
        assert {c.name for c in table.columns} == {c["name"] for c in insp.get_columns(name)}, name


def test_short_secret_refuses_to_start(monkeypatch):
    import pytest
    from fastapi.testclient import TestClient

    from app.config import get_settings
    from app.main import app

    monkeypatch.setenv("ADMIN_TOKEN", "short")
    get_settings.cache_clear()
    with pytest.raises(RuntimeError, match="at least 24"):
        with TestClient(app):
            pass
    monkeypatch.undo()
    get_settings.cache_clear()
