# Operations runbook

| Task | How |
|---|---|
| Rotate `ADMIN_TOKEN` | Update the secret in your manager; ESO syncs; `kubectl rollout restart deploy/<release>-api`. Sessions are per-browser tab; users sign in again. |
| Rotate `INTERNAL_API_KEY` | Change it, restart **api and listener together**. Hits arriving in between are spooled (not lost) and delivered after. |
| Upgrade | `helm upgrade` with the new tag. Migrations run automatically; roll back with `helm rollback` (migrations are additive — add a down-migration before any destructive change). |
| Backup/restore | Postgres: managed snapshots + PITR (tokens and alerts live there). Elasticsearch: snapshot repository + SLM; events are re-creatable only from backups. Tokens already planted in the wild stay valid as long as the Postgres rows and `files.<domain>` exist. |
| Disable a noisy/compromised token | Dashboard → Token Manager → toggle status (hits are then dropped silently). |
| Alert `CanaryHitsBacklogged` | API down, DB down, or key mismatch. `kubectl logs deploy/<rel>-listener` shows "API refused our key" or "API unreachable". Spooled hits deliver automatically once fixed (spool is in the pod `emptyDir`: don't delete listener pods while backlogged). |
| Alert `CanaryHitsDropped` | Spool full/unavailable and API down: hits were lost. Restore the API, then review web-server/ingress access logs for `/t/ /p/ /aws/ /k8s/` in that window. |
| Alert `EventPublishFailing` | Elasticsearch/webhook unreachable; alerts are still in Postgres and the dashboard, only SIEM/Slack delivery is affected. |
| Admin locked out (429) | 10 failed attempts per client IP per 5 min. Wait, or restart the API pods to clear the in-memory counters. |
| Honeypot compromised | Treat as expected. Capture logs from Kibana, then `kubectl delete pod` (the init job regenerates bait; breadcrumb tokens are re-used via `external_key`). Rebuild the node if you suspect escape. |
| Add a breadcrumb | Add an entry to `services/generator/persona_config.json` (`external_key` must be unique and stable), redeploy the generator image, restart the honeypot pod. |
