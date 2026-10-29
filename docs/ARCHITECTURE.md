# Architecture

## Components
- **canary-listener** — stateless, internet-facing. Answers identically for any id (403 page / 1×1 PNG) so valid and invalid tokens are indistinguishable, extracts the client IP from `X-Forwarded-For` honouring `TRUSTED_PROXY_COUNT` (rightmost-N, so clients can't spoof), strips `Cookie`/`Authorization`, rate-limits per IP, and forwards to the API with a shared key. It never touches the database.
- **api** — owns tokens + alerts (Postgres via SQLAlchemy; SQLite for tests). `/api/v1/*` needs the admin bearer token; `/internal/v1/hits` needs the internal key. On a valid hit it stores the alert, enriches with GeoIP, and publishes an event (stdout JSON, Elasticsearch, optional Slack-style webhook). Disabled/unknown tokens are dropped silently.
- **generator** — runs once before the honeypot (compose service / pod init container). Calls Gemini per `persona_config.json`, then creates canary tokens via the API (idempotent through `external_key`) and appends their URLs to the fake files (`breadcrumbs`). Falls back to canned content if the LLM is unavailable, so the honeypot always boots.
- **honeypot** — Ubuntu with sshd + nginx and *no* secrets or shippers. Seeds files from `/seed`, logs to `/var/log/honeypot`. rsyslog also appends to the decoy `/var/log/auth.log` so what an attacker reads stays consistent with real activity.
- **pipeline** — Filebeat (sidecar) → Logstash (grok → shared schema, GeoIP) → Elasticsearch (template + 90-day ILM) → Kibana (data view, saved searches, dashboard).
- **ui** — React dashboard served by unprivileged nginx which also reverse-proxies `/api` to the API (same origin, no CORS). Polls every 5 s.

## Trust boundaries
Internet → listener (untrusted input, no DB, no admin power) → API (internal key). Internet → honeypot (assume compromise; NetworkPolicy/egress limits; no service-account token, no real secrets). Operators → ui/API (admin token).

## Token types
`url` (`/t/<id>`), `pixel` (`/p/<id>.png`), `document` (a .docx that loads the pixel as a remote image when opened; generated on demand by `GET /api/v1/tokens/<id>/download`).
