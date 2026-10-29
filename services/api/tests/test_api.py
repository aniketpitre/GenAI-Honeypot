import io
import zipfile

from .conftest import ADMIN, INTERNAL


def make_token(client, **kw):
    body = {"name": "Q4 Financials", "type": "url", **kw}
    r = client.post("/api/v1/tokens", json=body, headers=ADMIN)
    assert r.status_code in (200, 201), r.text
    return r.json()


def test_auth_required(client):
    assert client.get("/api/v1/tokens").status_code == 401
    assert client.get("/api/v1/tokens", headers={"Authorization": "Bearer nope"}).status_code == 401
    assert client.post("/internal/v1/hits", json={"token_id": "x", "ip": "1.1.1.1"}).status_code == 401


def test_token_urls_by_type(client):
    t = make_token(client)
    assert t["value"] == f"https://canary.test/t/{t['id']}"
    p = make_token(client, name="px", type="pixel")
    assert p["value"] == f"https://canary.test/p/{p['id']}.png"


def test_external_key_is_idempotent(client):
    a = make_token(client, external_key="crumb-1")
    r = client.post("/api/v1/tokens", json={"name": "x", "external_key": "crumb-1"}, headers=ADMIN)
    assert r.status_code == 200 and r.json()["id"] == a["id"]


def test_hit_creates_alert_and_counts(client):
    t = make_token(client)
    r = client.post("/internal/v1/hits", headers=INTERNAL, json={
        "token_id": t["id"], "ip": "198.51.100.14", "user_agent": "curl/8", "path": f"/t/{t['id']}",
        "headers": {"accept": "*/*"}})
    assert r.status_code == 202 and r.json() == {"recorded": True}
    alerts = client.get("/api/v1/alerts", headers=ADMIN).json()
    assert len(alerts) == 1 and alerts[0]["ip"] == "198.51.100.14" and alerts[0]["token_name"] == "Q4 Financials"
    assert client.get("/api/v1/tokens", headers=ADMIN).json()[0]["alert_count"] == 1


def test_disabled_and_unknown_tokens_dropped(client):
    t = make_token(client)
    client.patch(f"/api/v1/tokens/{t['id']}", json={"status": "disabled"}, headers=ADMIN)
    for tid in (t["id"], "does-not-exist"):
        r = client.post("/internal/v1/hits", headers=INTERNAL, json={"token_id": tid, "ip": "8.8.8.8"})
        assert r.json() == {"recorded": False}
    assert client.get("/api/v1/alerts", headers=ADMIN).json() == []


def test_alert_triage(client):
    t = make_token(client)
    client.post("/internal/v1/hits", headers=INTERNAL, json={"token_id": t["id"], "ip": "8.8.8.8"})
    aid = client.get("/api/v1/alerts", headers=ADMIN).json()[0]["id"]
    r = client.patch(f"/api/v1/alerts/{aid}", headers=ADMIN, json={"status": "Resolved", "notes": "scanner"})
    assert r.json()["status"] == "Resolved" and r.json()["notes"] == "scanner"
    assert client.patch(f"/api/v1/alerts/{aid}", headers=ADMIN, json={"status": "bogus"}).status_code == 422


def test_document_download_embeds_pixel_url(client):
    t = make_token(client, type="document", name="Project Chimera")
    r = client.get(f"/api/v1/tokens/{t['id']}/download", headers=ADMIN)
    assert r.status_code == 200
    z = zipfile.ZipFile(io.BytesIO(r.content))
    assert t["value"] in z.read("word/_rels/document.xml.rels").decode()
    assert client.get(f"/api/v1/tokens/{make_token(client)['id']}/download", headers=ADMIN).status_code == 400


def test_generate_urls_fallback(client):
    r = client.post("/api/v1/generate/urls", json={"prompt": "exposed S3 bucket"}, headers=ADMIN)
    assert r.status_code == 200 and len(r.json()["urls"]) >= 3


def test_health(client):
    assert client.get("/healthz").status_code == 200
    assert client.get("/readyz").status_code == 200


def test_duplicate_hit_id_is_idempotent(client):
    t = make_token(client)
    body = {"token_id": t["id"], "ip": "8.8.8.8", "hit_id": "same-hit"}
    assert client.post("/internal/v1/hits", headers=INTERNAL, json=body).json() == {"recorded": True}
    assert client.post("/internal/v1/hits", headers=INTERNAL, json=body).json() == {"recorded": True}
    assert len(client.get("/api/v1/alerts", headers=ADMIN).json()) == 1


def test_metrics_endpoint(client):
    t = make_token(client)
    client.post("/internal/v1/hits", headers=INTERNAL, json={"token_id": t["id"], "ip": "8.8.8.8"})
    text = client.get("/metrics").text
    assert 'deception_hits_total{result="recorded"}' in text


def test_aws_and_kubeconfig_lures(client):
    a = make_token(client, type="aws", name="AWS prod")
    assert a["value"] == f"https://canary.test/aws/{a['id']}"
    r = client.get(f"/api/v1/tokens/{a['id']}/download", headers=ADMIN)
    assert r.status_code == 200 and "aws_access_key_id = AKIA" in r.text
    assert f"endpoint_url = https://canary.test/aws/{a['id']}" in r.text
    k = make_token(client, type="kubeconfig", name="k8s prod")
    r = client.get(f"/api/v1/tokens/{k['id']}/download", headers=ADMIN)
    assert f"server: https://canary.test/k8s/{k['id']}" in r.text and "kind: Config" in r.text
    assert client.get(f"/api/v1/tokens/{make_token(client)['id']}/download", headers=ADMIN).status_code == 400


def test_stats_flags_ip_hitting_several_tokens(client):
    t1, t2 = make_token(client, name="a"), make_token(client, name="b")
    for t in (t1, t2):
        client.post("/internal/v1/hits", headers=INTERNAL, json={"token_id": t["id"], "ip": "203.0.113.5"})
    client.post("/internal/v1/hits", headers=INTERNAL, json={"token_id": t1["id"], "ip": "198.51.100.7"})
    s = client.get("/api/v1/stats", headers=ADMIN).json()
    assert s["total_alerts"] == 3 and s["alerts_24h"] == 3 and s["new_alerts"] == 3 and s["active_tokens"] == 2
    assert s["top_sources"][0] == {"ip": "203.0.113.5", "alerts": 2, "distinct_tokens": 2, "country": ""}
