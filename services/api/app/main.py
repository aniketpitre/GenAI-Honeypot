import logging
import secrets
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import db as dbm
from .config import Settings, get_settings
from .db import Alert, Token, get_db
from .docx_canary import build_docx
from .events import canary_event, publish
from .geo import lookup
from .schemas import (
    AlertOut, AlertUpdate, GenerateUrlsIn, HitIn, TokenCreate, TokenOut, TokenUpdate,
)
from .security import require_admin, require_internal
from .urlgen import generate_deceptive_urls

log = logging.getLogger("deception.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    s = get_settings()
    logging.basicConfig(level=s.log_level)
    if dbm._engine is None:
        dbm.init_engine()
    if not s.admin_token or not s.internal_api_key:
        log.warning("ADMIN_TOKEN / INTERNAL_API_KEY not set: authenticated routes will reject all requests")
    yield


app = FastAPI(title="Deception Platform API", version="0.1.0", lifespan=lifespan)

_s = get_settings()
if _s.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in _s.cors_origins.split(",") if o.strip()],
        allow_methods=["*"],
        allow_headers=["*"],
    )


def trap_url(token: Token, s: Settings) -> str:
    base = s.canary_base_url.rstrip("/")
    return f"{base}/p/{token.id}.png" if token.type in ("pixel", "document") else f"{base}/t/{token.id}"


def token_out(token: Token, count: int, s: Settings) -> TokenOut:
    return TokenOut(
        id=token.id, name=token.name, type=token.type, status=token.status,
        value=trap_url(token, s), decoy_url=token.decoy_url,
        created_at=token.created_at, alert_count=count,
    )


def alert_out(a: Alert) -> AlertOut:
    return AlertOut(
        id=a.id, token_id=a.token_id, token_name=a.token.name, timestamp=a.timestamp,
        ip=a.ip, city=a.city, country=a.country, lat=a.lat, lon=a.lon,
        user_agent=a.user_agent, request_path=a.request_path, request_headers=a.request_headers,
        notes=a.notes, status=a.status,
    )


def _count(db: Session, token_id: str) -> int:
    return db.scalar(select(func.count()).select_from(Alert).where(Alert.token_id == token_id)) or 0


# ---- health -----------------------------------------------------------------
@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok"}


@app.get("/readyz", include_in_schema=False)
def readyz():
    try:
        dbm.ping()
    except Exception:
        raise HTTPException(503, "database unavailable")
    return {"status": "ready"}


# ---- tokens -----------------------------------------------------------------
@app.get("/api/v1/tokens", response_model=list[TokenOut], dependencies=[Depends(require_admin)])
def list_tokens(db: Session = Depends(get_db), s: Settings = Depends(get_settings)):
    counts = dict(db.execute(select(Alert.token_id, func.count()).group_by(Alert.token_id)).all())
    rows = db.scalars(select(Token).order_by(Token.created_at.desc())).all()
    return [token_out(t, counts.get(t.id, 0), s) for t in rows]


@app.post("/api/v1/tokens", response_model=TokenOut, status_code=201, dependencies=[Depends(require_admin)])
def create_token(
    body: TokenCreate, response: Response,
    db: Session = Depends(get_db), s: Settings = Depends(get_settings),
):
    if body.external_key:
        existing = db.scalar(select(Token).where(Token.external_key == body.external_key))
        if existing:
            response.status_code = 200
            return token_out(existing, _count(db, existing.id), s)
    token = Token(
        id=secrets.token_urlsafe(12), name=body.name, type=body.type,
        decoy_url=body.decoy_url, external_key=body.external_key,
    )
    db.add(token)
    db.commit()
    return token_out(token, 0, s)


def _get_token(db: Session, token_id: str) -> Token:
    token = db.get(Token, token_id)
    if not token:
        raise HTTPException(404, "token not found")
    return token


@app.patch("/api/v1/tokens/{token_id}", response_model=TokenOut, dependencies=[Depends(require_admin)])
def update_token(token_id: str, body: TokenUpdate, db: Session = Depends(get_db), s: Settings = Depends(get_settings)):
    token = _get_token(db, token_id)
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(token, k, v)
    db.commit()
    return token_out(token, _count(db, token.id), s)


@app.delete("/api/v1/tokens/{token_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_token(token_id: str, db: Session = Depends(get_db)):
    db.delete(_get_token(db, token_id))
    db.commit()


@app.get("/api/v1/tokens/{token_id}/download", dependencies=[Depends(require_admin)])
def download_token(token_id: str, db: Session = Depends(get_db), s: Settings = Depends(get_settings)):
    token = _get_token(db, token_id)
    if token.type != "document":
        raise HTTPException(400, "only document tokens can be downloaded")
    data = build_docx(trap_url(token, s), token.name)
    return Response(
        data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{token.id}.docx"'},
    )


# ---- alerts -----------------------------------------------------------------
@app.get("/api/v1/alerts", response_model=list[AlertOut], dependencies=[Depends(require_admin)])
def list_alerts(
    status: str | None = None, limit: int = Query(200, ge=1, le=1000), db: Session = Depends(get_db),
):
    q = select(Alert).order_by(Alert.timestamp.desc()).limit(limit)
    if status:
        q = q.where(Alert.status == status)
    return [alert_out(a) for a in db.scalars(q).all()]


@app.patch("/api/v1/alerts/{alert_id}", response_model=AlertOut, dependencies=[Depends(require_admin)])
def update_alert(alert_id: int, body: AlertUpdate, db: Session = Depends(get_db)):
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(404, "alert not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(alert, k, v)
    db.commit()
    return alert_out(alert)


@app.post("/api/v1/generate/urls", dependencies=[Depends(require_admin)])
def generate_urls(body: GenerateUrlsIn):
    return {"urls": generate_deceptive_urls(body.prompt)}


# ---- internal: canary listener -> API -------------------------------------------
@app.post("/internal/v1/hits", status_code=202, dependencies=[Depends(require_internal)])
async def record_hit(hit: HitIn, bg: BackgroundTasks, db: Session = Depends(get_db)):
    token = db.get(Token, hit.token_id)
    # Unknown/disabled tokens are dropped silently so the listener (and thus the
    # attacker) can't distinguish them.
    if not token or token.status != "active":
        return {"recorded": False}
    geo = lookup(hit.ip)
    alert = Alert(
        token_id=token.id, ip=hit.ip, user_agent=hit.user_agent, request_path=hit.path,
        request_headers=hit.headers, **geo,
    )
    db.add(alert)
    db.commit()
    bg.add_task(publish, canary_event(token, alert))
    return {"recorded": True}
