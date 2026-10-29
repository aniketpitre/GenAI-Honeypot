import httpx
import pytest

from app import security
from app.config import get_settings
from app.events import publish

from .conftest import ADMIN


@pytest.fixture(autouse=True)
def _reset():
    security._failures.clear()
    yield
    security._failures.clear()


def test_login_lockout_after_repeated_failures(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "auth_fail_limit", 3)
    bad = {"Authorization": "Bearer wrong"}
    assert [client.get("/api/v1/tokens", headers=bad).status_code for _ in range(3)] == [401, 401, 401]
    r = client.get("/api/v1/tokens", headers=bad)
    assert r.status_code == 429 and "Retry-After" in r.headers
    # locked out even with the right token until the window passes
    assert client.get("/api/v1/tokens", headers=ADMIN).status_code == 429


def test_lockout_is_per_client_ip_with_trusted_proxy(client, monkeypatch):
    s = get_settings()
    monkeypatch.setattr(s, "auth_fail_limit", 2)
    monkeypatch.setattr(s, "trusted_proxy_count", 1)
    bad = {"Authorization": "Bearer wrong"}
    for _ in range(2):
        client.get("/api/v1/tokens", headers={**bad, "X-Forwarded-For": "6.6.6.6"})
    assert client.get("/api/v1/tokens", headers={**bad, "X-Forwarded-For": "6.6.6.6"}).status_code == 429
    # a different real client is unaffected (no admin lock-out DoS from one attacker)
    assert client.get("/api/v1/tokens", headers={**ADMIN, "X-Forwarded-For": "10.1.1.1"}).status_code == 200


def test_success_does_not_count(client):
    for _ in range(30):
        assert client.get("/api/v1/tokens", headers=ADMIN).status_code == 200


@pytest.mark.asyncio
async def test_elasticsearch_credentials_sent(monkeypatch):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("authorization")
        return httpx.Response(201, json={})

    s = get_settings()
    monkeypatch.setattr(s, "elasticsearch_url", "http://es:9200")
    monkeypatch.setattr(s, "elasticsearch_user", "writer")
    monkeypatch.setattr(s, "elasticsearch_password", "pw")
    real = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: real(transport=httpx.MockTransport(handler), **kw))
    await publish({"@timestamp": "x", "deception": {"token": {"name": "n"}}, "source": {"ip": "1.1.1.1", "geo": {}}})
    assert seen["auth"].startswith("Basic ")
