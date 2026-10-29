"""Smoke test against a RUNNING compose stack (core + honeypot + elk profiles).

    python tests/e2e/compose_smoke.py --env-file .env [--compose-args "-f docker-compose.yml ..."]

Checks the whole chain on real containers: breadcrumbs planted in the honeypot, trap hit ->
alert (Postgres) -> SSE push -> Elasticsearch (authenticated writer), SSH attack -> Filebeat ->
Logstash -> Elasticsearch, and the Kibana dashboard objects.
"""
import argparse
import json
import shlex
import subprocess
import sys
import threading
import time

import httpx

p = argparse.ArgumentParser()
p.add_argument("--env-file", required=True)
p.add_argument("--compose-args", default="-f docker-compose.yml")
p.add_argument("--ssh-port", type=int, default=2222)
p.add_argument("--ui", default="http://127.0.0.1:3000")
p.add_argument("--listener", default="http://127.0.0.1:8081")
p.add_argument("--kibana", default="http://127.0.0.1:5601")
p.add_argument("--es", default="http://127.0.0.1:9200")
a = p.parse_args()

env = dict(l.split("=", 1) for l in open(a.env_file).read().splitlines() if "=" in l and not l.startswith("#"))
ADMIN = {"Authorization": f"Bearer {env['ADMIN_TOKEN']}"}
ES_AUTH = ("elastic", env["ELASTIC_PASSWORD"])
failed = 0


def check(cond: bool, msg: str) -> None:
    global failed
    print(("PASS " if cond else "FAIL ") + msg)
    failed += 0 if cond else 1


def compose_exec(service: str, cmd: str) -> str:
    full = f"docker compose {a.compose_args} --env-file {a.env_file} --profile honeypot --profile elk exec -T {service} {cmd}"
    return subprocess.run(shlex.split(full), capture_output=True, text=True).stdout


def wait_for(fn, timeout=90, every=3):
    end = time.time() + timeout
    while time.time() < end:
        try:
            r = fn()
            if r:
                return r
        except Exception:
            pass
        time.sleep(every)
    return None


def es_search(query: dict) -> list:
    r = httpx.post(f"{a.es}/deception-events-*/_search", auth=ES_AUTH, json=query, timeout=10)
    return r.json().get("hits", {}).get("hits", []) if r.status_code == 200 else []


# 1. API reachable through the UI proxy with auth; unauthenticated is refused
check(httpx.get(f"{a.ui}/api/v1/tokens").status_code == 401, "API refuses unauthenticated requests via the UI proxy")
tokens = httpx.get(f"{a.ui}/api/v1/tokens", headers=ADMIN).json()
check(any(t["name"].startswith("Honeypot breadcrumb") for t in tokens), "generator created breadcrumb tokens")

# 2. breadcrumbs are inside the honeypot's files and point at the canary
todo = compose_exec("honeypot", "cat /home/sysadmin/todo.txt")
trap = next((w for w in todo.split() if "/t/" in w), None)
check(trap is not None, f"breadcrumb URL present in honeypot todo.txt ({trap})")

# 3. trap hit -> SSE push (Postgres LISTEN/NOTIFY path) -> alert
got = threading.Event()


def listen():
    with httpx.stream("GET", f"{a.ui}/api/v1/stream", headers=ADMIN, timeout=60) as r:
        for line in r.iter_lines():
            if line.startswith("event: alert"):
                got.set()
                return


threading.Thread(target=listen, daemon=True).start()
time.sleep(2)
before = len(httpx.get(f"{a.ui}/api/v1/alerts", headers=ADMIN).json())
r = httpx.get(trap.replace("http://127.0.0.1:8081", a.listener), headers={"User-Agent": "smoke-test/1.0"})
check(r.status_code == 403, "trap link answers with the decoy 403")
check(got.wait(10), "dashboard SSE stream received the alert event")
alerts = httpx.get(f"{a.ui}/api/v1/alerts", headers=ADMIN).json()
check(len(alerts) == before + 1 and alerts[0]["user_agent"] == "smoke-test/1.0", "alert stored in Postgres with the request details")

# 4. canary event indexed in Elasticsearch by the least-privilege writer
hits = wait_for(lambda: es_search({"query": {"term": {"event.action": "canary_triggered"}}}))
check(bool(hits), "canary event indexed in Elasticsearch")
if hits:
    d = hits[0]["_source"]
    check(d["deception"]["sensor"] == "canary-listener" and d["user_agent"]["original"] == "smoke-test/1.0", "canary event has the shared schema")

# 5. SSH attack -> filebeat -> logstash -> elasticsearch
try:
    import paramiko

    for user, pw in (("root", "wrong"), ("admin", "admin123"), ("sysadmin", "sysadmin")):
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            c.connect("127.0.0.1", port=a.ssh_port, username=user, password=pw, timeout=10, allow_agent=False, look_for_keys=False)
            c.close()
        except Exception:
            pass
    ssh = wait_for(lambda: es_search({"query": {"term": {"deception.sensor": "honeypot-ssh"}}, "size": 20}), timeout=120)
    check(bool(ssh), "SSH events parsed by Logstash and indexed")
    actions = {h["_source"]["event"]["action"] for h in (ssh or [])}
    check({"ssh_login_failed", "ssh_login_success"} <= actions, f"failed and successful logins distinguished ({sorted(actions)})")
    check(any(h["_source"].get("user", {}).get("name") == "admin" for h in (ssh or [])), "attacker username captured (user.name)")
except ImportError:
    print("SKIP ssh checks (pip install paramiko)")

# 6. Kibana objects
r = httpx.get(f"{a.kibana}/api/saved_objects/dashboard/deception-overview", auth=ES_AUTH, timeout=15)
check(r.status_code == 200, "Kibana dashboard 'Deception Platform - Overview' exists")

print("SMOKE OK" if not failed else f"SMOKE FAILED ({failed})")
sys.exit(1 if failed else 0)
