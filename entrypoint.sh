#!/bin/bash

# Honeypot Container Entrypoint Script
# Ensures robust startup of SSH, Nginx, Filebeat, and log file creation

set -e

echo "[ENTRYPOINT] Starting honeypot container services..."

# Create necessary directories
mkdir -p /var/run/sshd /var/log /home/sysadmin

# Create /var/log/auth.log with proper permissions for SSH logging
touch /var/log/auth.log
chmod 644 /var/log/auth.log
chown root:root /var/log/auth.log

# Fix Filebeat config permissions
chmod 600 /etc/filebeat/filebeat.yml

# Ensure SSH host keys exist
ssh-keygen -A

# Start nginx
echo "[ENTRYPOINT] Starting nginx..."
service nginx start

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

# Start Filebeat in background
echo "[ENTRYPOINT] Starting Filebeat..."
filebeat -e -c /etc/filebeat/filebeat.yml &
FILEBEAT_PID=$!

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

# Start SSH daemon in foreground (main process)
echo "[ENTRYPOINT] Starting SSH daemon in foreground..."
exec /usr/sbin/sshd -D -e