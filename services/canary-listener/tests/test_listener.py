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
