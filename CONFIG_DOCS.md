# Configuration Files Documentation

This document provides line-by-line explanations of all configuration files in the GenAI-Honeypot project.

## Table of Contents
1. [Dockerfile](#dockerfile)
2. [docker-compose.yml](#docker-composeyml)
3. [entrypoint.sh](#entrypointsh)
4. [filebeat.yml](#filebeatyml)
5. [logstash.conf](#logstashconf)
6. [generation_script.py](#generation_scriptpy)
7. [persona_config.json](#persona_configjson)
8. [build_and_run.sh](#build_and_runsh)

---

## Dockerfile

**Purpose**: Defines how to build the honeypot container with all necessary components.

```dockerfile
# Use Ubuntu 22.04 as base - stable, well-documented, common target
FROM ubuntu:22.04

# Build argument to pass Gemini API key during build
ARG GEMINI_API_KEY
ENV GEMINI_API_KEY=${GEMINI_API_KEY}

# Install essential packages in single layer to minimize image size
RUN apt-get update && \
    apt-get install --no-install-recommends -y python3 python3-pip openssh-server nginx-full wget rsyslog && \
    mkdir -p /var/run/sshd /home/sysadmin /var/log && \
    useradd -m sysadmin && echo 'sysadmin:sysadmin' | chpasswd && \
    echo 'root:toor' | chpasswd && \
    echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config && \
    echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config && \
    echo 'AllowUsers sysadmin root admin' >> /etc/ssh/sshd_config && \
    echo 'SyslogFacility AUTH' >> /etc/ssh/sshd_config && \
    echo 'LogLevel VERBOSE' >> /etc/ssh/sshd_config && \
    echo 'UsePAM yes' >> /etc/ssh/sshd_config && \
    wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-8.14.0-amd64.deb && \
    dpkg -i filebeat-8.14.0-amd64.deb && \
    rm filebeat-8.14.0-amd64.deb
```

**Line-by-line explanation**:
- `FROM ubuntu:22.04`: Use Ubuntu 22.04 LTS as base image for stability and familiarity
- `ARG GEMINI_API_KEY`: Accept API key as build argument (secure way to pass secrets)
- `ENV GEMINI_API_KEY=${GEMINI_API_KEY}`: Set environment variable inside container
- `apt-get update`: Update package repository cache
- `python3 python3-pip`: Python runtime for AI generation scripts
- `openssh-server`: SSH daemon for honeypot interactions
- `nginx-full`: Web server with full module set
- `wget`: Download utility for Filebeat installation
- `rsyslog`: System logging daemon for proper log handling
- `mkdir -p /var/run/sshd`: Create SSH daemon runtime directory
- `useradd -m sysadmin`: Create sysadmin user with home directory
- `echo 'sysadmin:sysadmin'`: Set intentionally weak password
- `echo 'root:toor'`: Set weak root password (common honeypot pattern)
- `PermitRootLogin yes`: Allow direct root SSH access (normally disabled)
- `PasswordAuthentication yes`: Enable password auth (often disabled in production)
- `AllowUsers sysadmin root admin`: Limit SSH access to specific users
- `SyslogFacility AUTH`: Route SSH logs to auth facility for proper logging
- `LogLevel VERBOSE`: Maximum SSH logging for attack detection
- `UsePAM yes`: Enable PAM authentication for detailed logging
- `wget https://artifacts.elastic.co/.../filebeat-8.14.0-amd64.deb`: Download Filebeat package
- `dpkg -i filebeat-8.14.0-amd64.deb`: Install Filebeat for log shipping
- `rm filebeat-8.14.0-amd64.deb`: Clean up installation file

```dockerfile
# Copy Python dependencies and AI generation components
COPY requirements.txt /tmp/requirements.txt
COPY persona_config.json /tmp/persona_config.json
COPY generation_script.py /tmp/generation_script.py

# Copy Filebeat configuration and container startup script
COPY filebeat/filebeat.yml /etc/filebeat/filebeat.yml
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy AI-generated content to realistic locations
COPY generated_files/home/sysadmin/.bash_history /home/sysadmin/.bash_history
COPY generated_files/home/sysadmin/todo.txt /home/sysadmin/todo.txt
RUN chmod 644 /home/sysadmin/.bash_history /home/sysadmin/todo.txt

# Expose SSH and HTTP ports
EXPOSE 22 80

# Hide Docker-specific environment variables from processes
ENV DOCKER_HIDE=1

# Use custom entrypoint instead of default command
ENTRYPOINT ["/entrypoint.sh"]
```

**Second section explanation**:
- `COPY requirements.txt /tmp/`: Copy Python dependencies list
- `COPY persona_config.json /tmp/`: Copy AI generation configuration
- `COPY generation_script.py /tmp/`: Copy AI generation script
- `COPY filebeat/filebeat.yml /etc/filebeat/`: Install Filebeat configuration
- `COPY entrypoint.sh /entrypoint.sh`: Copy startup orchestration script
- `chmod +x /entrypoint.sh`: Make startup script executable
- `pip3 install --no-cache-dir`: Install Python dependencies without cache
- `COPY generated_files/home/sysadmin/.bash_history`: Copy fake command history
- `COPY generated_files/home/sysadmin/todo.txt`: Copy fake admin tasks
- `chmod 644`: Set readable permissions on user files
- `EXPOSE 22 80`: Document which ports the container uses
- `ENV DOCKER_HIDE=1`: Hide Docker metadata from attackers
- `ENTRYPOINT ["/entrypoint.sh"]`: Use custom startup script

---

## docker-compose.yml

**Purpose**: Orchestrates all services and defines their relationships.

```yaml
services:
  # Elasticsearch - Document database for log storage
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.14.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node          # Single-node cluster for development
      - xpack.security.enabled=false        # Disable security for easy access
      - ES_JAVA_OPTS=-Xms512m -Xmx512m     # Limit memory usage
    ports:
      - "9200:9200"                        # Expose REST API
    volumes:
      - esdata:/usr/share/elasticsearch/data # Persistent data storage
```

**Elasticsearch explanation**:
- `image: docker.elastic.co/elasticsearch/elasticsearch:8.14.0`: Official Elastic image
- `container_name: elasticsearch`: Fixed container name for internal DNS
- `discovery.type=single-node`: Skip cluster discovery for single instance
- `xpack.security.enabled=false`: Disable authentication/authorization for development
- `ES_JAVA_OPTS=-Xms512m -Xmx512m`: Set JVM heap size (adjust based on system RAM)
- `ports: "9200:9200"`: Map container port to host for external access
- `volumes: esdata:...`: Named volume for data persistence across restarts

```yaml
  # Logstash - Log processing pipeline
  logstash:
    image: docker.elastic.co/logstash/logstash:8.14.0
    container_name: logstash
    depends_on:
      - elasticsearch                       # Wait for ES to start first
    ports:
      - "5044:5044"                        # Beats input port
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline:ro  # Pipeline config
      - ./:/workspace:ro                   # Access to generated files
```

**Logstash explanation**:
- `depends_on: elasticsearch`: Ensures Elasticsearch starts before Logstash
- `ports: "5044:5044"`: Expose Beats input port for Filebeat connections
- `./logstash/pipeline:/usr/share/logstash/pipeline:ro`: Mount pipeline configuration as read-only
- `./:/workspace:ro`: Mount entire project directory for file input access

```yaml
  # Kibana - Visualization and dashboard interface
  kibana:
    image: docker.elastic.co/kibana/kibana:8.14.0
    container_name: kibana
    depends_on:
      - elasticsearch                       # Needs ES for data access
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200  # ES connection string
      - XPACK_SECURITY_ENABLED=false       # Match ES security settings
    ports:
      - "5601:5601"                        # Web interface port
```

**Kibana explanation**:
- `ELASTICSEARCH_HOSTS=http://elasticsearch:9200`: Use Docker internal DNS to connect to ES
- `XPACK_SECURITY_ENABLED=false`: Disable security to match Elasticsearch
- `ports: "5601:5601"`: Expose web interface for dashboard access

```yaml
  # GenAI Honeypot - Main honeypot container
  genai-honeypot:
    build: .                               # Build from local Dockerfile
    container_name: honeypot-test
    depends_on:
      - logstash                           # Ensure log pipeline is ready
    ports:
      - "2223:22"                          # SSH honeypot port
      - "80:80"                            # Web server port
    logging:
      driver: json-file                    # Use JSON log driver
      options:
        max-size: "10m"                    # Rotate logs at 10MB
        max-file: "3"                      # Keep 3 log files
```

**Honeypot explanation**:
- `build: .`: Build container from current directory's Dockerfile
- `depends_on: logstash`: Wait for log processing pipeline
- `ports: "2223:22"`: Map SSH port (avoid conflict with host SSH)
- `ports: "80:80"`: Map HTTP port directly
- `logging.driver: json-file`: Use structured logging
- `max-size: "10m"`: Prevent log files from growing too large
- `max-file: "3"`: Keep recent log history without filling disk

```yaml
# Named volumes for data persistence
volumes:
  esdata:
    driver: local                          # Use local storage driver
```

**Volumes explanation**:
- `esdata`: Named volume for Elasticsearch data persistence
- `driver: local`: Store data on local filesystem (default)

---

## entrypoint.sh

**Purpose**: Orchestrates container startup and ensures all services start correctly.

```bash
#!/bin/bash
# Honeypot Container Entrypoint Script
# Ensures robust startup of SSH, Nginx, Filebeat, and log file creation

set -e  # Exit on any error to prevent undefined behavior
```

**Script header**:
- `#!/bin/bash`: Use bash for advanced scripting features
- `set -e`: Exit immediately if any command fails (fail-fast behavior)

```bash
echo "[ENTRYPOINT] Starting honeypot container services..."

# Create necessary directories
mkdir -p /var/run/sshd /var/log /home/sysadmin
```

**Directory creation**:
- `mkdir -p`: Create directories and parent directories if they don't exist
- `/var/run/sshd`: Required for SSH daemon operation
- `/var/log`: System log directory
- `/home/sysadmin`: User home directory

```bash
# Create /var/log/auth.log with proper permissions for syslog/SSH logging
touch /var/log/auth.log
# rsyslog runs as user 'syslog' and group 'adm' on Ubuntu; grant write to owner only
chown syslog:adm /var/log/auth.log
chmod 640 /var/log/auth.log
```

**Log file setup**:
- `touch /var/log/auth.log`: Create authentication log file
- `chown syslog:adm`: Set correct ownership (syslog user, adm group)
- `chmod 640`: Set permissions (read/write for owner, read for group, none for others)

```bash
# Fix Filebeat config permissions
chmod 600 /etc/filebeat/filebeat.yml
```

**Filebeat security**:
- `chmod 600`: Filebeat requires strict permissions (read/write for owner only)

```bash
# Ensure SSH host keys exist
ssh-keygen -A
```

**SSH setup**:
- `ssh-keygen -A`: Generate all SSH host key types (RSA, ECDSA, ED25519)

```bash
# Start nginx
echo "[ENTRYPOINT] Starting nginx..."
service nginx start
```

**Web server startup**:
- `service nginx start`: Start nginx web server daemon

```bash
# Start syslog daemon for proper auth.log handling (try different options)
echo "[ENTRYPOINT] Starting syslog daemon..."
if command -v rsyslogd >/dev/null 2>&1; then
    rsyslogd
elif service rsyslog start >/dev/null 2>&1; then
    echo "[ENTRYPOINT] rsyslog service started"
elif service syslog-ng start >/dev/null 2>&1; then
    echo "[ENTRYPOINT] syslog-ng service started"
else
    echo "[ENTRYPOINT] Warning: No syslog daemon found, SSH may not log to auth.log"
fi
```

**Syslog startup with fallbacks**:
- `command -v rsyslogd`: Check if rsyslogd binary exists
- `rsyslogd`: Start rsyslog daemon directly
- `service rsyslog start`: Fallback to service management
- `service syslog-ng start`: Alternative syslog implementation
- Error handling: Warn if no syslog daemon available

```bash
# Start Filebeat in background
echo "[ENTRYPOINT] Starting Filebeat..."
filebeat -e -c /etc/filebeat/filebeat.yml &
FILEBEAT_PID=$!
```

**Filebeat startup**:
- `filebeat -e -c /etc/filebeat/filebeat.yml &`: Start in background with config
- `-e`: Log to stderr (visible in container logs)
- `-c`: Specify configuration file path
- `&`: Run in background
- `FILEBEAT_PID=$!`: Capture background process ID for cleanup

```bash
# Function to handle graceful shutdown
cleanup() {
    echo "[ENTRYPOINT] Shutting down services..."
    kill $FILEBEAT_PID 2>/dev/null || true
    service nginx stop 2>/dev/null || true
    service rsyslog stop 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT
```

**Cleanup handling**:
- `cleanup()`: Function to stop all services gracefully
- `kill $FILEBEAT_PID`: Stop Filebeat background process
- `service nginx stop`: Stop web server
- `service rsyslog stop`: Stop syslog daemon
- `|| true`: Ignore errors if services already stopped
- `trap cleanup SIGTERM SIGINT`: Run cleanup on container stop signals

```bash
# Start SSH daemon in foreground (main process)
echo "[ENTRYPOINT] Starting SSH daemon in foreground..."
exec /usr/sbin/sshd -D
```

**SSH daemon startup**:
- `exec /usr/sbin/sshd -D`: Replace shell with SSH daemon process
- `-D`: Run in foreground (required for Docker containers)
- `exec`: Replace current process (PID 1) for proper signal handling

---

## filebeat.yml

**Purpose**: Configures Filebeat to monitor log files and ship to Logstash.

```yaml
filebeat.inputs:
- type: log                    # Log file input type
  enabled: true               # Enable this input
  paths:
    - /var/log/auth.log       # Monitor SSH authentication log
```

**Input configuration**:
- `type: log`: Use log file input (reads file line by line)
- `enabled: true`: Activate this input configuration
- `paths: [/var/log/auth.log]`: Monitor SSH authentication log file

```yaml
output.logstash:
  hosts: ["logstash:5044"]    # Send to Logstash service on port 5044
```

**Output configuration**:
- `output.logstash`: Use Logstash output (instead of direct Elasticsearch)
- `hosts: ["logstash:5044"]`: Connect to Logstash container using Docker DNS

```yaml
logging:
  level: info                 # Log level for Filebeat itself
  to_files: true             # Write Filebeat logs to files
  files:
    path: /var/log/filebeat  # Filebeat log directory
    name: filebeat.log       # Log file name
    keepfiles: 7             # Retain 7 days of logs
    permissions: 0644        # Log file permissions
```

**Logging configuration**:
- `level: info`: Set log verbosity (debug, info, warning, error)
- `to_files: true`: Enable file logging (vs. console only)
- `path: /var/log/filebeat`: Directory for Filebeat's own logs
- `keepfiles: 7`: Automatic log rotation (keep 7 files)
- `permissions: 0644`: Make log files readable by group/others

---

## logstash.conf

**Purpose**: Defines how Logstash processes and routes log data.

```ruby
input {
  beats {
    port => 5044             # Listen for Filebeat connections
  }
  file {
    path => [               # Read static files for historical data
      "/workspace/host_auth.log",
      "/workspace/generated_files/var/log/auth.log",
      "/workspace/generated_files/var/log/alert.log",
      "/workspace/generated_files/var/log/stealth_alert.log",
      "/workspace/generated_files/home/sysadmin/.bash_history"
    ]
    start_position => "beginning"    # Read from start of file
    sincedb_path => "/usr/share/logstash/data/sincedb-honeypot"  # Track read position
    type => "honeypot-files"         # Tag for identification
    mode => "tail"                   # Monitor for new content
    codec => plain { charset => "UTF-8" }  # Text encoding
  }
}
```

**Input configuration**:
- `beats.port => 5044`: Listen for Filebeat connections on port 5044
- `file.path => [...]`: Array of files to monitor
- `start_position => "beginning"`: Read entire file on first run
- `sincedb_path`: Database file to track reading position
- `type => "honeypot-files"`: Add type field to distinguish sources
- `mode => "tail"`: Continue monitoring file for new lines
- `codec => plain`: Parse as plain text with UTF-8 encoding

```ruby
filter {
  mutate {
    add_field => { "source" => "%{[type]}" }  # Add source identification
  }
}
```

**Filter configuration**:
- `mutate`: Modify event fields
- `add_field`: Add new field to each event
- `"source" => "%{[type]}"`: Set source field to the type value

```ruby
output {
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]    # Elasticsearch cluster
    index => "honeypot-%{+YYYY.MM.dd}"       # Daily index pattern
  }
  stdout { codec => rubydebug }              # Debug output to console
}
```

**Output configuration**:
- `elasticsearch.hosts`: Array of Elasticsearch nodes
- `index => "honeypot-%{+YYYY.MM.dd}"`: Create daily indices (honeypot-2025.10.12)
- `stdout.codec => rubydebug`: Pretty-print events to console for debugging

---

## generation_script.py

**Purpose**: Generates realistic system files using Google Gemini AI.

```python
import os
import sys
import json
import argparse
from pathlib import Path
import google.generativeai as genai
```

**Imports**:
- `os, sys`: System interaction and environment variables
- `json`: Parse persona configuration
- `argparse`: Command-line argument parsing
- `pathlib.Path`: Modern file path handling
- `google.generativeai`: Google Gemini AI client

```python
def main():
    parser = argparse.ArgumentParser(description="Generative AI Honeypot File Creator")
    parser.add_argument('--persona', required=True, help='Path to persona_config.json')
    parser.add_argument('--output', required=True, help='Root directory to write generated files')
    args = parser.parse_args()
```

**Argument parsing**:
- `ArgumentParser`: Handle command-line arguments
- `--persona`: Path to configuration file (required)
- `--output`: Output directory for generated files (required)

```python
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        sys.exit(1)
    genai.configure(api_key=api_key)
```

**API setup**:
- `os.environ.get('GEMINI_API_KEY')`: Read API key from environment
- Error handling: Exit if API key not provided
- `genai.configure(api_key=api_key)`: Initialize Gemini client

```python
    import random
    import datetime
    with open(args.persona, 'r') as f:
        config = json.load(f)

    files = config.get('files', [])
    if not files:
        print("No files specified in persona config.")
        sys.exit(1)

    model = genai.GenerativeModel('models/gemini-2.0-flash')
```

**Configuration loading**:
- Import additional modules for randomization
- Load persona configuration from JSON file
- Extract files array from configuration
- Error handling: Exit if no files specified
- Initialize Gemini model (gemini-2.0-flash for fast generation)

```python
    # Add randomness/timestamp to each prompt for uniqueness
    run_id = f"RunID:{random.randint(100000,999999)} Date:{datetime.datetime.now().isoformat()}"
    for file_obj in files:
        rel_path = file_obj['path']
        prompt = file_obj['prompt'] + f"\n{run_id}"
        # Write to /generated_files instead of system locations
        out_path = Path(args.output) / rel_path.lstrip('/')
        gen_root = Path(args.output)
        if str(gen_root) == '/':
            gen_root = Path('/generated_files')
            out_path = gen_root / rel_path.lstrip('/')
```

**File generation loop**:
- `run_id`: Add unique identifier to prevent identical outputs
- `random.randint(100000,999999)`: Generate random run ID
- `datetime.now().isoformat()`: Add timestamp
- `file_obj['path']`: Get target file path from configuration
- `prompt + f"\n{run_id}"`: Append run ID to prompt for uniqueness
- `Path(args.output) / rel_path.lstrip('/')`: Build output path safely
- Path security: Remove leading slash to prevent absolute path injection

```python
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"[GEN] Generating {rel_path} -> {out_path}")
            print(f"[GEN] Prompt: {prompt}")
            response = model.generate_content(prompt)
            print(f"[GEN] API Response: {response}")
            content = response.text if hasattr(response, 'text') else str(response)
            with open(out_path, 'w') as outf:
                outf.write(content)
            print(f"[GEN] Written: {out_path}")
            if out_path.exists():
                print(f"[GEN] File exists: {out_path}")
            else:
                print(f"[ERROR] File {out_path} was NOT created!")
        except Exception as e:
            print(f"[ERROR] Exception generating {rel_path}: {e}")
```

**File generation process**:
- `out_path.parent.mkdir(parents=True, exist_ok=True)`: Create parent directories
- Detailed logging for debugging generation process
- `model.generate_content(prompt)`: Call Gemini AI with prompt
- `response.text`: Extract generated content from API response
- Error handling: Graceful failure if generation fails
- File verification: Confirm file was created successfully

---

## persona_config.json

**Purpose**: Configuration for AI content generation defining what files to create.

```json
{
  "persona": "Debian Web Server",
  "files": [
    {
      "path": "/var/log/auth.log",
      "prompt": "Generate a realistic Debian /var/log/auth.log file for a web server in October 2025. Include several successful admin logins and numerous failed brute-force SSH attempts from various IPs. Use authentic log formats and plausible timestamps."
    },
    {
      "path": "/home/sysadmin/.bash_history",
      "prompt": "Generate a plausible .bash_history for a sysadmin on a Debian web server. Include package management, user management, log inspection, and web server maintenance commands. Use realistic command sequences and occasional mistakes."
    },
    {
      "path": "/home/sysadmin/todo.txt",
      "prompt": "Generate a plausible to-do list for a sysadmin managing a Debian web server. Include tasks related to security, updates, backups, and web server configuration. Use a casual, realistic style."
    }
  ]
}
```

**Configuration structure**:
- `persona`: Overall character/role for the honeypot
- `files`: Array of files to generate
- `path`: Target file location (will be adjusted for container)
- `prompt`: Detailed instruction for AI content generation

**Prompt design principles**:
- **Specific context**: "Debian web server in October 2025"
- **Realistic details**: "Include several successful admin logins"
- **Authentic format**: "Use authentic log formats"
- **Behavioral patterns**: "Include occasional mistakes"
- **Temporal relevance**: "plausible timestamps"

---

## build_and_run.sh

**Purpose**: Main deployment script that orchestrates the entire setup process.

```bash
#!/bin/bash
set -euo pipefail  # Strict error handling

# v1.1 Orchestration Script: Generate AI files and bring up ELK + Honeypot via docker-compose
```

**Script header**:
- `set -euo pipefail`: Strict bash mode (exit on error, undefined variables, pipe failures)

```bash
# Ensure API key is set
if [ -z "${GEMINI_API_KEY:-}" ]; then
  echo "Error: GEMINI_API_KEY environment variable not set."
  exit 1
fi
```

**Prerequisites check**:
- `[ -z "${GEMINI_API_KEY:-}" ]`: Check if API key is empty or unset
- `:-`: Bash parameter expansion with default empty value
- Exit with error code 1 if API key missing

```bash
# Clean up stale files from v1.0 if present
rm -f nohup.out || true
mkdir -p generated_files
rm -rf generated_files/*
```

**Cleanup**:
- `rm -f nohup.out`: Remove old background process output
- `|| true`: Ignore error if file doesn't exist
- `mkdir -p generated_files`: Create output directory
- `rm -rf generated_files/*`: Clear any existing generated content

```bash
# Generate files using Gemini API
echo "[v1.1] Generating honeypot artifacts via Gemini..."
python3 generation_script.py --persona persona_config.json --output generated_files
```

**AI generation**:
- Progress indicator with version tag
- Call generation script with persona configuration
- Output to generated_files directory

```bash
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
```

**Docker Compose detection**:
- Modern Docker includes `docker compose` command
- Older installations use separate `docker-compose` binary
- Test for modern command first
- Fallback to legacy command
- Error if neither available

```bash
# Bring up the full stack
echo "[v1.1] Starting ELK stack and honeypot..."
$DC up -d --build
```

**Stack deployment**:
- Use detected Docker Compose command
- `up -d`: Start in detached mode (background)
- `--build`: Rebuild images if needed

```bash
echo "[v1.1] Stack is up. Services: elasticsearch:9200, kibana:5601, logstash:12201/udp, honeypot:2223,80"

# Quick verification: check files inside the honeypot container
echo "[v1.1] Verifying files in honeypot container..."
docker exec honeypot-test ls -l /var/log/auth.log /home/sysadmin/.bash_history /home/sysadmin/todo.txt

echo "[v1.1] Upgrade complete. Access Kibana at http://localhost:5601"
```

**Verification and completion**:
- List all exposed service ports
- Verify generated files exist inside container
- Provide access URL for Kibana dashboard

This comprehensive configuration documentation provides the foundation for understanding, maintaining, and extending the GenAI-Honeypot system.