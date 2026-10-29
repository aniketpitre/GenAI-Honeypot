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
| Elasticsearch/Kibana: enable `xpack.security`, TLS, per-service credentials (currently disabled for dev) | ⬜ **required before production** |
| Secrets via External Secrets / Sealed Secrets / Vault (chart supports `secrets.existingSecret`) | 🟡 |
| Stronger honeypot isolation: gVisor/Kata `runtimeClass`, dedicated node pool/VPC, egress firewall | ⬜ |
| Image scanning (Trivy/Grype) + SBOM + signing (cosign) in CI; pin base images by digest | ⬜ |
| Dependency pinning with lockfiles for Python (pip-tools/uv) and Dependabot/Renovate | ⬜ |
| Login rate limiting / lockout on the admin API | ⬜ |

## 3. Reliability & scale
- ✅ Health/readiness probes, PDBs, HPA on the listener (stateless), `Recreate` single-replica honeypot.
- ✅ Listener forwards with retry and never blocks the response on the API.
- 🟡 Alerts can be lost if the API is down for >2 retries. ⬜ Add a durable queue (Redis stream / NATS / Kafka) between listener and API, or an on-disk spool.
- ⬜ Alembic migrations (tables are currently `create_all` on start-up).
- ⬜ Postgres HA/backups (use a managed DB); Elasticsearch multi-node or managed Elastic/OpenSearch; snapshots.
- ⬜ Multiple honeypot personas/replicas (web, DB, FTP) as separate Deployments via values.

## 4. Observability
- ⬜ Prometheus metrics (`/metrics`): hits/s, forward failures, alert latency, token counts; Grafana dashboards; alert on "listener→API failures".
- ⬜ Structured JSON application logs with request IDs; OpenTelemetry traces.
- ⬜ Self-monitoring canary: a synthetic token hit on a schedule to prove the whole path works end-to-end.

## 5. Detection quality (product improvements)
- ⬜ More token types: DNS tokens (needs authoritative NS), fake AWS keys (CloudTrail/`GetCallerIdentity` detection), fake DB creds, QR/PDF/XLSX, `.git` config and `.env` lures, Kubernetes service-account bait.
- ⬜ Dedup/grouping and severity scoring (same IP across tokens ⇒ one incident); suppress known scanners and your own security tools (allow-list, "false positive" learning).
- ⬜ MaxMind GeoLite2 + ASN/Tor/VPN/cloud-provider enrichment (supported via `GEOIP_DB_PATH`, DB not bundled — licence).
- ⬜ Email-client/AV pre-fetch detection (pixels fire from scanners; tag by UA/ASN to cut false positives).
- ⬜ Interactive honeypot: LLM-backed shell (e.g. Cowrie fork) so attackers can run commands, with strict output filtering and cost caps. Today the bait is static.
- ⬜ Notifications beyond one webhook: PagerDuty, email, MS Teams, per-token routing; SSE/WebSocket push to the UI instead of 5 s polling.
- ⬜ Export to SIEM (Splunk/Sentinel) and STIX/MISP for threat-intel sharing.

## 6. Delivery
- ✅ CI: unit tests (3 Python services), UI typecheck+build, compose/Helm lint + kubeconform schema check, image builds, chart/pipeline drift check; tag-triggered image publish to GHCR.
- ⬜ Integration test in CI: `docker compose up` + scripted canary hit → assert alert (and a kind-cluster install of the chart).
- ⬜ Playwright smoke test for the dashboard; typed API client generated from the OpenAPI schema.
- ⬜ Helm chart publishing (OCI) and a `values.production.yaml` example; Argo CD/Flux manifests.
- ⬜ Test the Logstash grok patterns with `logstash -t` / pipeline unit tests; confirm the Kibana saved-objects import on a real 8.14 instance (**unverified**).

## 7. Suggested order of work
1. **Before any internet exposure:** enable Elasticsearch security + TLS; real secret management; restrict dashboard ingress (VPN/IP allow-list); run the honeypot in its own isolated cluster/namespace with egress firewall.
2. Durable listener→API queue + metrics + self-test canary.
3. DNS/AWS-key tokens and dedup/enrichment (largest detection value).
4. Interactive LLM shell and SIEM export.
