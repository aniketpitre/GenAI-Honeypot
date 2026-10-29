import asyncio

from app.realtime import Broker, event_stream, broker, announce_alert


async def test_event_stream_delivers_and_heartbeats():
    q = broker.subscribe()
    gen = event_stream(q, heartbeat=0.05)
    assert (await gen.__anext__()).startswith("retry:")
    assert (await gen.__anext__()) == ": ping\n\n"          # idle -> heartbeat
    broker.publish({"alert_id": 7})
    chunk = await gen.__anext__()
    assert chunk == 'event: alert\ndata: {"alert_id": 7}\n\n'
    await gen.aclose()
    assert broker.subscribers == 0                            # cleaned up on disconnect


async def test_slow_subscriber_does_not_block_others():
    b = Broker()
    slow, fast = b.subscribe(), b.subscribe()
    for i in range(150):                                      # overflows `slow` (maxsize 100)
        b.publish({"n": i})
        if not fast.empty():
            fast.get_nowait()
    assert slow.qsize() == 100


def test_hit_announces_on_sqlite(client):
    from .conftest import ADMIN, INTERNAL

    q = broker.subscribe()
    t = client.post("/api/v1/tokens", json={"name": "n"}, headers=ADMIN).json()
    client.post("/internal/v1/hits", headers=INTERNAL, json={"token_id": t["id"], "ip": "8.8.8.8"})
    assert q.get_nowait() == {"alert_id": 1}
    broker.unsubscribe(q)


def test_stream_requires_admin(client):
    assert client.get("/api/v1/stream").status_code == 401
