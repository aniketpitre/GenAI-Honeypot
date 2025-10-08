#!/usr/bin/env python3
import time
from pathlib import Path
import re

# Paths to monitor
auth_log = Path('generated_files/var/log/auth.log')
bash_history = Path('generated_files/home/sysadmin/.bash_history')
alert_log = Path('generated_files/var/log/stealth_alert.log')

# Suspicious patterns to watch for
patterns = [
    r'Failed password', r'Accepted password for root', r'cat /etc/shadow', r'rm -rf /',
    r'wget http://', r'nc -lvp', r'useradd', r'python3 -m http.server', r'chmod 777 /root'
]

def scan_file(file_path, last_pos, patterns):
    with open(file_path, 'r') as f:
        f.seek(last_pos)
        lines = f.readlines()
        new_pos = f.tell()
    alerts = []
    for line in lines:
        for pat in patterns:
            if re.search(pat, line):
                alerts.append(line.strip())
    return alerts, new_pos

def main():
    print("[STEALTH] Starting stealth monitor...")
    last_auth_pos = 0
    last_bash_pos = 0
    while True:
        # Monitor auth.log
        if auth_log.exists():
            alerts, last_auth_pos = scan_file(auth_log, last_auth_pos, patterns)
            for alert in alerts:
                with open(alert_log, 'a') as af:
                    af.write(f"[AUTH ALERT] {alert}\n")
        # Monitor .bash_history
        if bash_history.exists():
            alerts, last_bash_pos = scan_file(bash_history, last_bash_pos, patterns)
            for alert in alerts:
                with open(alert_log, 'a') as af:
                    af.write(f"[BASH ALERT] {alert}\n")
        time.sleep(30)

if __name__ == "__main__":
    main()
