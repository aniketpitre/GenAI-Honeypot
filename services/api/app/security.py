import hmac

from fastapi import Depends, Header, HTTPException, status

from .config import Settings, get_settings


def _check(provided: str | None, expected: str) -> bool:
    if not expected or not provided:
        return False
    return hmac.compare_digest(provided.encode(), expected.encode())


def _bearer(authorization: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


def require_admin(
    authorization: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    if not _check(_bearer(authorization), settings.admin_token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid or missing admin token")


def require_internal(
    x_internal_key: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    if not _check(x_internal_key, settings.internal_api_key):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid internal key")
