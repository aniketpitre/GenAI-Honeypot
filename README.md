# Deception Platform — AI Honeypot + Canary Tokens

One project, two kinds of tripwire, one alert pipeline:

| Sensor | What it catches | How |
|---|---|---|
| **Honeypot** (SSH + web) | Attackers poking at a fake Debian server | Bait filesystem written by Gemini (`auth.log`, `.bash_history`, `todo.txt`); SSH/nginx logs shipped Filebeat → Logstash → Elasticsearch |
| **Canary tokens** (URL, pixel, Word doc, fake AWS keys, fake kubeconfig) | Someone using stolen data, a leaked cloud credential or cluster access, or opening a planted document, **anywhere** | Unique link/pixel/endpoint → `canary-listener` → API → alert with real IP, GeoIP, headers (and the decoy AWS key id used) |
| **Breadcrumbs** | Attackers who steal the honeypot's files and use them elsewhere | The generator plants canary URLs *inside* the fake files, so exfiltrated bait phones home |

All events share one schema (`docs/EVENT_SCHEMA.md`) and land in the same Elasticsearch index (`deception-events-*`), so a single Kibana dashboard shows SSH brute-force, web probes and canary hits side by side. The React dashboard (Tripwire) is for triage: alert status, analyst notes, token management.

```
                       ┌──────────────┐  hit   ┌─────────┐        ┌────────────┐
 attacker/leaked link ─▶ canary-listener ─────▶│   API   │──────▶ │ Postgres   │
                       └──────────────┘        │ FastAPI │──┬───▶ │ (tokens,   │
                                               └────▲────┘  │     │  alerts)   │
 dashboard (React) ─────────────────────────────────┘       │     └────────────┘
                                                            ▼ events (+ Slack webhook)
 attacker ─▶ honeypot (sshd+nginx) ─logs▶ filebeat ─▶ logstash ─▶ Elasticsearch ─▶ Kibana
                 ▲
   generator (init job): Gemini content + canary breadcrumbs
```

### Token types
| Type | Plant it | Fires when |
|---|---|---|
| URL / pixel | wikis, emails, web pages | the link or image is fetched |
| Word document | file shares, mailboxes | the doc is opened with external content on |
| Fake AWS keys | repos, laptops, CI variables | any `aws`/SDK call uses the profile (its `endpoint_url` is the canary) |
| Fake kubeconfig | repos, home dirs, CI secrets | `kubectl`/`k9s`/client libs use it (verified with real kubectl) |

The dashboard shows an IP that touches several *different* tokens in red: that is almost always a real intruder rather than a scanner.

## Quick start (Docker Compose)

```bash
cp .env.example .env            # fill POSTGRES_PASSWORD, ADMIN_TOKEN, INTERNAL_API_KEY (openssl rand -hex 32)
make up                         # core: postgres, api, canary-listener, dashboard
make up-all                     # + honeypot, filebeat, elasticsearch, logstash, kibana
```

- Dashboard: http://localhost:3000 — sign in with `ADMIN_TOKEN`
- Canary listener: http://localhost:8081 (set `CANARY_BASE_URL` to its public address)
- Kibana: http://localhost:5601 → dashboard "Deception Platform - Overview" (needs `ELASTICSEARCH_URL=http://elasticsearch:9200` in `.env` for canary events to be indexed)
- Honeypot: `ssh sysadmin@localhost -p 2222` (password `sysadmin`) and http://localhost:8088

Without `GEMINI_API_KEY` the generator and decoy-URL feature fall back to canned content.

## Kubernetes (Helm)

```bash
helm install dp deploy/helm/deception-platform \
  --set secrets.adminToken=$(openssl rand -hex 32) --set secrets.internalApiKey=$(openssl rand -hex 32) \
  --set secrets.databaseUrl='postgresql+psycopg://user:pass@db:5432/deception' \
  --set canary.baseUrl=https://files.example.com \
  --set ingress.dashboardHost=dashboard.example.com --set ingress.canaryHost=files.example.com
# demo cluster (kind/minikube): add --set dev.postgres.enabled=true --set dev.elk.enabled=true
```

The chart ships hardened pod specs, NetworkPolicies (the honeypot pod cannot reach anything but DNS, the API init call and Logstash), HPA/PDB for the listener, and an Ingress. See `docs/PRODUCTION_READINESS.md` before exposing it to the internet.

## Layout

```
services/api               FastAPI: tokens, alerts, event publishing        (tests: pytest)
services/canary-listener   public trap endpoint (/t/<id>, /p/<id>.png)      (tests: pytest)
services/generator         Gemini content + breadcrumb planting (init job)  (tests: pytest)
services/honeypot          sshd + nginx bait container (no secrets inside)
services/ui                Tripwire dashboard (React/Vite/Tailwind)
pipeline/                  filebeat, logstash, ES template/ILM, Kibana objects
deploy/helm/               Helm chart
docs/                      ARCHITECTURE, EVENT_SCHEMA, PRODUCTION_READINESS, legacy/ (v1.1 docs)
```

`make test` runs all unit tests; `make sync-chart` copies `pipeline/` configs into the chart (CI fails on drift).

## Safety

The honeypot has intentionally weak credentials and is *meant* to be compromised. Run it only on an isolated network/cluster, never alongside real workloads, and never put real data in the seed content. Only deploy on infrastructure you own or are authorised to monitor.

History: this repo absorbed [TripWire-Sentinel](https://github.com/aniketpitre/TripWire-Sentinel) (history preserved under `services/ui`).
