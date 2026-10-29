# Deception Platform — AI Honeypot + Canary Tokens

A self-hosted deception platform. It catches attackers three ways and routes every signal into **one alert pipeline, one dashboard and one Kibana view**, deployable with Docker Compose or Kubernetes.

| Sensor | What it catches | How |
|---|---|---|
| **Honeypot** (SSH + web) | Attackers probing a fake Debian server | Bait filesystem written by Gemini (`auth.log`, `.bash_history`, `todo.txt`); SSH/nginx logs shipped Filebeat → Logstash → Elasticsearch |
| **Canary tokens** | Someone using stolen data, a leaked cloud credential or cluster access, or opening a planted document — **anywhere** | A unique link / pixel / endpoint → `canary-listener` → API → alert with real IP, GeoIP and headers |
| **Breadcrumbs** | Attackers who steal the honeypot's files and use them elsewhere | The generator plants canary URLs *inside* the fake files, so exfiltrated bait phones home |

```
                       ┌─────────────────┐  hit   ┌─────────┐        ┌────────────┐
 attacker / leaked link ▶ canary-listener  ├──────▶ │   API   ├──────▶ │ PostgreSQL │
                       └─────────────────┘ (spool) │ FastAPI │        │ tokens,    │
                                                   └─┬────┬──┘        │ alerts     │
 dashboard (React) ◀── live updates (SSE) ───────────┘    │           └────────────┘
                                                          ▼ events (+ Slack-style webhook)
 attacker ─▶ honeypot (sshd+nginx) ─logs▶ filebeat ─▶ logstash ─▶ Elasticsearch ─▶ Kibana
                 ▲
   generator (init job): Gemini content + canary breadcrumbs
```

## Features

- **Five canary token types**

  | Type | Plant it | Fires when |
  |---|---|---|
  | URL / tracking pixel | wikis, emails, web pages | the link or image is fetched |
  | Word document | file shares, mailboxes | the document is opened with external content on |
  | Fake AWS credentials | repos, laptops, CI variables | any `aws`/SDK call uses the profile (its `endpoint_url` is the canary); the decoy access-key id is recorded |
  | Fake kubeconfig | repos, home dirs, CI secrets | `kubectl` / `k9s` / client libraries use it (verified with a real `kubectl`) |

- **Live dashboard** — new alerts appear within a fraction of a second over server-sent events (fanned out across API replicas with Postgres `LISTEN/NOTIFY`); triage status, analyst notes, token management, and a "top sources" panel that highlights an IP touching several *different* tokens (almost always a real intruder, not a scanner).
- **Never lose an alert** — the listener spools hits to disk and retries (in order) if the API is down or rejects its key; the API de-duplicates redeliveries.
- **One event schema** (`docs/EVENT_SCHEMA.md`, ECS-flavoured) for SSH, web and canary events → one Elasticsearch index (`deception-events-*`, 90-day ILM) and one Kibana dashboard.
- **AI-generated bait** with Gemini (canned fallback without a key); decoy-URL suggestions for URL tokens.
- **Production-minded** — hardened containers, NetworkPolicies, Elasticsearch security, External Secrets, hash-locked dependencies, signed releases, Prometheus metrics/alerts, runbook. See [Status](#status--what-is-verified).

## Quick start (Docker Compose)

```bash
cp .env.example .env     # fill POSTGRES_PASSWORD, ADMIN_TOKEN, INTERNAL_API_KEY  (openssl rand -hex 32)
                         # for --profile elk also ELASTIC_PASSWORD, ES_WRITER_PASSWORD, KIBANA_PASSWORD
                         # and set ELASTICSEARCH_URL=http://elasticsearch:9200
make up                  # core: postgres, api, canary-listener, dashboard
make up-all              # + honeypot, filebeat, elasticsearch, logstash, kibana
```

| What | Where |
|---|---|
| Dashboard | http://localhost:3000 — sign in with `ADMIN_TOKEN` |
| Canary listener | http://localhost:8081 (set `CANARY_BASE_URL` to its **public** address before creating tokens) |
| Kibana | http://localhost:5601 (user `elastic`) → "Deception Platform - Overview" |
| Honeypot | `ssh sysadmin@localhost -p 2222` (password `sysadmin`) and http://localhost:8088 |

Try it: create a **Fake Kubeconfig** token in the dashboard, download it, run `kubectl --kubeconfig <file> get pods`, and watch the alert appear.

> `ADMIN_TOKEN` and `INTERNAL_API_KEY` must be at least 24 characters; the API refuses to start otherwise.

## Kubernetes (Helm)

```bash
helm install dp deploy/helm/deception-platform \
  --set secrets.adminToken=$(openssl rand -hex 32) --set secrets.internalApiKey=$(openssl rand -hex 32) \
  --set secrets.databaseUrl='postgresql+psycopg://user:pass@db:5432/deception' \
  --set canary.baseUrl=https://files.example.com \
  --set ingress.dashboardHost=dashboard.example.com --set ingress.canaryHost=files.example.com
# demo cluster: add --set dev.postgres.enabled=true --set dev.elk.enabled=true --set dev.elk.password=<pw>
```

For production use `deploy/helm/deception-platform/values.production.yaml` and follow **[`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)**: secrets via External Secrets Operator, managed Postgres/Elasticsearch, a dedicated gVisor node pool for the honeypot ([`deploy/isolation/`](deploy/isolation)), a verification checklist. Day-2 tasks (rotation, upgrades, backups, alert playbooks) are in **[`docs/RUNBOOK.md`](docs/RUNBOOK.md)**.

## Configuration (environment variables)

| Variable | Service | Purpose |
|---|---|---|
| `ADMIN_TOKEN` | api | bearer token for the dashboard/admin API (≥ 24 chars); 10 failed attempts per client IP → 429 for 5 min |
| `INTERNAL_API_KEY` | api, listener | shared secret for `/internal/v1/hits` (≥ 24 chars) |
| `DATABASE_URL` | api | `postgresql+psycopg://…` (SQLite for local dev); migrations run at start-up |
| `CANARY_BASE_URL` | api | public URL tokens point at |
| `ELASTICSEARCH_URL`, `_USER`, `_PASSWORD` / `_API_KEY`, `_CA_FILE` | api | direct event indexing (least-privilege writer) |
| `WEBHOOK_URL` | api | Slack-compatible alert webhook |
| `GEMINI_API_KEY`, `GEMINI_MODEL` | api, generator | AI bait and decoy URLs (optional) |
| `GEOIP_DB_PATH` | api | MaxMind GeoLite2-City file (optional; not bundled — licence) |
| `TRUSTED_PROXY_COUNT` | api, listener | reverse proxies that append to `X-Forwarded-For` (client-IP attribution) |
| `RATE_LIMIT_PER_MINUTE`, `SPOOL_DIR`, `SPOOL_MAX_ENTRIES` | listener | per-IP limit; on-disk retry queue |
| `HONEYPOT_USERS` | honeypot | intentionally weak bait logins (`user:pass,…`) |

`.env.example` lists the Compose variables; Helm values are documented in `deploy/helm/deception-platform/values.yaml`.

## Development & testing

```bash
make test               # unit tests: api, canary-listener, generator (pytest)
make e2e                # real processes, no Docker: generator → trap → alert → SSE, plus API-outage recovery
make ui-build           # typecheck + production build of the dashboard
make smoke              # full-stack check against a running `make up-all` stack
make prometheus-test    # promtool unit tests for the chart's alert rules (helm + docker)
make helm-lint          # lint the chart; make sync-chart after editing pipeline/ configs
```

CI (`.github/workflows`): unit tests, UI build, e2e, a full-stack compose smoke job, Helm lint + Kubernetes/CRD schema validation, alert-rule tests, image builds, and a security workflow (pip-audit, npm audit, Trivy). Tagging `vX.Y.Z` publishes SBOM-attached, cosign-signed images to GHCR.

## Layout

```
services/api               FastAPI: tokens, alerts, SSE, event publishing, migrations (Alembic)
services/canary-listener   public trap endpoints (/t /p /aws /k8s), spool + retry, rate limit
services/generator         Gemini bait + breadcrumb planting (compose service / pod init container)
services/honeypot          sshd + nginx bait container (no secrets inside)
services/ui                Tripwire dashboard (React / Vite / Tailwind)
pipeline/                  filebeat, logstash, Elasticsearch template + ILM, Kibana objects, bootstrap script
deploy/helm/               Helm chart (+ values.production.yaml)
deploy/isolation/          gVisor RuntimeClass, Pod Security namespace, Cilium egress, GKE/EKS Terraform examples
tests/                     e2e (no-Docker flow, compose smoke, UI smoke), prometheus rule tests
docs/                      ARCHITECTURE, EVENT_SCHEMA, DEPLOYMENT, RUNBOOK, PRODUCTION_READINESS, legacy/
```

## Status — what is verified

Verified (real containers / tools, in the authoring environment):
- Unit tests (API 23, listener 9, generator 2), the no-Docker e2e flow, UI typecheck/build.
- All five images build from hash-locked requirements.
- The **full stack under Docker Compose** — Postgres, Elasticsearch 8.14 with security on, Kibana, Logstash, Filebeat — passes `tests/e2e/compose_smoke.py` 12/12: breadcrumbs planted, trap hit → alert → live push → Elasticsearch, SSH attack → Filebeat → Logstash → Elasticsearch, Kibana dashboard present. A real browser showed a new alert 228 ms after the hit.
- A real `kubectl` using the generated kubeconfig token raises an alert.
- Helm chart: lint plus Kubernetes and CRD schema validation (including `PrometheusRule` and `ExternalSecret`) for default, demo and production values.

**Not yet verified** — please check before relying on it:
- an install on a real Kubernetes cluster (use a staging cluster and `docs/DEPLOYMENT.md`);
- the GitHub Actions workflows (none had run when this was written);
- the Prometheus alert-rule unit tests and the Grafana dashboard against live Prometheus/Grafana;
- `terraform apply` of the isolation examples (they only parse), and the `aws` CLI against the fake-AWS token.

Known limits and the prioritised backlog (DNS tokens, incident grouping, an interactive LLM shell, SIEM export, …) are in [`docs/PRODUCTION_READINESS.md`](docs/PRODUCTION_READINESS.md).

## Safety

The honeypot has intentionally weak credentials and is *meant* to be compromised. Run it only on an isolated network or cluster, never alongside real workloads, and never put real data in the seed content. Deploy only on infrastructure you own or are authorised to monitor.

History: this repo absorbed [TripWire-Sentinel](https://github.com/aniketpitre/TripWire-Sentinel) (its history is preserved under `services/ui`).
