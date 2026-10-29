import pytest
from fastapi.testclient import TestClient

from app import main
from app.main import app


@pytest.fixture
def sent(monkeypatch):
    calls = []

    async def fake_forward(payload):
        calls.append(payload)

    monkeypatch.setattr(main, "forward", fake_forward)
    main._hits.clear()
    return calls


def test_trap_returns_403_and_forwards(sent):
    c = TestClient(app)
    r = c.get("/t/abc123", headers={"X-Forwarded-For": "203.0.113.9", "Cookie": "secret=1", "User-Agent": "curl/8"})
    assert r.status_code == 403
    assert sent[0]["token_id"] == "abc123" and sent[0]["ip"] == "203.0.113.9"
    assert "cookie" not in sent[0]["headers"] and sent[0]["user_agent"] == "curl/8"


def test_spoofed_xff_prefix_ignored(sent):
    # attacker prepends a fake entry; with 1 trusted proxy we take the rightmost.
    TestClient(app).get("/t/x", headers={"X-Forwarded-For": "6.6.6.6, 203.0.113.9"})
    assert sent[0]["ip"] == "203.0.113.9"


def test_pixel(sent):
    r = TestClient(app).get("/p/abc.png")
    assert r.headers["content-type"] == "image/png" and r.content.startswith(b"\x89PNG")
    assert len(sent) == 1


def test_rate_limit(sent, monkeypatch):
    monkeypatch.setattr(main.settings, "rate_limit_per_minute", 3)
    c = TestClient(app)
    for _ in range(10):
        assert c.get("/t/x", headers={"X-Forwarded-For": "9.9.9.9"}).status_code == 403
    assert len(sent) == 3


def test_spool_roundtrip_and_order(tmp_path):
    import asyncio

    from app.spool import Spool

    async def go():
        sp = Spool(str(tmp_path), max_entries=3)
        for i in range(3):
            assert await sp.add({"n": i})
        assert not await sp.add({"n": 99})  # full
        seen = []

        async def flaky(p):
            seen.append(p["n"])
            return p["n"] != 1  # n=1 fails -> n=1,2 stay queued, in order

        assert await sp.drain(flaky) == 2
        assert seen == [0, 1]
        assert await sp.drain(lambda p: _ok()) == 0

    async def _ok():
        return True

    asyncio.run(go())


def test_api_down_spools_then_retries(monkeypatch, tmp_path):
    import asyncio

    from app.spool import Spool

    async def go():
        main.spool = Spool(str(tmp_path))
        up = {"v": False}
        sent = []

        async def fake_post(payload):
            if not up["v"]:
                return False
            sent.append(payload)
            return True

        monkeypatch.setattr(main, "post_hit", fake_post)
        await main.forward({"hit_id": "h1"})
        assert main.spool.size() == 1 and not sent
        up["v"] = True
        assert await main.spool.drain(main.post_hit) == 0
        assert sent == [{"hit_id": "h1"}]

    asyncio.run(go())


def test_hit_has_unique_id_and_metrics(sent):
    c = TestClient(app)
    c.get("/t/a"); c.get("/t/a")
    assert sent[0]["hit_id"] != sent[1]["hit_id"]
    assert "canary_hits_total" in c.get("/metrics").text
