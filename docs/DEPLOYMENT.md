# Production deployment guide (Kubernetes)

Verified here: chart lint + Kubernetes schema validation, unit/e2e tests. **Not** verified here (no cluster/Docker available when written): image builds, a live install, Elasticsearch security bootstrap, Prometheus/Grafana objects. Do a staging install first.

## 0. Prerequisites
- Kubernetes ≥ 1.27, an Ingress controller (examples use ingress-nginx), cert-manager, a CNI that **enforces NetworkPolicy** (Calico/Cilium), optionally External Secrets Operator and prometheus-operator.
- A **managed PostgreSQL** (TLS, backups) and a **managed Elasticsearch/OpenSearch** (TLS + auth), or your own.
- Two DNS names: `dashboard.<domain>` (restricted) and `files.<domain>` (public; embedded in every token — choose something unremarkable and keep it for the life of the tokens).
- A separate, isolated **node pool/VPC** for the honeypot (and ideally a gVisor/Kata RuntimeClass).

## 1. Build and publish images
Tag `vX.Y.Z` → `.github/workflows/release.yml` builds the five images, attaches SBOM + provenance, pushes to GHCR and signs them with cosign (keyless). Enforce signatures at admission (Kyverno/Connaisseur) if you can.

## 2. Secrets
Preferred: External Secrets Operator (`externalSecrets.enabled=true`, see `values.production.yaml`). Required keys: `ADMIN_TOKEN`, `INTERNAL_API_KEY` (each ≥ 24 chars: `openssl rand -hex 32`), `DATABASE_URL` (`postgresql+psycopg://…?sslmode=require`). Optional: `ELASTICSEARCH_USER`/`ELASTICSEARCH_PASSWORD` (or `ELASTICSEARCH_API_KEY`), `WEBHOOK_URL`, `GEMINI_API_KEY`.
Create the Elasticsearch writer with the least privilege used in `pipeline/setup.sh` (`deception_writer`: `create_index, create, index, auto_configure` on `deception-events-*`).

## 3. Install
```bash
helm upgrade --install dp deploy/helm/deception-platform -n deception --create-namespace \
  -f deploy/helm/deception-platform/values.production.yaml
```
The API applies database migrations on start-up (Postgres advisory lock → safe with replicas).

## 4. Network exposure
- `files.<domain>` routes only `/t/`, `/p/`, `/aws/`, `/k8s/` to the listener. `/metrics`, `/internal`, `/api` are not reachable through it.
- Restrict `dashboard.<domain>` to VPN/office ranges (ingress allow-list/WAF) and put SSO in front if available.
- Expose the honeypot Service (`LoadBalancer`) on its own IP/node pool; the pod's NetworkPolicy only allows DNS, the API (init job) and Logstash out. Add a cloud/VPC egress firewall as a second layer.
- If your ingress adds more/fewer proxies than the defaults, set `listener.trustedProxyCount` / `api.trustedProxyCount` so client IPs (and login lock-outs) are attributed correctly.

## 5. Verify
1. Dashboard login works; create a URL token, `curl` it from outside → alert appears within ~5 s.
2. Create a kubeconfig token, run `kubectl --kubeconfig <file> get pods` → alert.
3. Stop the API (`kubectl scale deploy/dp-deception-platform-api --replicas=0`), hit a token, scale back → alert arrives; `canary_spool_size` returned to 0.
4. `ssh` the honeypot with a wrong password → event in Kibana "SSH failed logins".
5. Trigger `CanaryHitsBacklogged` by step 3 held > 5 min → alert fires.
