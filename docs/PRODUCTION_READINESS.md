# Production readiness & improvement plan

Legend: ✅ done in this change · 🟡 partial · ⬜ todo. "Unverified" = written but not run in the authoring environment (no Docker daemon / cluster available there) — verify on first deploy.

## 1. Fixed while merging the two repos
- ✅ `GEMINI_API_KEY` was baked into the honeypot image (`ARG`/`ENV`) and into the TripWire browser bundle (Vite `define`). Now only the server-side generator/API see it, at runtime.
- ✅ TripWire was a `localStorage` mock (random IPs, simulated alerts). Now a real API + listener capture the true IP/headers.
- ✅ Build no longer depends on an uncommitted `generated_files/` directory; content is produced at start-up into a volume.
- ✅ Filebeat moved out of the honeypot image into a sidecar; the honeypot carries no shipper or credentials to the backend.
- ✅ Tailwind CDN + third-party importmap removed from the UI; assets are built and self-hosted.
- ✅ Fake `auth.log` is no longer ingested as if it were real telemetry.

## 2. Security hardening
| Item | Status |
|---|---|
| Admin auth on API (bearer, constant-time compare), separate internal key for the listener | ✅ |
| Containers: non-root (except sshd), `cap_drop: ALL`, read-only rootfs, `no-new-privileges`, seccomp RuntimeDefault, resource limits | ✅ (honeypot needs root + a few caps for sshd) |
| NetworkPolicies: honeypot egress limited to DNS/API/Logstash; API ingress restricted | ✅ (needs a CNI that enforces policies) |
| No service-account token mounted in honeypot pod | ✅ |
| Listener: IP spoof-resistant XFF handling, per-IP rate limit, sensitive headers stripped, uniform responses | ✅ |
| Replace single shared admin token with real SSO/OIDC + per-user audit trail | ⬜ |
| Elasticsearch security on in compose and the chart's dev ELK; least-privilege `deception_writer` for API/Logstash; `kibana_system` service account; API supports basic auth/API key + custom CA | ✅ (bootstrap in `pipeline/setup.sh` not run against a live cluster). ⬜ In-cluster TLS between Filebeat/Logstash/ES — use managed ES with TLS for production |
| Secrets via External Secrets Operator (`externalSecrets.*`) or `existingSecret`; production values example | ✅ |
| Honeypot `runtimeClassName`, nodeSelector/tolerations for a dedicated pool; `deploy/isolation/` (gVisor RuntimeClass, Pod Security namespace, default-deny, Cilium egress, GKE/EKS Terraform for pool + egress firewall) | ✅ files (Kubernetes YAML schema-validated, Terraform parses; **Terraform not applied**). ⬜ Provisioning the real pool/VPC is environment-specific |
| Trivy image scan (fails on CRITICAL), Trivy config scan, pip-audit, npm audit (`security.yml`); SBOM + provenance + keyless cosign on release | ✅ (workflows not yet run on GitHub). ⬜ Pin base images by digest (Dependabot can then bump them); enforce signatures at admission |
| Dependabot for pip/npm/docker/actions | ✅ |
| Hash-pinned lockfiles for api, canary-listener and generator (`requirements.in` → pip-compile **inside python:3.12** → `requirements.txt`, installed with `--require-hashes`; images built from them) | ✅ |
| Admin/internal secrets must be ≥ 24 chars (API refuses to start otherwise) | ✅ |
| Admin login lock-out per client IP (10 fails / 5 min, 429), IP taken from `X-Forwarded-For` per `trustedProxyCount` | ✅ |

## 3. Reliability & scale
- ✅ Health/readiness probes, PDBs, HPA on the listener (stateless), `Recreate` single-replica honeypot.
- ✅ Listener forwards with retry and never blocks the response on the API.
- ✅ Listener spools hits to disk when the API is down (or refuses its key) and retries every 5 s, in order; the API de-duplicates redeliveries via `hit_id`. Covered by `tests/e2e`. 🟡 The spool lives in the pod's `emptyDir`: it survives container restarts but not pod rescheduling — use a PVC or a broker (Redis/NATS) for stronger guarantees.
- ✅ Alembic migrations run at API start-up under a Postgres advisory lock (safe with several replicas).
- ⬜ Postgres HA/backups (use a managed DB); Elasticsearch multi-node or managed Elastic/OpenSearch; snapshots.
- ⬜ Multiple honeypot personas/replicas (web, DB, FTP) as separate Deployments via values.

## 4. Observability
- ✅ Prometheus `/metrics` on API and listener (`deception_hits_total`, `canary_hits_total{outcome}`, `canary_spool_size`, event publish failures) with scrape annotations in the chart. ✅ Optional PrometheusRule (spool backlog, dropped hits, event-publish failures) and Grafana dashboard ConfigMap in the chart (`monitoring.*`; rules/dashboard not run against a live Prometheus/Grafana).
- ⬜ Structured JSON application logs with request IDs; OpenTelemetry traces.
- ⬜ Self-monitoring canary: a synthetic token hit on a schedule to prove the whole path works end-to-end.

## 5. Detection quality (product improvements)
- ✅ Fake AWS credentials file (via `endpoint_url`) and fake kubeconfig tokens. ⬜ DNS tokens (needs authoritative NS), real-AWS-account decoy keys detected via CloudTrail, fake DB creds, QR/PDF/XLSX, `.git`/`.env` lures.
- 🟡 `/api/v1/stats` + dashboard summary highlight IPs that hit several different tokens. ⬜ Full incident grouping/severity scoring; suppress known scanners and your own security tools (allow-list).
- ⬜ MaxMind GeoLite2 + ASN/Tor/VPN/cloud-provider enrichment (supported via `GEOIP_DB_PATH`, DB not bundled — licence).
- ⬜ Email-client/AV pre-fetch detection (pixels fire from scanners; tag by UA/ASN to cut false positives).
- ⬜ Interactive honeypot: LLM-backed shell (e.g. Cowrie fork) so attackers can run commands, with strict output filtering and cost caps. Today the bait is static.
- ✅ Live dashboard updates over server-sent events (`/api/v1/stream`), fanned out across API replicas with Postgres LISTEN/NOTIFY (30 s polling kept as a safety net). ⬜ Notifications beyond one webhook: PagerDuty, email, MS Teams, per-token routing.
- ⬜ Export to SIEM (Splunk/Sentinel) and STIX/MISP for threat-intel sharing.

## 6. Delivery
- ✅ CI: unit tests (3 Python services), UI typecheck+build, compose/Helm lint + kubeconform schema check, image builds, chart/pipeline drift check; tag-triggered image publish to GHCR.
- ✅ `tests/e2e/run_e2e.py` (CI job `e2e`): real processes, generator breadcrumb → trap hit → alert, plus API-outage spool recovery. ⬜ Same flow against `docker compose up`, and a kind-cluster install of the chart.
- 🟡 Browser smoke script `tests/e2e/ui_smoke.cjs` (manual; not in CI yet) caught a real UI bug (alert cards invisible). ⬜ Run it in CI; typed API client generated from the OpenAPI schema.
- ⬜ Helm chart publishing (OCI) and a `values.production.yaml` example; Argo CD/Flux manifests.
- ⬜ Test the Logstash grok patterns with `logstash -t` / pipeline unit tests; confirm the Kibana saved-objects import on a real 8.14 instance (**unverified**).

## 6b. Docs
- ✅ `docs/DEPLOYMENT.md` (production install + verification checklist), `docs/RUNBOOK.md` (rotation, upgrades, backups, alert playbooks).

## 6c. What was verified on real containers (Docker daemon available in the later authoring session)
Images for api, canary-listener, generator, honeypot and ui build from the hash-locked requirements; the honeypot accepts SSH logins and logs them; the real Logstash 8.14 container parses the honeypot's actual auth/nginx lines; the Elasticsearch security bootstrap and Kibana saved-object import run to completion; the UI container serves with the security headers and proxies `/api`. This found and fixed: API image missing `migrations/`, sshd `-e` bypassing syslog, non-traditional rsyslog timestamps, UI read-only-fs start-up, setup job not retrying ES 503s, and a 3.13-compiled lockfile that broke the 3.12 image.
The full-stack smoke test (`tests/e2e/compose_smoke.py`) then **passed 12/12** on the running compose stack with real Postgres, Elasticsearch 8.14 (security on), Kibana, Logstash and Filebeat: breadcrumbs planted in the honeypot, trap hit → alert in Postgres → SSE push (Postgres LISTEN/NOTIFY) → event indexed by the least-privilege writer, SSH attack → Filebeat → Logstash → Elasticsearch (failed/successful/invalid-user distinguished), Kibana dashboard present. In a real browser a new alert card appeared 228 ms after the hit (poll interval 30 s). CI job `compose-smoke` repeats this with the official Elastic images.
**Still unverified:** the `tests/prometheus` rule tests (the Prometheus image/promtool could not be obtained in the authoring sandbox), the GitHub Actions workflows (none has run yet), `terraform apply` of the isolation examples, and an install of the Helm chart on a real Kubernetes cluster (a kind cluster could not start in the authoring sandbox: nested runc failure). Chart lint, schema and CRD validation did pass.

## 7. Suggested order of work
1. **Before any internet exposure:** enable Elasticsearch security + TLS; real secret management; restrict dashboard ingress (VPN/IP allow-list); run the honeypot in its own isolated cluster/namespace with egress firewall.
2. Durable listener→API queue + metrics + self-test canary.
3. DNS/AWS-key tokens and dedup/enrichment (largest detection value).
4. Interactive LLM shell and SIEM export.
