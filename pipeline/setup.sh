#!/bin/sh
# One-shot: load ILM policy + index template into Elasticsearch, then import
# the Kibana data view / saved searches / dashboard. Idempotent.
set -eu
ES="${ELASTICSEARCH_URL:-http://elasticsearch:9200}"
KB="${KIBANA_URL:-http://kibana:5601}"

until curl -fsS "$ES/_cluster/health?wait_for_status=yellow&timeout=5s" >/dev/null; do echo "waiting for elasticsearch"; sleep 3; done
curl -fsS -X PUT "$ES/_ilm/policy/deception-events" -H 'Content-Type: application/json' --data-binary @/pipeline/elasticsearch/ilm-policy.json
curl -fsS -X PUT "$ES/_index_template/deception-events" -H 'Content-Type: application/json' --data-binary @/pipeline/elasticsearch/index-template.json
echo "elasticsearch configured"

until curl -fsS "$KB/api/status" >/dev/null; do echo "waiting for kibana"; sleep 5; done
curl -fsS -X POST "$KB/api/saved_objects/_import?overwrite=true" -H 'kbn-xsrf: true' --form file=@/pipeline/kibana/deception.ndjson
echo "kibana objects imported"
