#!/usr/bin/env python3
import time
import random
import subprocess
from datetime import datetime

# Simulate web requests to localhost (nginx/apache)
def simulate_web_requests():
    urls = ["http://localhost", "http://localhost/index.html", "http://localhost/admin", "http://localhost/login"]
    url = random.choice(urls)
    try:
        subprocess.run(["curl", "-s", url], check=True)
        print(f"[NET] Web request sent: {url}")
    except Exception as e:
        print(f"[NET] Web request failed: {url} - {e}")

# Simulate SSH connection attempts
def simulate_ssh_sessions():
    users = ["sysadmin", "root", "webmaster", "admin"]
    user = random.choice(users)
    # This will fail unless keys/passwords are set, but that's realistic for brute force
    try:
        subprocess.run(["ssh", f"{user}@localhost", "exit"], timeout=5)
        print(f"[NET] SSH session attempted: {user}@localhost")
    except Exception as e:
        print(f"[NET] SSH session failed: {user}@localhost - {e}")

def main():
    print("[NET] Starting network traffic simulator...")
    while True:
        if random.random() < 0.7:
            simulate_web_requests()
        else:
            simulate_ssh_sessions()
        time.sleep(random.randint(20, 90))  # Wait 20-90 seconds

if __name__ == "__main__":
    main()
