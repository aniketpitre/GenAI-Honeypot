import hmac
import time
from collections import defaultdict, deque

from fastapi import Depends, Header, HTTPException, Request, status

from .config import Settings, get_settings


def _check(provided: str | None, expected: str) -> bool:
    if not expected or not provided:
        return False
    return hmac.compare_digest(provided.encode(), expected.encode())


def _bearer(authorization: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


_failures: dict[str, deque[float]] = defaultdict(deque)


def client_ip(request: Request, trusted: int) -> str:
    peer = request.client.host if request.client else "unknown"
    xff = [p.strip() for p in request.headers.get("x-forwarded-for", "").split(",") if p.strip()]
    return xff[-trusted] if trusted > 0 and len(xff) >= trusted else peer


def _recent_failures(ip: str, window: int) -> deque[float]:
    now = time.monotonic()
    q = _failures[ip]
    while q and now - q[0] > window:
        q.popleft()
    if not q:
        _failures.pop(ip, None)
        q = _failures[ip]
    return q


def require_admin(
    request: Request,
    authorization: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    ip = client_ip(request, settings.trusted_proxy_count)
    failures = _recent_failures(ip, settings.auth_fail_window_seconds)
    if len(failures) >= settings.auth_fail_limit:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "too many failed attempts; try again later",
                            headers={"Retry-After": str(settings.auth_fail_window_seconds)})
    if not _check(_bearer(authorization), settings.admin_token):
        failures.append(time.monotonic())
        if len(_failures) > 10_000:  # bound memory under spoofed-address floods
            _failures.clear()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid or missing admin token")


def require_internal(
    x_internal_key: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    if not _check(x_internal_key, settings.internal_api_key):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid internal key")
