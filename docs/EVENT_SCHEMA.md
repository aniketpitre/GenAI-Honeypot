# Event schema

Every sensor emits an ECS-flavoured document into `deception-events-YYYY.MM.DD`
(mapping: `pipeline/elasticsearch/index-template.json`).

| Field | Type | Notes |
|---|---|---|
| `@timestamp` | date | |
| `event.kind` | keyword | `alert` (canary) or `event` (honeypot telemetry) |
| `event.category` | keyword | `intrusion_detection`, `authentication`, `web` |
| `event.action` | keyword | `canary_triggered`, `ssh_login_failed`, `ssh_login_success`, `ssh_invalid_user`, `http_request` |
| `event.dataset` | keyword | `deception.canary`, `deception.ssh`, `deception.nginx` |
| `event.outcome` | keyword | `success` / `failure` (SSH) |
| `deception.sensor` | keyword | `canary-listener`, `honeypot-ssh`, `honeypot-web` |
| `deception.token.{id,name,type}` | keyword | canary events only |
| `source.ip` | ip | real client IP |
| `source.geo.{city_name,country_iso_code,location}` | keyword/geo_point | GeoIP (needs MaxMind DB) |
| `user.name` | keyword | SSH username tried |
| `user_agent.original`, `url.path`, `http.*` | | web-style events |

Adding a sensor = emit this shape (stdout JSON, Logstash filter, or direct ES write).
