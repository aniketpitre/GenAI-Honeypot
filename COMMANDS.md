# GenAI-Honeypot Commands Reference 🎯 - Beginner's Guide

This guide provides all the commands you'll need to run the GenAI-Honeypot project. **Everything is explained in simple terms** with examples for Windows, macOS, and Linux.

## 📋 Table of Contents
1. [🚀 Quick Start (Copy & Paste Commands)](#-quick-start-copy--paste-commands)
2. [🔧 Setup Commands by Operating System](#-setup-commands-by-operating-system)
3. [📊 Monitoring Commands (Check if Everything Works)](#-monitoring-commands-check-if-everything-works)
4. [🛠️ Maintenance Commands (Keep Things Running)](#️-maintenance-commands-keep-things-running)
5. [🐛 Troubleshooting Commands (Fix Problems)](#-troubleshooting-commands-fix-problems)
6. [🎓 Learning Commands (Understand What's Happening)](#-learning-commands-understand-whats-happening)

---

## 🚀 Quick Start (Copy & Paste Commands)

### For Absolute Beginners - Just Copy These! 📋

#### Step 1: Download the Project
```bash
git clone https://github.com/aniketpitre/GenAI-Honeypot.git
cd GenAI-Honeypot
```
**What this does**: Downloads all the project files to your computer

#### Step 2: Set Your AI Key
Replace `your_api_key_here` with your actual Google AI key:

**Windows PowerShell** 🪟
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

**macOS/Linux Terminal** 🍎🐧
```bash
export GEMINI_API_KEY="your_api_key_here"
```
**What this does**: Tells the AI system how to access Google's AI

#### Step 3: Start Everything (The Magic Button!) ✨
```bash
chmod +x build_and_run.sh
./build_and_run.sh
```
**What this does**: Automatically sets up and starts the entire honeypot system

#### Step 4: Check if it Worked ✅
```bash
docker compose ps
```
**Expected result**: You should see 4 services running (all showing "Up")

#### Step 5: Open Your Dashboard 🌐
- Open your web browser
- Go to: `http://localhost:5601`
- Wait 3-5 minutes if it doesn't load immediately

---

## 🔧 Setup Commands by Operating System

### Windows Users 🪟

#### Prerequisites Installation
```powershell
# Check if Docker is installed
docker --version

# Check if Git is installed
git --version

# If either command fails, install them first!
```

#### Setting Environment Variables
```powershell
# Set API key for current session
$env:GEMINI_API_KEY="your_api_key_here"

# Set API key permanently (optional)
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your_api_key_here", "User")
```

#### Running Commands
```powershell
# Navigate to project folder
cd C:\path\to\GenAI-Honeypot

# Make sure Docker Desktop is running first!
# Check system info
docker info

# Generate AI data
python generation_script.py --persona persona_config.json --output generated_files

# Build and start
docker compose build --no-cache
docker compose up -d
```

### macOS Users 🍎

#### Prerequisites Check
```bash
# Check if Docker is installed
docker --version

# Check if Git is installed (usually pre-installed)
git --version

# Check if Python is available
python3 --version
```

#### Setting Environment Variables
```bash
# Set API key for current session
export GEMINI_API_KEY="your_api_key_here"

# Set API key permanently
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

#### Running Commands
```bash
# Navigate to project
cd ~/Downloads/GenAI-Honeypot  # or wherever you downloaded it

# Make sure Docker Desktop is running
docker info

# Generate AI data
python3 generation_script.py --persona persona_config.json --output generated_files

# Build and start
docker compose build --no-cache
docker compose up -d
```

### Linux Users 🐧

#### Prerequisites Installation (Ubuntu/Debian)
```bash
# Update system
sudo apt update

# Install Docker
sudo apt install docker.io docker-compose

# Install Git and Python
sudo apt install git python3 python3-pip

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add yourself to docker group (to avoid sudo)
sudo usermod -aG docker $USER
newgrp docker
```

#### Setting Environment Variables
```bash
# Set API key for current session
export GEMINI_API_KEY="your_api_key_here"

# Set API key permanently
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

#### Running Commands
```bash
# Navigate to project
cd ~/GenAI-Honeypot

# Check Docker is working
docker info

# Generate AI data
python3 generation_script.py --persona persona_config.json --output generated_files

# Build and start
docker compose build --no-cache
docker compose up -d
```

---

## 📊 Monitoring Commands (Check if Everything Works)

### Basic Health Checks 🏥

#### Check All Services
```bash
docker compose ps
```
**What you should see**: 4 services all showing "Up" status:
- `elasticsearch` - The database
- `kibana` - The dashboard
- `logstash` - The log processor  
- `honeypot-test` - The fake server

#### Check Individual Services
```bash
# Check if Kibana dashboard is ready
curl http://localhost:5601

# Check if the web server is working
curl http://localhost:80

# Check if SSH honeypot is listening
ssh root@localhost -p 2223
# (This should ask for a password - that's good!)
```

### Real-Time Monitoring 👁️

#### Watch Live Logs
```bash
# See all logs in real-time
docker compose logs -f

# See logs from just the honeypot
docker compose logs -f honeypot-test

# See logs from Elasticsearch
docker compose logs -f elasticsearch
```
**What this shows**: Live updates of what's happening in each service

#### Monitor Resource Usage
```bash
# See how much CPU/memory each service uses
docker stats

# Check disk space used by Docker
docker system df
```

### Testing the Honeypot 🧪

#### Generate Test Traffic
```bash
# Try to connect to the SSH honeypot (this creates log entries)
ssh root@localhost -p 2223
# When it asks for password, type anything and press Enter
# Press Ctrl+C to exit

# Visit the web server (creates web logs)
curl http://localhost:80
```

#### Check if Logs are Being Created
```bash
# Look inside the honeypot container
docker compose exec honeypot-test ls -la /var/log/

# See recent authentication attempts
docker compose exec honeypot-test tail -f /var/log/auth.log
```

---

## 🛠️ Maintenance Commands (Keep Things Running)

### Daily Operations 📅

#### Restart Everything
```bash
# Stop all services
docker compose down

# Start all services
docker compose up -d

# Or do both in one command
docker compose restart
```
**When to use**: If something stops working or seems slow

#### Generate Fresh AI Data
```bash
# Create new fake data
python3 generation_script.py --persona persona_config.json --output generated_files

# Restart the honeypot to use new data
docker compose restart honeypot-test
```
**When to use**: Daily or weekly to keep data fresh

#### Clean Up Space
```bash
# Remove old Docker images and data
docker system prune -f

# See how much space you freed
docker system df
```
**When to use**: When your computer is running low on disk space

### Backup and Restore 💾

#### Backup Your Data
```bash
# Create backup folder
mkdir backup_$(date +%Y%m%d)

# Backup generated files
cp -r generated_files backup_$(date +%Y%m%d)/

# Backup configuration
cp persona_config.json backup_$(date +%Y%m%d)/
```

#### Complete Reset (Start Fresh)
```bash
# DANGER: This deletes everything!
docker compose down -v
docker system prune -a --volumes -f
rm -rf generated_files/

# Then start over with:
./build_and_run.sh
```

---

## 🐛 Troubleshooting Commands (Fix Problems)

### Common Problems and Solutions 🔧

#### Problem: "Docker not found"
```bash
# Check if Docker is installed
which docker
docker --version

# If not found, install Docker first!
```
**Solution**: Install Docker Desktop for your operating system

#### Problem: "Permission denied"
```bash
# Linux: Add yourself to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or use sudo (not recommended)
sudo docker compose up -d
```

#### Problem: "Port already in use"
```bash
# Find what's using the port
netstat -tulpn | grep :5601  # Kibana
netstat -tulpn | grep :2223  # SSH honeypot

# Kill the conflicting process (replace PID with actual number)
kill -9 [PID]
```

#### Problem: "Can't access Kibana"
```bash
# Check if Kibana is really running
docker compose ps | grep kibana

# Check Kibana logs for errors
docker compose logs kibana | tail -20

# Wait longer (Kibana can take 5+ minutes to start)
sleep 300  # Wait 5 minutes
curl http://localhost:5601
```

#### Problem: "No data in Kibana"
```bash
# Check if logs are being generated
docker compose exec honeypot-test ls -la /var/log/

# Check if Logstash is processing logs
docker compose logs logstash | grep "successfully"

# Check Elasticsearch for data
curl "localhost:9200/_cat/indices?v"
```

### Diagnostic Commands 🔍

#### Get Detailed Information
```bash
# Check Docker system info
docker info

# Check container details
docker compose ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}"

# Check network connections
docker network ls
docker network inspect genai-honeypot_default
```

#### Export Logs for Help
```bash
# Save all logs to a file
docker compose logs > debug_logs.txt

# Save system info
docker info > system_info.txt
docker compose ps > services_status.txt
```
**Use these files when asking for help**

---

## 🎓 Learning Commands (Understand What's Happening)

### Explore the System 🔍

#### Look Inside Containers
```bash
# Open a command line inside the honeypot
docker compose exec honeypot-test /bin/bash

# Once inside, you can explore:
ls -la /var/log/          # See log files
ps aux                    # See running processes
netstat -tulpn           # See network connections
exit                     # Leave the container
```

#### Understand the Data Flow
```bash
# 1. Check generated AI data
cat generated_files/var/log/auth.log

# 2. See how it gets into the container
docker compose exec honeypot-test cat /var/log/auth.log

# 3. Check if Logstash is processing it
docker compose logs logstash | grep "auth.log"

# 4. See if Elasticsearch has the data
curl "localhost:9200/logstash-*/_search?pretty&size=1"
```

### Test Different Scenarios 🧪

#### Simulate Different Attacks
```bash
# Simulate failed SSH login
sshpass -p "wrongpassword" ssh root@localhost -p 2223 || echo "Failed as expected"

# Simulate web access
curl -A "Hacker Browser" http://localhost:80

# Generate multiple connection attempts
for i in {1..5}; do
    ssh -o ConnectTimeout=3 root@localhost -p 2223 || true
    sleep 1
done
```

#### Watch Changes in Real-Time
```bash
# Terminal 1: Watch honeypot logs
docker compose logs -f honeypot-test

# Terminal 2: Watch Logstash processing
docker compose logs -f logstash

# Terminal 3: Try connections
ssh root@localhost -p 2223
```

### Advanced Learning 🎓

#### Understand Configuration Files
```bash
# See how Docker builds the honeypot
cat Dockerfile

# See how services connect
cat docker-compose.yml

# See how logs are processed
cat logstash/pipeline/logstash.conf

# See what AI personality we're using
cat persona_config.json
```

#### Modify and Experiment
```bash
# Create a custom persona
cp persona_config.json my_persona.json
# Edit my_persona.json with your favorite text editor

# Generate data with your custom persona
python3 generation_script.py --persona my_persona.json --output my_generated_files

# Test with your custom data
# (Edit docker-compose.yml to point to your new folder)
```

---

## 💡 Pro Tips and Best Practices

### Daily Workflow 📅
1. **Morning**: Check status with `docker compose ps`
2. **Generate fresh data**: Run the generation script
3. **Monitor**: Look at Kibana dashboard
4. **Evening**: Check logs for interesting activities

### Performance Tips ⚡
- **Use `-d` flag**: Always run `docker compose up -d` (background mode)
- **Clean regularly**: Run `docker system prune -f` weekly
- **Monitor resources**: Check `docker stats` if things seem slow
- **Restart if needed**: `docker compose restart` fixes most issues

### Security Reminders 🔒
- **Never expose to internet**: This is for learning only!
- **Use strong API keys**: Keep your Google AI key secret
- **Regular updates**: Pull latest code occasionally with `git pull`
- **Backup important data**: Save your custom configurations

### Getting Help 🆘
- **Read the error messages**: They usually tell you exactly what's wrong
- **Check the logs**: `docker compose logs [service_name]`
- **Google the error**: Most Docker errors have known solutions
- **Ask for help**: Include the output of diagnostic commands

---

## 🎯 Command Quick Reference

| What You Want to Do | Command |
|-------------------|---------|
| Start everything | `./build_and_run.sh` |
| Check if running | `docker compose ps` |
| See live logs | `docker compose logs -f` |
| Stop everything | `docker compose down` |
| Restart everything | `docker compose restart` |
| Open Kibana | Browser: `http://localhost:5601` |
| Test SSH honeypot | `ssh root@localhost -p 2223` |
| Generate new data | `python3 generation_script.py --persona persona_config.json --output generated_files` |
| Clean up space | `docker system prune -f` |
| Get help with errors | `docker compose logs [service_name]` |

---

## 🌐 Kibana Dashboard and Data View Setup

### Creating Your First Data View 📊

#### Step 1: Access Kibana
1. Make sure all services are running: `docker compose ps`
2. Open your browser and go to: `http://localhost:5601`
3. Wait 3-5 minutes for Kibana to fully load

#### Step 2: Create Data View
1. **Click the hamburger menu** (≡) in the top-left corner
2. **Go to "Stack Management"** (usually at the bottom of the menu)
3. **Click "Data Views"** in the left sidebar
4. **Click "Create data view"** button

#### Step 3: Configure Data View
Fill in these details:
- **Name**: `honeypot-logs` (or any name you prefer)
- **Index pattern**: `logstash-*` (this finds all our log data)
- **Timestamp field**: `@timestamp` (should auto-select)
- **Click "Save data view to Kibana"**

#### Step 4: Create Your First Dashboard
1. **Go to "Analytics" → "Dashboard"** from the main menu
2. **Click "Create dashboard"**
3. **Click "Create visualization"**
4. **Select your data view**: `honeypot-logs`

#### Step 5: Add Visualizations
Try these beginner-friendly charts:

**A. Failed Login Attempts Timeline**
- **Chart type**: Line chart
- **X-axis**: `@timestamp` (time-based)
- **Y-axis**: Count of documents
- **Filter**: Add filter `message` contains `"Failed password"`

**B. Top Attacking IPs**
- **Chart type**: Bar chart (horizontal)
- **X-axis**: Top values of `source_ip.keyword`
- **Y-axis**: Count of documents
- **Size**: Show top 10

**C. User Activity Over Time**
- **Chart type**: Area chart
- **X-axis**: `@timestamp`
- **Y-axis**: Count
- **Split series**: `user.keyword`

#### Step 6: Save Your Dashboard
1. **Click "Save"** in the top-right corner
2. **Name it**: "My Honeypot Security Dashboard"
3. **Add description**: "Real-time monitoring of honeypot activities"
4. **Click "Save"**

### Advanced Dashboard Features 🚀

#### Setting Up Alerts
```bash
# Check if there's new suspicious activity
curl -X GET "localhost:9200/logstash-*/_search?pretty" \
     -H 'Content-Type: application/json' \
     -d '{"query": {"range": {"@timestamp": {"gte": "now-1h"}}}}'
```

#### Exporting/Importing Dashboards
```bash
# Export your dashboard
curl -X POST "localhost:5601/api/saved_objects/_export" \
     -H "kbn-xsrf: true" \
     -H "Content-Type: application/json" \
     -d '{"type":"dashboard"}' > my_dashboards.ndjson

# Import dashboards (if you have a file)
curl -X POST "localhost:5601/api/saved_objects/_import" \
     -H "kbn-xsrf: true" \
     -F file=@my_dashboards.ndjson
```

---

**Remember**: All commands should be run from the project directory where `docker-compose.yml` is located! 📁

**Having trouble?** Read the error messages carefully - they usually tell you exactly what to fix! 🔍