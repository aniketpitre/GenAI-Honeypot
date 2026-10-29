#!/bin/sh
# One-shot, idempotent: create the least-privilege writer user, set the Kibana
# service-account password, load ILM policy + index template, import Kibana objects.
# Required env: ELASTIC_PASSWORD, ES_WRITER_PASSWORD, KIBANA_PASSWORD
set -eu
ES="${ELASTICSEARCH_URL:-http://elasticsearch:9200}"
KB="${KIBANA_URL:-http://kibana:5601}"
: "${ELASTIC_PASSWORD:?ELASTIC_PASSWORD required}" "${ES_WRITER_PASSWORD:?ES_WRITER_PASSWORD required}" "${KIBANA_PASSWORD:?KIBANA_PASSWORD required}"
AUTH="elastic:${ELASTIC_PASSWORD}"
J='Content-Type: application/json'

# Elasticsearch answers 503 for the security APIs until its .security index is ready, which can be
# well after the cluster reports "yellow", so every call is retried. (Arguments are not echoed:
# they contain credentials.)
req() {
    n=0
    until curl -fsS "$@"; do
        n=$((n + 1))
        if [ "$n" -ge 60 ]; then echo "request failed after $n attempts" >&2; return 1; fi
        echo "not ready yet, retrying ($n)..." >&2
        sleep 3
    done
    echo
}

req -u "$AUTH" "$ES/_cluster/health?wait_for_status=yellow&timeout=5s" >/dev/null

req -u "$AUTH" -X PUT "$ES/_security/role/deception_writer" -H "$J" -d \
  '{"cluster":["monitor"],"indices":[{"names":["deception-events-*"],"privileges":["create_index","create","index","auto_configure"]}]}'
req -u "$AUTH" -X PUT "$ES/_security/user/deception_writer" -H "$J" -d \
  "{\"password\":\"${ES_WRITER_PASSWORD}\",\"roles\":[\"deception_writer\"]}"
req -u "$AUTH" -X POST "$ES/_security/user/kibana_system/_password" -H "$J" -d \
  "{\"password\":\"${KIBANA_PASSWORD}\"}"
req -u "$AUTH" -X PUT "$ES/_ilm/policy/deception-events" -H "$J" --data-binary @/pipeline/elasticsearch/ilm-policy.json
req -u "$AUTH" -X PUT "$ES/_index_template/deception-events" -H "$J" --data-binary @/pipeline/elasticsearch/index-template.json
echo "elasticsearch configured"

req -u "$AUTH" "$KB/api/status" >/dev/null
req -u "$AUTH" -X POST "$KB/api/saved_objects/_import?overwrite=true" -H 'kbn-xsrf: true' --form file=@/pipeline/kibana/deception.ndjson
echo "kibana objects imported"
