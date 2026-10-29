#!/bin/bash
# Honeypot entrypoint: seed fake content, set (intentionally weak) credentials,
# start syslog + nginx, run sshd in the foreground.
set -euo pipefail

SEED_DIR="${SEED_DIR:-/seed}"
# user:password pairs, comma separated. Weak on purpose - this is the bait.
HONEYPOT_USERS="${HONEYPOT_USERS:-sysadmin:sysadmin,root:toor}"

mkdir -p /var/run/sshd /var/log/honeypot
touch /var/log/honeypot/auth.log /var/log/honeypot/nginx-access.log /var/log/honeypot/nginx-error.log
chmod 644 /var/log/honeypot/*.log

if [ -d "$SEED_DIR" ]; then
    echo "[honeypot] seeding filesystem from $SEED_DIR"
    cp -a "$SEED_DIR"/. /
    chown -R sysadmin:sysadmin /home/sysadmin 2>/dev/null || true
fi
touch /var/log/auth.log

IFS=',' read -ra PAIRS <<< "$HONEYPOT_USERS"
for pair in "${PAIRS[@]}"; do
    echo "$pair" | chpasswd
done

ssh-keygen -A
rsyslogd
nginx

cleanup() { pkill nginx || true; pkill rsyslogd || true; }
trap cleanup SIGTERM SIGINT

echo "[honeypot] ready"
exec /usr/sbin/sshd -D -e
