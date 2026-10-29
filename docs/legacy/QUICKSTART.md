# 🚀 Quick Start Guide - GenAI-Honeypot

**Get up and running in under 15 minutes!** This guide gets you from zero to fully working honeypot with beautiful dashboards.

## ⚡ Super Quick Start (5 Commands)

If you just want to see it work, copy and paste these commands:

```bash
# 1. Download the project
git clone https://github.com/aniketpitre/GenAI-Honeypot.git && cd GenAI-Honeypot

# 2. Set your Google AI key (get one free at: https://aistudio.google.com/app/apikey)
export GEMINI_API_KEY="your_api_key_here"

# 3. Run the magic script
chmod +x build_and_run.sh && ./build_and_run.sh

# 4. Wait 5 minutes, then open: http://localhost:5601

# 5. Test it works
ssh root@localhost -p 2223
```

**That's it!** You now have a working AI-powered honeypot! 🎉

---

## 📋 What You Need First

### System Requirements ✅
- **Computer**: Windows 10+, macOS 10.15+, or Ubuntu 18.04+
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 10GB free space
- **Internet**: For downloading Docker images and AI API

### Software to Install 📥

#### Windows 🪟
1. **Docker Desktop**: https://www.docker.com/products/docker-desktop/
2. **Git**: https://git-scm.com/download/win
3. **Google AI Key**: https://aistudio.google.com/app/apikey (free)

#### macOS 🍎
1. **Docker Desktop**: https://www.docker.com/products/docker-desktop/
2. **Git**: Usually pre-installed, or from https://git-scm.com/download/mac
3. **Google AI Key**: https://aistudio.google.com/app/apikey (free)

#### Linux 🐧
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install docker.io docker-compose git python3

# Start Docker
sudo systemctl start docker && sudo usermod -aG docker $USER
newgrp docker

# Get Google AI Key: https://aistudio.google.com/app/apikey (free)
```

---

## 🏃‍♂️ Step-by-Step Walkthrough

### Step 1: Get Google AI Key 🔑

1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. **Copy the key** (starts with "AIza...")
5. **Keep it safe** - you'll need it in Step 3

### Step 2: Download the Project 📥

Open your terminal/command prompt:

```bash
# Clone the repository
git clone https://github.com/aniketpitre/GenAI-Honeypot.git

# Enter the project directory
cd GenAI-Honeypot

# Check what's inside
ls -la
```

### Step 3: Set Your AI Key 🔧

Replace `your_actual_key_here` with the key from Step 1:

#### Windows PowerShell 🪟
```powershell
$env:GEMINI_API_KEY="your_actual_key_here"
```

#### macOS/Linux 🍎🐧
```bash
export GEMINI_API_KEY="your_actual_key_here"
```

**Verify it's set:**
```bash
echo $GEMINI_API_KEY  # Should show your key
```

### Step 4: One-Click Setup 🎬

Use the automated script:

```bash
# Make it executable
chmod +x build_and_run.sh

# Run everything automatically
./build_and_run.sh
```

**What this script does:**
1. ✅ Generates realistic AI data (1-2 minutes)
2. ✅ Builds all Docker containers (3-5 minutes)  
3. ✅ Starts all services (1-2 minutes)
4. ✅ Verifies everything is working

### Step 5: Verify It's Working ✅

Check that all services are running:

```bash
docker compose ps
```

**Expected output** (all should show "Up"):
```
NAME            STATUS
elasticsearch   Up 3 minutes
kibana          Up 3 minutes  
logstash        Up 3 minutes
honeypot-test   Up 3 minutes
```

### Step 6: Open Your Dashboard 🌐

1. **Wait 3-5 minutes** for Kibana to fully start
2. **Open your web browser**
3. **Go to**: `http://localhost:5601`
4. **You should see** the Kibana welcome screen

**If it doesn't load**: Wait longer (can take 5+ minutes on slower systems)

---

## 📊 Create Your First Dashboard

### Step 1: Create Data View 📋

1. **Click the hamburger menu** (≡) in top-left
2. **Go to "Stack Management"** (at bottom of menu)
3. **Click "Data Views"** in left sidebar
4. **Click "Create data view"**
5. **Fill in**:
   - **Name**: `honeypot-logs`
   - **Index pattern**: `logstash-*`
   - **Timestamp**: `@timestamp` (auto-selected)
6. **Click "Save data view to Kibana"**

### Step 2: Create Your Dashboard 📈

1. **Go to "Analytics" → "Dashboard"**
2. **Click "Create dashboard"**
3. **Click "Create visualization"**
4. **Select**: `honeypot-logs`
5. **Choose "Line" chart**
6. **Configure**:
   - **X-axis**: `@timestamp`
   - **Y-axis**: Count
7. **Click "Save and return"**
8. **Save dashboard** as "My Security Dashboard"

🎉 **Congratulations!** You now have a working security dashboard!

---

## 🧪 Test Your Honeypot

### Generate Some Attack Data 🎯

Try these commands to create interesting log entries:

```bash
# Simulate SSH brute force attacks
ssh root@localhost -p 2223
# When prompted for password, type anything and press Enter
# Do this a few times with different usernames

# Test the web server
curl http://localhost:80

# Generate multiple failed attempts
for i in {1..5}; do ssh -o ConnectTimeout=3 admin@localhost -p 2223 || true; sleep 1; done
```

### Watch the Data Flow 👁️

```bash
# See live logs from the honeypot
docker compose logs -f honeypot-test

# Check if data is reaching Elasticsearch
curl "localhost:9200/_cat/indices?v"

# See recent log entries
curl "localhost:9200/logstash-*/_search?pretty&size=3"
```

### Refresh Your Dashboard 🔄

1. **Go back to Kibana**: `http://localhost:5601`
2. **Open your dashboard**
3. **Set time range** to "Last 15 minutes"
4. **You should see** your test attacks in the chart!

---

## 🐛 Quick Troubleshooting

### Problem: "Docker not found" ❌

**Solution**: Install Docker Desktop for your OS
- Windows/Mac: Download from docker.com
- Linux: `sudo apt install docker.io`

### Problem: "Permission denied" ❌

**Linux**: Add yourself to docker group
```bash
sudo usermod -aG docker $USER
newgrp docker
```

**Windows**: Run PowerShell as Administrator

### Problem: "Port already in use" ❌

Something else is using the ports:
```bash
# Find what's using port 5601 (Kibana)
netstat -tulpn | grep :5601

# Kill the process (replace XXXX with actual PID)
kill -9 XXXX
```

### Problem: "Kibana won't load" ❌

**Wait longer** - Kibana can take 5+ minutes to start:
```bash
# Check Kibana status
docker compose logs kibana | tail -10

# Wait 5 minutes
sleep 300
curl http://localhost:5601
```

### Problem: "No data in Kibana" ❌

Check the data pipeline:
```bash
# 1. Check if logs exist in honeypot
docker compose exec honeypot-test ls -la /var/log/

# 2. Check if Logstash is processing
docker compose logs logstash | grep "successfully"

# 3. Check if Elasticsearch has data
curl "localhost:9200/_cat/indices?v"
```

### Problem: "AI generation failed" ❌

Check your API key:
```bash
# Verify key is set
echo $GEMINI_API_KEY

# Test the API
python3 -c "
import os
import google.generativeai as genai
genai.configure(api_key=os.environ['GEMINI_API_KEY'])
model = genai.GenerativeModel('gemini-2.0-flash-exp')
print('AI key works!')
"
```

---

## 🎯 What's Next?

### Immediate Next Steps 🚶‍♂️
1. **Explore Kibana** - Try different chart types
2. **Generate more data** - Run the AI script again
3. **Create more visualizations** - Show different attack patterns
4. **Test different attacks** - SSH, web requests, etc.

### Learning Path 📚
1. **Read the full README.md** - Understand how everything works
2. **Try the TUTORIAL.md** - Step-by-step learning guide
3. **Study ARCHITECTURE.md** - Technical deep dive
4. **Experiment** - Modify configurations and see what happens

### Advanced Usage 🚀
1. **Custom AI personas** - Edit `persona_config.json`
2. **Multiple honeypots** - Scale up with docker-compose
3. **Real-time alerts** - Set up Kibana watchers
4. **Integration** - Connect to SIEM systems

---

## 📞 Getting Help

### If You're Stuck 🆘

1. **Check the logs**: `docker compose logs [service_name]`
2. **Read error messages** - they usually tell you what's wrong
3. **Try restarting**: `docker compose restart`
4. **Full reset**: `docker compose down -v && ./build_and_run.sh`

### Resources 📖
- **Full documentation** - All the .md files in this project
- **GitHub Issues** - https://github.com/aniketpitre/GenAI-Honeypot/issues
- **Docker docs** - https://docs.docker.com/
- **Elasticsearch docs** - https://www.elastic.co/guide/

### Command Quick Reference 📝

| Task | Command |
|------|---------|
| Start everything | `./build_and_run.sh` |
| Check status | `docker compose ps` |
| View logs | `docker compose logs -f` |
| Stop everything | `docker compose down` |
| Restart services | `docker compose restart` |
| Test SSH honeypot | `ssh root@localhost -p 2223` |
| Open Kibana | Browser: `http://localhost:5601` |
| Generate new data | `python3 generation_script.py --persona persona_config.json --output generated_files` |

---

## 🎉 Success!

**You now have:**
- ✅ A working AI-powered honeypot
- ✅ Professional monitoring dashboards  
- ✅ Real-time attack visualization
- ✅ A platform for cybersecurity learning
- ✅ The foundation for advanced security research

**Welcome to the world of cybersecurity research!** 🛡️🔍

**Time to start exploring and learning!** The honeypot is your laboratory - experiment, learn, and discover how cybersecurity really works.

---

*Need more details? Check out the other documentation files for deeper dives into each component!*