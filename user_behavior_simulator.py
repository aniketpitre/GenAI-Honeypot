#!/usr/bin/env python3
import time
import random
from datetime import datetime
from pathlib import Path

# Paths to files to update
backup_log = Path('generated_files/var/log/backup.log')
auth_log = Path('generated_files/var/log/auth.log')
bash_history = Path('generated_files/home/sysadmin/.bash_history')

# Simulate cron job: backup
backup_commands = [
    'tar -czf /backup/home_sysadmin_$(date +%F).tar.gz /home/sysadmin',
    'mysqldump -u root --all-databases > /backup/db_backup_$(date +%F).sql',
    'rsync -av /var/www/ /backup/www_backup/'
]

# Simulate admin login
admin_users = ['sysadmin', 'root']

def append_backup_log():
    now = datetime.now().strftime('%b %d %H:%M:%S')
    cmd = random.choice(backup_commands)
    entry = f"{now} debian CRON[12345]: Executed backup: {cmd}\n"
    with open(backup_log, 'a') as f:
        f.write(entry)
    with open(bash_history, 'a') as f:
        f.write(cmd + '\n')

def append_admin_login():
    now = datetime.now().strftime('%b %d %H:%M:%S')
    user = random.choice(admin_users)
    entry = f"{now} debian sshd[12345]: Accepted password for {user} from 127.0.0.1 port {random.randint(1000,65000)} ssh2\n"
    with open(auth_log, 'a') as f:
        f.write(entry)
    with open(bash_history, 'a') as f:
        f.write(f"ssh {user}@localhost\n")

def main():
    print("[USER] Starting user behavior simulator...")
    while True:
        if random.random() < 0.5:
            append_backup_log()
        else:
            append_admin_login()
        print("[USER] Simulated user behavior event.")
        time.sleep(random.randint(60, 180))  # Wait 1-3 minutes

if __name__ == "__main__":
    main()
