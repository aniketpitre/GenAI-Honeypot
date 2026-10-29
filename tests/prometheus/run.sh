#!/bin/bash
# Render the chart's alert rules and unit-test them with promtool (needs helm, docker, python3+pyyaml).
set -euo pipefail
cd "$(dirname "$0")/../.."
tmp=$(mktemp -d)
helm template t deploy/helm/deception-platform --set secrets.adminToken=a,secrets.internalApiKey=b,secrets.databaseUrl=x,monitoring.prometheusRule.enabled=true > "$tmp/render.yaml"
python3 - "$tmp" <<'PY'
import sys, yaml
tmp = sys.argv[1]
rule = next(d for d in yaml.safe_load_all(open(f"{tmp}/render.yaml")) if d and d.get("kind") == "PrometheusRule")
yaml.safe_dump({"groups": rule["spec"]["groups"]}, open(f"{tmp}/rules.yml", "w"))
PY
cp tests/prometheus/rules_test.yml "$tmp/"
docker run --rm -v "$tmp:/t" -w /t --entrypoint promtool prom/prometheus:v2.55.1 check rules rules.yml
docker run --rm -v "$tmp:/t" -w /t --entrypoint promtool prom/prometheus:v2.55.1 test rules rules_test.yml
