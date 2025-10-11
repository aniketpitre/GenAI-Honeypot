#!/bin/bash
set -euo pipefail

# v1.1 Orchestration Script: Generate AI files and bring up ELK + Honeypot via docker-compose

# Ensure API key is set
if [ -z "${GEMINI_API_KEY:-}" ]; then
  echo "Error: GEMINI_API_KEY environment variable not set."
  exit 1
fi

# Clean up stale files from v1.0 if present
rm -f nohup.out || true
mkdir -p generated_files
rm -rf generated_files/*

# Generate files using Gemini API
echo "[v1.1] Generating honeypot artifacts via Gemini..."
python3 generation_script.py --persona persona_config.json --output generated_files

# Determine docker-compose command (docker compose vs docker-compose)
DC="docker compose"
if ! docker compose version >/dev/null 2>&1; then
  if command -v docker-compose >/dev/null 2>&1; then
    DC="docker-compose"
  else
    echo "Error: docker compose or docker-compose not found. Please install Docker Compose."
    exit 1
  fi
fi

# Bring up the full stack
echo "[v1.1] Starting ELK stack and honeypot..."
$DC up -d --build

echo "[v1.1] Stack is up. Services: elasticsearch:9200, kibana:5601, logstash:12201/udp, honeypot:2223,80"

# Quick verification: check files inside the honeypot container
echo "[v1.1] Verifying files in honeypot container..."
docker exec honeypot-test ls -l /var/log/auth.log /home/sysadmin/.bash_history /home/sysadmin/todo.txt

echo "[v1.1] Upgrade complete. Access Kibana at http://localhost:5601"
