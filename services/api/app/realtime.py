"""Server-sent events for new alerts.

Each API replica keeps a set of connected dashboards. New alerts reach them via
PostgreSQL LISTEN/NOTIFY so every replica is informed no matter which one stored
the hit; on SQLite (dev/tests) we publish in-process. The event carries only the
alert id - the dashboard refetches through the authenticated API.
"""
import asyncio
import json
import logging
from collections.abc import AsyncIterator

from sqlalchemy import text
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)
CHANNEL = "deception_alerts"


class Broker:
    def __init__(self) -> None:
        self._subs: set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subs.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self._subs.discard(q)

    def publish(self, payload: dict) -> None:
        for q in list(self._subs):
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:  # slow client: it will resync on its next poll
                pass

    @property
    def subscribers(self) -> int:
        return len(self._subs)


broker = Broker()


def announce_alert(db: Session, alert_id: int) -> None:
    """Called after an alert is committed."""
    if db.get_bind().dialect.name == "postgresql":
        db.execute(text("SELECT pg_notify(:c, :p)"), {"c": CHANNEL, "p": str(alert_id)})
        db.commit()
    else:
        broker.publish({"alert_id": alert_id})


async def event_stream(q: asyncio.Queue, heartbeat: float = 15.0) -> AsyncIterator[str]:
    yield "retry: 3000\n\n"
    try:
        while True:
            try:
                payload = await asyncio.wait_for(q.get(), timeout=heartbeat)
                yield f"event: alert\ndata: {json.dumps(payload)}\n\n"
            except asyncio.TimeoutError:
                yield ": ping\n\n"
    finally:
        broker.unsubscribe(q)


async def pg_listener(sqlalchemy_url: str) -> None:
    """Forward Postgres notifications to local subscribers; reconnect forever."""
    import psycopg

    dsn = sqlalchemy_url.replace("+psycopg", "", 1)
    delay = 1.0
    while True:
        try:
            async with await psycopg.AsyncConnection.connect(dsn, autocommit=True) as conn:
                await conn.execute(f"LISTEN {CHANNEL}")
                delay = 1.0
                async for note in conn.notifies():
                    try:
                        broker.publish({"alert_id": int(note.payload)})
                    except ValueError:
                        pass
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.warning("LISTEN connection lost (%s); retrying in %.0fs", exc, delay)
            await asyncio.sleep(delay)
            delay = min(delay * 2, 30)
