#!/bin/bash
set -e

# Ensure API key is set
if [ -z "$GEMINI_API_KEY" ]; then
  echo "Error: GEMINI_API_KEY environment variable not set."
  exit 1
fi

# Step 1: Generate files using Gemini API
python3 generation_script.py --persona persona_config.json --output generated_files

# Step 2: Build Docker image
DOCKER_IMAGE=genai-honeypot
docker build -t $DOCKER_IMAGE .

# Step 3: Remove previous container if exists
CONTAINER_NAME=honeypot-test
docker rm -f $CONTAINER_NAME 2>/dev/null || true

# Step 4: Run new container
PORT=2223
docker run -d -p $PORT:22 --name $CONTAINER_NAME $DOCKER_IMAGE

# Step 5: Verify files in container
docker exec $CONTAINER_NAME ls -l /var/log/auth.log /home/sysadmin/.bash_history /home/sysadmin/todo.txt

echo "Honeypot system is built, running, and verified!"
