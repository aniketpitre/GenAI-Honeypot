import ipaddress
import logging
from functools import lru_cache

from .config import get_settings

log = logging.getLogger(__name__)
UNKNOWN = {"city": "", "country": "", "lat": 0.0, "lon": 0.0}


@lru_cache
def _reader():
    path = get_settings().geoip_db_path
    if not path:
        return None
    try:
        import geoip2.database

        return geoip2.database.Reader(path)
    except Exception as exc:  # missing file or lib: degrade to "unknown"
        log.warning("GeoIP disabled: %s", exc)
        return None


def lookup(ip: str) -> dict:
    try:
        if not ipaddress.ip_address(ip).is_global:
            return dict(UNKNOWN)
    except ValueError:
        return dict(UNKNOWN)
    reader = _reader()
    if reader is None:
        return dict(UNKNOWN)
    try:
        r = reader.city(ip)
        return {
            "city": r.city.name or "",
            "country": r.country.iso_code or "",
            "lat": r.location.latitude or 0.0,
            "lon": r.location.longitude or 0.0,
        }
    except Exception:
        return dict(UNKNOWN)
