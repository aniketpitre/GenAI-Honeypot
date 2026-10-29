"""Public, stateless endpoint that canary tokens point at. It always answers
the same way for every id (valid or not) and forwards the hit to the API."""
import asyncio
import base64
import logging
import time
import uuid
from contextlib import asynccontextmanager
from collections import defaultdict, deque

import httpx
from fastapi import BackgroundTasks, FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest
from pydantic_settings import BaseSettings, SettingsConfigDict

from .spool import Spool

log = logging.getLogger("canary-listener")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")
    api_url: str = "http://api:8080"
    internal_api_key: str = ""
    # Number of trusted reverse proxies in front (ingress, LB) appending to X-Forwarded-For.
    trusted_proxy_count: int = 1
    rate_limit_per_minute: int = 60
    spool_dir: str = "/tmp/canary-spool"
    spool_max_entries: int = 10000
    spool_retry_seconds: float = 5.0
    log_level: str = "INFO"


settings = Settings()

HITS = Counter("canary_hits_total", "Trap requests received", ["outcome"])  # forwarded|spooled|dropped|rate_limited
SPOOL_SIZE = Gauge("canary_spool_size", "Hits waiting for the API")

spool: Spool | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global spool
    logging.basicConfig(level=settings.log_level)
    spool = Spool(settings.spool_dir, settings.spool_max_entries)
    SPOOL_SIZE.set(spool.size())
    task = asyncio.create_task(retry_loop())
    yield
    task.cancel()


async def retry_loop() -> None:
    while True:
        await asyncio.sleep(settings.spool_retry_seconds)
        if spool and spool.size():
            SPOOL_SIZE.set(await spool.drain(post_hit))


app = FastAPI(title="Canary Listener", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)

PIXEL = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)
DECOY = """<!doctype html><html><head><title>403 Forbidden</title></head>
<body style="font-family:sans-serif"><h1>403 Forbidden</h1><p>You don't have permission to access this resource.</p></body></html>"""
DROP_HEADERS = {"cookie", "authorization", "proxy-authorization"}

_hits: dict[str, deque[float]] = defaultdict(deque)


def client_ip(request: Request, trusted: int) -> str:
    peer = request.client.host if request.client else "0.0.0.0"
    xff = [p.strip() for p in request.headers.get("x-forwarded-for", "").split(",") if p.strip()]
    # The rightmost `trusted` entries were added by our own proxies; the one
    # before them is the first address we can attribute to the client.
    if trusted > 0 and len(xff) >= trusted:
        return xff[-trusted]
    return peer


def allowed(ip: str, limit: int) -> bool:
    now = time.monotonic()
    q = _hits[ip]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= limit:
        return False
    q.append(now)
    if len(_hits) > 10_000:  # bound memory under address-spoofing floods
        for k in [k for k, v in _hits.items() if not v or now - v[-1] > 60]:
            del _hits[k]
    return True


async def post_hit(payload: dict) -> bool:
    url = f"{settings.api_url.rstrip('/')}/internal/v1/hits"
    try:
        async with httpx.AsyncClient(timeout=3) as c:
            r = await c.post(url, json=payload, headers={"X-Internal-Key": settings.internal_api_key})
        if r.status_code >= 500 or r.status_code in (401, 403, 429):
            if r.status_code in (401, 403):
                log.error("API refused our key (%s): check INTERNAL_API_KEY; hits are being spooled", r.status_code)
            return False
        if r.status_code >= 400:
            log.error("API rejected hit with %s (dropping): %s", r.status_code, r.text[:200])
        return True
    except Exception as exc:
        log.warning("API unreachable: %s", exc)
        return False


async def forward(payload: dict) -> None:
    if await post_hit(payload):
        HITS.labels("forwarded").inc()
    elif spool and await spool.add(payload):
        HITS.labels("spooled").inc()
        SPOOL_SIZE.set(spool.size())
    else:
        HITS.labels("dropped").inc()
        log.error("hit lost: API down and spool unavailable/full")


def _record(request: Request, token_id: str, bg: BackgroundTasks) -> None:
    ip = client_ip(request, settings.trusted_proxy_count)
    if not allowed(ip, settings.rate_limit_per_minute):
        HITS.labels("rate_limited").inc()
        return
    headers = {k: v[:500] for k, v in request.headers.items() if k.lower() not in DROP_HEADERS}
    bg.add_task(forward, {
        "hit_id": uuid.uuid4().hex, "token_id": token_id[:64], "ip": ip, "path": request.url.path,
        "user_agent": request.headers.get("user-agent", "")[:2000], "headers": headers,
    })


@app.api_route("/t/{token_id}", methods=["GET", "HEAD", "POST"])
async def trap(token_id: str, request: Request, bg: BackgroundTasks):
    _record(request, token_id, bg)
    return HTMLResponse(DECOY, status_code=403)


@app.get("/p/{token_id}.png")
async def pixel(token_id: str, request: Request, bg: BackgroundTasks):
    _record(request, token_id, bg)
    return Response(PIXEL, media_type="image/png", headers={"Cache-Control": "no-store"})


@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok"}


@app.get("/metrics", include_in_schema=False)
def metrics():
    # Not routed by the ingress (only /t/ and /p/ are); scrape in-cluster.
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
