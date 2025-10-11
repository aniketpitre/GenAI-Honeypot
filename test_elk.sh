#!/bin/bash
# Generate some sample logs directly into Elasticsearch to verify the stack works

echo "Sending test log to Elasticsearch..."

curl -X POST "localhost:9200/honeypot-$(date +%Y.%m.%d)/_doc" \
  -H 'Content-Type: application/json' \
  -d '{
    "@timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'",
    "level": "INFO",
    "message": "Test honeypot log entry",
    "container": {
      "name": "honeypot-test",
      "id": "test-123"
    },
    "source": "test-script"
  }'

echo -e "\nTest log sent. Check indices with: curl http://localhost:9200/_cat/indices?v"