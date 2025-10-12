# GenAI-Honeypot 🍯 - Complete Beginner's Guide

[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![ELK Stack](https://img.shields.io/badge/Elastic%20Stack-005571?style=for-the-badge&logo=elastic&logoColor=white)](https://www.elastic.co/)
[![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)](https://www.python.org/)
[![AI](https://img.shields.io/badge/AI%20Powered-FF6B6B?style=for-the-badge&logo=openai&logoColor=white)](https://ai.google.dev/)

---

## 🤔 What is This Project? (In Simple Terms)

**Think of this as a "digital decoy" or "cyber trap"** 🪤

Imagine you want to catch a burglar, so you set up a fake house with cameras to see how they break in. That's exactly what this project does, but for computer hackers!

### What This Project Does:
- **Creates a Fake Computer System** 💻 - Looks like a real web server that hackers want to attack
- **Uses AI to Make it Realistic** 🤖 - Google's AI creates fake user activity, logs, and files
- **Monitors Everything** 👁️ - Records every action hackers take when they try to break in
- **Shows Beautiful Reports** 📊 - Creates charts and graphs to understand the attacks

### Why This is Useful:
- **🎓 Learn Cybersecurity**: See real hacking techniques in action
- **🔬 Research Security**: Study how attacks happen
- **🛡️ Test Defenses**: Check if your security tools work
- **📈 Understand Threats**: Know what hackers are trying to do

---

## 📋 Table of Contents

1. [🎯 What You'll Need (Requirements)](#-what-youll-need-requirements)
2. [💾 Installing Everything (Step by Step)](#-installing-everything-step-by-step)
3. [📁 Understanding Each File](#-understanding-each-file)
4. [🚀 Running the Project](#-running-the-project)
5. [📊 Creating Dashboards](#-creating-dashboards)
6. [🔧 How Everything Works](#-how-everything-works)
7. [🐛 Fixing Problems](#-fixing-problems)
8. [❓ Frequently Asked Questions](#-frequently-asked-questions)

---

## 📚 Documentation Index

Quick links to all guides and references in this repo:

- QUICKSTART: Get running fast in 5 commands → [QUICKSTART.md](./QUICKSTART.md)
- Commands Reference: All commands with explanations → [COMMANDS.md](./COMMANDS.md)
- Tutorial: Beginner-friendly, step-by-step learning path → [TUTORIAL.md](./TUTORIAL.md)
- Architecture: How everything works under the hood → [ARCHITECTURE.md](./ARCHITECTURE.md)
- Config Docs: Line-by-line explanation of configs → [CONFIG_DOCS.md](./CONFIG_DOCS.md)

Tip: Start with QUICKSTART.md, then explore the Tutorial and Dashboard sections here.

## 🎯 What You'll Need (Requirements)

### 💻 System Requirements
- **Computer**: Windows 10/11, macOS 10.15+, or Linux
- **RAM**: At least 8GB (16GB recommended)
- **Storage**: 10GB free space
- **Internet**: For downloading and AI features

### 🛠️ Software You Need to Install

#### For Windows Users 🪟
1. **Docker Desktop**: [Download here](https://www.docker.com/products/docker-desktop/)
2. **Git**: [Download here](https://git-scm.com/download/win)
3. **Google AI API Key**: [Get free key here](https://aistudio.google.com/app/apikey)

#### For macOS Users 🍎
1. **Docker Desktop**: [Download here](https://www.docker.com/products/docker-desktop/)
2. **Git**: Usually pre-installed, or [download here](https://git-scm.com/download/mac)
3. **Google AI API Key**: [Get free key here](https://aistudio.google.com/app/apikey)

#### For Linux Users 🐧
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose git python3 python3-pip

# CentOS/RHEL/Fedora
sudo dnf install docker docker-compose git python3 python3-pip

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

---

## 💾 Installing Everything (Step by Step)

### Step 1: Get Google AI Key 🔑
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (keep it safe!)

### Step 2: Download the Project 📥

#### Windows (PowerShell) 🪟
```powershell
# Open PowerShell as Administrator
git clone https://github.com/aniketpitre/GenAI-Honeypot.git
cd GenAI-Honeypot
```

#### macOS (Terminal) 🍎
```bash
# Open Terminal
git clone https://github.com/aniketpitre/GenAI-Honeypot.git
cd GenAI-Honeypot
```

#### Linux (Terminal) 🐧
```bash
# Open Terminal
git clone https://github.com/aniketpitre/GenAI-Honeypot.git
cd GenAI-Honeypot
```

### Step 3: Set Up Your API Key 🔧

#### Windows 🪟
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

#### macOS/Linux 🍎🐧
```bash
export GEMINI_API_KEY="your_api_key_here"
```

---

## 📁 Understanding Each File (What Does What?)

Let me explain every file in simple terms:

### 🐳 Docker Files (The "Container" System)
- **`Dockerfile`** - Instructions to build our fake computer system
  - *Think of it like a recipe to make a cake - tells Docker how to build our honeypot*
- **`docker-compose.yml`** - Connects all the different parts together
  - *Like a conductor of an orchestra - makes sure all parts work together*
- **`entrypoint.sh`** - The first thing that runs when our fake system starts
  - *Like the power button - starts all the services*

### 🤖 AI and Data Files
- **`generation_script.py`** - The AI brain that creates fake data
  - *Uses Google's AI to write fake user activities, login attempts, etc.*
- **`persona_config.json`** - Tells the AI what kind of fake user to create
  - *Like giving the AI a character to play - "be a system administrator named John"*
- **`requirements.txt`** - List of Python tools needed
  - *Like a shopping list of ingredients*

### 📊 Monitoring Files
- **`filebeat/`** folder - Collects log files
  - *Like a mail carrier - picks up logs and delivers them*
- **`logstash/`** folder - Processes and organizes logs
  - *Like a librarian - sorts and categorizes all the information*

### 📖 Documentation Files
- **`README.md`** - This file! Main instructions
- **`ARCHITECTURE.md`** - Technical details of how it works
- **`CONFIG_DOCS.md`** - Explains all settings
- **`COMMANDS.md`** - List of useful commands
- **`TUTORIAL.md`** - Step-by-step learning guide

### 🚀 Helper Files
- **`build_and_run.sh`** - One-click script to start everything
  - *Like a "easy button" - runs multiple commands at once*

---

## 🚀 Running the Project (Complete Guide)

### Method 1: Easy Way (Automatic) ⚡
```bash
# Make the script executable
chmod +x build_and_run.sh

# Run everything automatically
./build_and_run.sh
```

### Method 2: Step by Step (Manual) 🔧

#### Step 1: Generate AI Content 🤖
```bash
# Create realistic fake data using AI
python3 generation_script.py --persona persona_config.json --output generated_files
```
**What this does:** Creates fake login logs, user activities, and admin tasks

#### Step 2: Build the System 🏗️
```bash
# Build our fake computer system
docker compose build --no-cache
```
**What this does:** Creates a pretend Linux server with web services

#### Step 3: Start Everything 🎬
```bash
# Start all services
docker compose up -d
```
**What this does:** Runs 4 different services:
- **Honeypot**: The fake server (port 2223 for SSH, port 80 for web)
- **Elasticsearch**: Stores all the data
- **Logstash**: Processes the logs
- **Kibana**: Creates the dashboards (port 5601)

#### Step 4: Check Everything is Working ✅
```bash
# See if all services are running
docker compose ps
```
**Expected output:**
```
NAME            STATUS    PORTS
elasticsearch   Up        9200/tcp
kibana          Up        0.0.0.0:5601->5601/tcp
logstash        Up        5044/tcp
honeypot-test   Up        0.0.0.0:80->80/tcp, 0.0.0.0:2223->22/tcp
```

---

## 📊 Creating Dashboards (Kibana Data Views)

### Step 1: Open Kibana 🌐
1. **Wait 3-5 minutes** for everything to start up
2. Open your web browser
3. Go to: `http://localhost:5601`
4. You should see the Kibana welcome page

### Step 2: Create a Data View 📋

#### What is a Data View?
*Think of it as telling Kibana where to find your data - like giving someone directions to your house*

1. **Click on the hamburger menu** (three lines) in the top left
2. **Go to "Stack Management"** (usually at the bottom)
3. **Click "Data Views"** in the left sidebar
4. **Click "Create data view"** button

#### Fill in the Details:
- **Name**: `honeypot-logs` (you can name it anything)
- **Index pattern**: `logstash-*` (this finds all our log data)
- **Timestamp field**: `@timestamp` (this should be auto-selected)
- **Click "Save data view to Kibana"**

### Step 3: Create Your First Dashboard 📈

1. **Go to "Analytics" → "Dashboard"** from the main menu
2. **Click "Create dashboard"**
3. **Click "Create visualization"**
4. **Select your data view**: `honeypot-logs`

#### Suggested Visualizations:
1. **Failed Login Attempts Over Time**
   - Chart type: Line chart
   - X-axis: @timestamp
   - Y-axis: Count of documents
   - Filter: `message: "Failed password"`

2. **Top Attacking IP Addresses**
   - Chart type: Bar chart
   - X-axis: Top values of `source_ip`
   - Y-axis: Count

3. **User Activity Timeline**
   - Chart type: Timeline
   - X-axis: @timestamp
   - Split by: `user`

### Step 4: Save and Share 💾
1. **Click "Save"** in the top right
2. **Give your dashboard a name**: "Honeypot Security Dashboard"
3. **Click "Save"**

---

## 🔧 How Everything Works (The Complete Story)

### The Big Picture 🖼️
```
[Hacker] → [Honeypot] → [Logs] → [Processing] → [Dashboard]
    ↓           ↓          ↓          ↓           ↓
  Attacks    Fake       Raw       Clean      Beautiful
            Server     Data       Data       Charts
```

### Step-by-Step Process 📝

#### 1. AI Creates Realistic Content 🤖
- **Script**: `generation_script.py`
- **What it does**: Uses Google's Gemini AI to create:
  - Fake login attempts (failed passwords, usernames)
  - Realistic user activities (commands, file access)
  - System administrator tasks (updates, backups)
- **Why**: Makes the honeypot look like a real, active server

#### 2. Honeypot Runs as Fake Server 🎭
- **Container**: Custom Ubuntu Linux
- **Services**:
  - **SSH (port 2223)**: Fake command line access
  - **Web (port 80)**: Fake website
  - **Rsyslog**: Records all activities
- **Purpose**: Looks like a real server that hackers want to attack

#### 3. Filebeat Collects Logs 📮
- **Location**: Inside the honeypot container
- **Job**: Watches log files and sends new entries to Logstash
- **Files monitored**:
  - `/var/log/auth.log` (login attempts)
  - `/home/sysadmin/.bash_history` (commands)
  - Custom application logs

#### 4. Logstash Processes Data 🏭
- **Input**: Raw log files from Filebeat
- **Processing**:
  - Parses different log formats
  - Extracts important information (IP addresses, usernames, timestamps)
  - Adds labels and categories
- **Output**: Clean, structured data to Elasticsearch

#### 5. Elasticsearch Stores Everything 🗄️
- **Purpose**: Like a super-fast database
- **Stores**: All processed log data with timestamps
- **Features**: Can search millions of records in milliseconds

#### 6. Kibana Shows Beautiful Dashboards 📊
- **Connects to**: Elasticsearch
- **Creates**: Interactive charts, graphs, and reports
- **Features**: Real-time updates, filtering, drilling down into data

### What Happens When Someone Attacks 🚨

1. **Hacker connects** to port 2223 (SSH) or port 80 (web)
2. **Honeypot pretends** to be a real server
3. **All activities are logged** (even if they succeed or fail)
4. **Filebeat immediately** sends logs to Logstash
5. **Logstash processes** and sends to Elasticsearch
6. **Kibana dashboard updates** in real-time
7. **You can see** exactly what the hacker tried to do!

---

## 🐛 Fixing Problems (Troubleshooting Guide)

### Common Issues and Solutions 🔧

#### ❌ "Docker not found" Error
**Problem**: Docker isn't installed or running
**Solution**:
- **Windows**: Install Docker Desktop, restart computer
- **macOS**: Install Docker Desktop, start the application
- **Linux**: `sudo systemctl start docker`

#### ❌ "Permission denied" Error
**Problem**: Docker needs admin rights
**Solution**:
- **Windows**: Run PowerShell as Administrator
- **macOS**: Use `sudo` before docker commands
- **Linux**: Add user to docker group: `sudo usermod -aG docker $USER`, then log out and back in

#### ❌ "Port already in use" Error
**Problem**: Another program is using the same port
**Solution**:
```bash
# Check what's using the ports
netstat -tulpn | grep :5601  # Kibana
netstat -tulpn | grep :2223  # SSH honeypot
netstat -tulpn | grep :80    # Web server

# Stop the conflicting service or change ports in docker-compose.yml
```

#### ❌ "API key invalid" Error
**Problem**: Google AI API key not set or wrong
**Solution**:
1. Get a new key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Set it again: `export GEMINI_API_KEY="your_new_key"`
3. Regenerate data: `python3 generation_script.py --persona persona_config.json --output generated_files`

#### ❌ Kibana Shows "No Data"
**Problem**: Data isn't flowing through the pipeline
**Solution**:
```bash
# Check if services are running
docker compose ps

# Check logs for errors
docker compose logs elasticsearch
docker compose logs logstash
docker compose logs kibana

# Restart everything
docker compose down
docker compose up -d
```

#### ❌ Can't Access Kibana
**Problem**: Service not ready or wrong URL
**Solution**:
1. **Wait 5 minutes** for everything to fully start
2. **Check URL**: `http://localhost:5601` (not https)
3. **Check if running**: `docker compose ps`
4. **Try different browser** or incognito mode

### Getting Help 🆘

#### Check Service Status
```bash
# See all containers
docker compose ps

# Check specific service logs
docker compose logs [service_name]
# Examples:
docker compose logs honeypot-test
docker compose logs elasticsearch
docker compose logs logstash
docker compose logs kibana
```

#### Reset Everything
```bash
# Stop everything
docker compose down -v

# Remove old data
docker system prune -a --volumes -f

# Start fresh
./build_and_run.sh
```

---

## ❓ Frequently Asked Questions

### 🔒 Security Questions

**Q: Is this safe to run?**
A: Yes! Everything runs in isolated Docker containers. The honeypot can't access your real computer.

**Q: Will hackers attack my real computer?**
A: No! The honeypot only exposes fake services on specific ports. Your real system stays protected.

**Q: Can I run this on my work computer?**
A: Check with your IT department first. Some companies block Docker or unusual network activity.

### 🤖 AI Questions

**Q: Do I need to pay for the Google AI?**
A: Google AI Studio has a generous free tier. You're unlikely to exceed it with normal use.

**Q: Can I use different AI models?**
A: Currently configured for Google Gemini, but you can modify `generation_script.py` for other APIs.

**Q: How realistic is the AI-generated data?**
A: Very realistic! It creates proper log formats, realistic IP addresses, and believable user activities.

### 🛠️ Technical Questions

**Q: How much computer resources does this use?**
A: About 4-6GB of RAM when running. CPU usage is light except during initial setup.

**Q: Can I run this 24/7?**
A: Yes! It's designed to run continuously. Data will accumulate over time.

**Q: How do I back up my data?**
A: Elasticsearch data is stored in Docker volumes. Use `docker volume ls` to see them.

### 🎯 Usage Questions

**Q: How do I attract real attackers?**
A: This is for research/education only. Don't expose it to the internet without proper security measures.

**Q: Can I modify the fake data?**
A: Yes! Edit `persona_config.json` to change the fake user characteristics.

**Q: How do I add more services to monitor?**
A: Modify the `Dockerfile` to install additional services and update `filebeat.yml` to monitor their logs.

---

## 🎓 Learning Path (What to Do Next)

### Beginner Level 🌱
1. **Run the basic setup** following this guide
2. **Explore Kibana dashboards** and try different visualizations
3. **Read the generated logs** to understand what they contain
4. **Try connecting to the honeypot** yourself: `ssh root@localhost -p 2223`

### Intermediate Level 🌿
1. **Modify the persona config** to create different fake users
2. **Add custom log parsing** in Logstash configuration
3. **Create advanced Kibana dashboards** with multiple data sources
4. **Study the Docker setup** to understand containerization

### Advanced Level 🌳
1. **Add new services** to the honeypot (FTP, MySQL, etc.)
2. **Implement alerting** for suspicious activities
3. **Scale the system** with multiple honeypots
4. **Integrate with security tools** (SIEM, threat intelligence)

---

## 🤝 Contributing and Support

### Found a Bug? 🐞
1. Check the [troubleshooting section](#-fixing-problems-troubleshooting-guide) first
2. Look at existing [GitHub issues](https://github.com/aniketpitre/GenAI-Honeypot/issues)
3. Create a new issue with:
   - Your operating system
   - Error messages
   - Steps to reproduce

### Want to Improve This? 💡
1. Fork the repository
2. Make your changes
3. Test thoroughly
4. Submit a pull request

### Need Help? 🆘
- **Documentation**: Read all the `.md` files in this project
- **GitHub Issues**: Ask questions or report problems
- **Community**: Share your experience and learn from others

---

## 📜 License and Legal

**Important**: This project is for **educational and research purposes only**. 

### Legal Guidelines 📋
- ✅ **DO**: Use for learning cybersecurity
- ✅ **DO**: Research attack patterns in controlled environments
- ✅ **DO**: Test security tools and defenses
- ❌ **DON'T**: Use to actually trap real attackers without legal authority
- ❌ **DON'T**: Deploy on networks you don't own
- ❌ **DON'T**: Use for malicious purposes

### Disclaimer ⚠️
The authors are not responsible for any misuse of this tool. Always follow your local laws and regulations regarding cybersecurity research.

---

## 🎉 Congratulations!

If you've made it this far, you now understand:
- What a honeypot is and why it's useful
- How AI can create realistic fake data
- How to set up a complete monitoring system
- How to analyze security data with Kibana
- How all the components work together

**You're now ready to explore the fascinating world of cybersecurity research!** 🚀

---

*Made with ❤️ for cybersecurity education and research*