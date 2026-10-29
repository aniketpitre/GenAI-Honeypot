"""Shared event schema (ECS-flavoured). Every sensor - canary, SSH, HTTP lure -
produces documents of this shape so one Kibana data view covers everything."""
import json
import logging
import sys
from datetime import datetime, timezone

import httpx

from .config import get_settings
from .db import Alert, Token
from .metrics import EVENT_PUBLISH_FAILURES

event_log = logging.getLogger("deception.events")
if not event_log.handlers:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("%(message)s"))
    event_log.addHandler(h)
    event_log.propagate = False
    event_log.setLevel(logging.INFO)

log = logging.getLogger(__name__)


def canary_event(token: Token, alert: Alert) -> dict:
    ts = alert.timestamp
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return {
        "@timestamp": ts.isoformat(),
        "event": {
            "kind": "alert",
            "category": ["intrusion_detection"],
            "action": "canary_triggered",
            "dataset": "deception.canary",
            "severity": 80,
        },
        "source": {
            "ip": alert.ip,
            "geo": {
                "city_name": alert.city,
                "country_iso_code": alert.country,
                **({"location": {"lat": alert.lat, "lon": alert.lon}} if alert.lat or alert.lon else {}),
            },
        },
        "user_agent": {"original": alert.user_agent},
        "url": {"path": alert.request_path},
        "http": {"request": {"headers": alert.request_headers}},
        "deception": {
            "sensor": "canary-listener",
            "alert_id": alert.id,
            "token": {"id": token.id, "name": token.name, "type": token.type},
        },
    }


async def publish(event: dict) -> None:
    """stdout (for log shippers) + best-effort direct write to Elasticsearch + webhook."""
    event_log.info(json.dumps(event, separators=(",", ":")))
    s = get_settings()
    async with httpx.AsyncClient(timeout=5) as client:
        if s.elasticsearch_url:
            day = datetime.now(timezone.utc).strftime("%Y.%m.%d")
            url = f"{s.elasticsearch_url.rstrip('/')}/{s.elasticsearch_index_prefix}-{day}/_doc"
            try:
                (await client.post(url, json=event)).raise_for_status()
            except Exception as exc:
                EVENT_PUBLISH_FAILURES.labels("elasticsearch").inc()
                log.warning("elasticsearch write failed: %s", exc)
        if s.webhook_url:
            tok = event["deception"]["token"]
            text = (
                f":rotating_light: Canary *{tok['name']}* triggered from "
                f"{event['source']['ip']} ({event['source']['geo'].get('country_iso_code') or '??'})"
            )
            try:
                await client.post(s.webhook_url, json={"text": text})
            except Exception as exc:
                EVENT_PUBLISH_FAILURES.labels("webhook").inc()
                log.warning("webhook failed: %s", exc)
