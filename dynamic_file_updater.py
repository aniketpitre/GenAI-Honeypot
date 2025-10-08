#!/usr/bin/env python3
import time
import random
from datetime import datetime
from pathlib import Path

# Paths to files to update
auth_log = Path('generated_files/var/log/auth.log')
bash_history = Path('generated_files/home/sysadmin/.bash_history')

# Sample log entries and commands
ssh_fail_ips = [
    '185.234.219.10', '91.200.12.45', '203.0.113.77', '178.62.1.23', '45.76.89.101'
]
admin_users = ['sysadmin', 'root']

bash_commands = [
    'sudo apt update', 'sudo apt upgrade', 'tail -f /var/log/auth.log',
    'grep "Failed password" /var/log/auth.log', 'sudo systemctl restart nginx',
    'sudo nano /etc/nginx/sites-available/default', 'df -h', 'free -m', 'exit'
]

def append_auth_log():
    now = datetime.now().strftime('%b %d %H:%M:%S')
    if random.random() < 0.7:
        # Failed SSH attempt
        ip = random.choice(ssh_fail_ips)
        entry = f"{now} debian sshd[12345]: Failed password for invalid user admin from {ip} port {random.randint(1000,65000)} ssh2\n"
    else:
        # Successful admin login
        user = random.choice(admin_users)
        entry = f"{now} debian sshd[12345]: Accepted password for {user} from 127.0.0.1 port {random.randint(1000,65000)} ssh2\n"
    with open(auth_log, 'a') as f:
        f.write(entry)

def append_bash_history():
    cmd = random.choice(bash_commands)
    with open(bash_history, 'a') as f:
        f.write(cmd + '\n')

def main():
    print("[DYNAMIC] Starting periodic file updater...")
    while True:
        append_auth_log()
        append_bash_history()
        print("[DYNAMIC] Updated logs.")
        time.sleep(random.randint(30, 120))  # Wait 30-120 seconds

if __name__ == "__main__":
    main()
