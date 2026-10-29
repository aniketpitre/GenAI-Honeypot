from collections.abc import Iterator
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import get_settings


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    type: Mapped[str] = mapped_column(String(16))  # url | pixel | document
    status: Mapped[str] = mapped_column(String(16), default="active")  # active | disabled
    decoy_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Idempotency key so breadcrumb generation can be re-run safely.
    external_key: Mapped[str | None] = mapped_column(String(200), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    alerts: Mapped[list["Alert"]] = relationship(back_populates="token", cascade="all, delete-orphan")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Listener-generated id; makes redelivered hits idempotent.
    hit_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    token_id: Mapped[str] = mapped_column(ForeignKey("tokens.id", ondelete="CASCADE"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    ip: Mapped[str] = mapped_column(String(64))
    city: Mapped[str] = mapped_column(String(120), default="")
    country: Mapped[str] = mapped_column(String(8), default="")
    lat: Mapped[float] = mapped_column(default=0.0)
    lon: Mapped[float] = mapped_column(default=0.0)
    user_agent: Mapped[str] = mapped_column(Text, default="")
    request_path: Mapped[str] = mapped_column(Text, default="")
    request_headers: Mapped[dict] = mapped_column(JSON, default=dict)
    notes: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="New")

    token: Mapped[Token] = relationship(back_populates="alerts")


_engine = None
_SessionLocal: sessionmaker[Session] | None = None


def init_engine(url: str | None = None, create_all: bool = False) -> None:
    """(Re)initialise the engine. Tests pass create_all=True with an in-memory SQLite URL;
    real deployments use Alembic (app.migrate)."""
    global _engine, _SessionLocal
    url = url or get_settings().database_url
    kwargs: dict = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        if ":memory:" in url or url == "sqlite://":
            kwargs["poolclass"] = StaticPool
    _engine = create_engine(url, **kwargs)
    _SessionLocal = sessionmaker(_engine, expire_on_commit=False)
    if create_all:
        Base.metadata.create_all(_engine)


def get_engine():
    if _engine is None:
        init_engine()
    return _engine


def get_db() -> Iterator[Session]:
    if _SessionLocal is None:
        init_engine()
    assert _SessionLocal is not None
    with _SessionLocal() as session:
        yield session


def ping() -> None:
    for db in get_db():
        db.execute(select(func.count()).select_from(Token))
