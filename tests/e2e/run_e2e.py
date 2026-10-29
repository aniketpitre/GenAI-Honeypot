"""End-to-end smoke test without Docker: real API + listener processes, the
generator planting breadcrumbs, a trap hit, and an API outage in the middle
(the hit must be spooled and delivered after the API comes back).

    python tests/e2e/run_e2e.py        (needs services' requirements installed)
"""
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
ADMIN = "e2e-admin-token-0123456789abcdef"
INTERNAL = "e2e-internal-key-0123456789abcdef"
API, LISTENER = "http://127.0.0.1:18080", "http://127.0.0.1:18081"
procs: list[subprocess.Popen] = []


def start(service: str, port: int, env: dict) -> subprocess.Popen:
    p = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(port), "--log-level", "warning"],
        cwd=ROOT / "services" / service, env={**os.environ, **env},
    )
    procs.append(p)
    return p


def wait(url: str, timeout: float = 20) -> None:
    end = time.time() + timeout
    while time.time() < end:
        try:
            if httpx.get(url, timeout=1).status_code == 200:
                return
        except Exception:
            time.sleep(0.2)
    raise SystemExit(f"timeout waiting for {url}")


def check(cond: bool, msg: str) -> None:
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        raise SystemExit(1)


def main() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="e2e-"))
    api_env = {"ADMIN_TOKEN": ADMIN, "INTERNAL_API_KEY": INTERNAL, "CANARY_BASE_URL": LISTENER,
               "DATABASE_URL": f"sqlite:///{tmp}/e2e.db"}
    ls_env = {"API_URL": API, "INTERNAL_API_KEY": INTERNAL, "TRUSTED_PROXY_COUNT": "0",
              "SPOOL_DIR": str(tmp / "spool"), "SPOOL_RETRY_SECONDS": "0.5"}
    try:
        api = start("api", 18080, api_env)
        start("canary-listener", 18081, ls_env)
        wait(f"{API}/readyz"); wait(f"{LISTENER}/healthz")
        h = {"Authorization": f"Bearer {ADMIN}"}

        gen = subprocess.run(
            [sys.executable, "-m", "generator.generate", "--output", str(tmp / "seed")],
            cwd=ROOT / "services" / "generator", env={**os.environ, "API_URL": API, "ADMIN_TOKEN": ADMIN,
                                                    "GEMINI_API_KEY": ""})
        check(gen.returncode == 0, "generator ran and planted breadcrumbs")
        todo = (tmp / "seed/home/sysadmin/todo.txt").read_text()
        trap = next(w for w in todo.split() if "/t/" in w)

        r = httpx.get(trap)
        check(r.status_code == 403, "trap link returns decoy 403")
        time.sleep(1)
        alerts = httpx.get(f"{API}/api/v1/alerts", headers=h).json()
        check(len(alerts) == 1 and alerts[0]["ip"] == "127.0.0.1", "hit became an alert with client IP")

        # --- API outage: hit must be spooled, then delivered on recovery ----------
        api.send_signal(signal.SIGTERM); api.wait(timeout=10); procs.remove(api)
        httpx.get(trap)
        time.sleep(1)
        check((tmp / "spool/pending.jsonl").exists() and (tmp / "spool/pending.jsonl").read_text().strip() != "",
              "hit spooled to disk while API is down")
        start("api", 18080, api_env)
        wait(f"{API}/readyz")
        deadline = time.time() + 15
        while time.time() < deadline and len(httpx.get(f"{API}/api/v1/alerts", headers=h).json()) < 2:
            time.sleep(0.5)
        check(len(httpx.get(f"{API}/api/v1/alerts", headers=h).json()) == 2, "spooled hit delivered after API recovered")
        check("deception_hits_total" in httpx.get(f"{API}/metrics").text, "metrics exposed")
        print("E2E OK")
    finally:
        for p in procs:
            p.terminate()


if __name__ == "__main__":
    main()
