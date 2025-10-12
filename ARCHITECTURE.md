# 🏗️ GenAI-Honeypot Architecture - Explained Simply

**Welcome to the technical deep-dive!** This document explains how everything works together, using simple language and visual diagrams.

## 📋 Table of Contents
1. [🎯 The Big Picture](#-the-big-picture)
2. [🧩 Component Breakdown](#-component-breakdown)
3. [🔄 Data Flow Journey](#-data-flow-journey)
4. [🐳 Docker Architecture](#-docker-architecture)
5. [🤖 AI Integration](#-ai-integration)
6. [🔧 Technical Details](#-technical-details)
7. [🚀 Scalability & Extensions](#-scalability--extensions)

---

## 🎯 The Big Picture

### Simple View: What Happens When Someone Attacks? 🎭

```
Hacker → Honeypot → Logs → Processing → Dashboard → You See It!
  ↓         ↓        ↓        ↓          ↓         ↓
Attack   Fake     Raw     Clean      Pretty    Analysis
         Server   Data    Data       Charts
```

### Real-World Analogy 🏠
Think of this like a **smart security camera system**:

1. **Camera (Honeypot)** - Watches the front door
2. **Recording Device (Filebeat)** - Saves the footage
3. **Video Processor (Logstash)** - Enhances and organizes footage
4. **Storage System (Elasticsearch)** - Keeps all videos organized
5. **Monitor Display (Kibana)** - Shows you what's happening
6. **AI Assistant (Gemini)** - Makes the scene look realistic

---

## 🧩 Component Breakdown

### 1. The Honeypot Container 🍯

**What it is**: A fake Linux server that looks real to attackers

**What's inside**:
```
Ubuntu 22.04 Container
├── SSH Server (openssh-server)     → Fake command line access
├── Web Server (nginx)              → Fake website
├── Log Service (rsyslog)           → Records everything
├── Filebeat Agent                  → Sends logs out
└── AI-Generated Data               → Makes it look real
```

**Ports exposed**:
- **Port 2223** → SSH access (fake terminal)
- **Port 80** → Web server (fake website)

**Key files**:
- `/var/log/auth.log` → Login attempts
- `/var/log/nginx/access.log` → Website visits
- `/home/sysadmin/.bash_history` → Fake user commands

### 2. Elasticsearch - The Smart Database 🗄️

**What it is**: Super-fast database that stores all log data

**Think of it like**: A librarian who can instantly find any book
- Stores millions of log entries
- Searches in milliseconds
- Automatically organizes by date/type

**Technical specs**:
- **Port**: 9200 (internal)
- **Storage**: JSON documents
- **Index pattern**: `logstash-YYYY.MM.DD`
- **Memory**: 2GB default

### 3. Logstash - The Data Processor 🏭

**What it is**: Takes messy log files and makes them clean and organized

**Process flow**:
```
Raw Log Entry → Parse → Enhance → Validate → Send to Elasticsearch
     ↓            ↓        ↓         ↓              ↓
"Failed pwd"  → Extract → Add geo → Check format → Store clean data
```

**What it does**:
- **Parses** different log formats
- **Extracts** IP addresses, usernames, timestamps
- **Enriches** with geographic data
- **Standardizes** all data formats

### 4. Kibana - The Beautiful Dashboard 📊

**What it is**: Web interface that turns data into pretty charts

**Features**:
- **Real-time dashboards** → See attacks as they happen
- **Interactive charts** → Click to zoom and filter
- **Search capabilities** → Find specific events
- **Alert systems** → Notify when things happen

**Access**: `http://localhost:5601`

### 5. Filebeat - The Log Shipper 📮

**What it is**: Watches log files and immediately sends new entries

**Like a mail carrier**:
- Monitors specific files
- Picks up new entries
- Delivers to Logstash
- Ensures nothing is lost

---

## 🔄 Data Flow Journey

### Step-by-Step: How Data Moves Through the System 🚶‍♂️

#### 1. Attack Happens 🎯
```
Hacker types: ssh root@honeypot -p 2223
```

#### 2. Honeypot Records 📝
```
SSH service logs to: /var/log/auth.log
Entry: "Oct 12 14:23:45 honeypot sshd[1234]: Failed password for root from 1.2.3.4"
```

#### 3. Filebeat Detects 👁️
```
Filebeat monitors: /var/log/auth.log
Sees new line, immediately reads it
```

#### 4. Logstash Processes 🔧
```
Input: Raw log line
Filter: Parse timestamp, IP, username, action
Output: Structured JSON document
```

#### 5. Elasticsearch Stores 💾
```
Receives JSON document
Indexes by timestamp
Makes searchable instantly
```

#### 6. Kibana Displays 📺
```
Queries Elasticsearch
Updates dashboard in real-time
Shows new attack on charts
```

### Visual Data Flow 🌊

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Attacker  │───▶│  Honeypot   │───▶│  Filebeat   │───▶│  Logstash   │
│             │    │(Logs events)│    │(Ships logs) │    │(Processes)  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                  │
┌─────────────┐    ┌─────────────┐                               │
│   Kibana    │◀───│Elasticsearch│◀──────────────────────────────┘
│ (Dashboard) │    │  (Storage)  │
└─────────────┘    └─────────────┘
```

---

## 🐳 Docker Architecture

### Container Network Design 🕸️

```
Host Machine (Your Computer)
│
├── Docker Network: genai-honeypot_default
│   │
│   ├── honeypot-test (Ubuntu container)
│   │   ├── SSH: 0.0.0.0:2223 → 22 (exposed to host)
│   │   ├── HTTP: 0.0.0.0:80 → 80 (exposed to host)
│   │   └── Internal IP: 172.20.0.2
│   │
│   ├── elasticsearch
│   │   ├── API: 9200 (internal only)
│   │   └── Internal IP: 172.20.0.3
│   │
│   ├── logstash
│   │   ├── Beats input: 5044 (internal only)
│   │   └── Internal IP: 172.20.0.4
│   │
│   └── kibana
│       ├── Web UI: 0.0.0.0:5601 → 5601 (exposed to host)
│       └── Internal IP: 172.20.0.5
│
└── Data Volumes
    ├── esdata (Elasticsearch data)
    └── generated_files (AI content)
```

### Volume Management 💾

**Persistent data storage**:
- **`esdata`** → Elasticsearch data (survives container restarts)
- **`generated_files`** → AI-created content mounted into honeypot

**Temporary data**:
- Container filesystems (reset on rebuild)
- Log files (streamed to persistent storage)

---

## 🤖 AI Integration

### How Google Gemini AI Works Here 🧠

#### 1. Persona-Based Generation 👤
```python
# persona_config.json defines the fake user
{
  "name": "John Smith",
  "role": "System Administrator",
  "company": "TechCorp Inc",
  "personality": "security-conscious, detail-oriented",
  "tools": ["bash", "vim", "htop", "fail2ban"]
}
```

#### 2. Content Generation Process 🏭
```
AI Input: Persona + Context → Google Gemini → Realistic Output

Examples:
Input: "Generate SSH failed login attempts for a web server"
Output: Realistic auth.log entries with proper timestamps,
        various attack patterns, believable IP addresses

Input: "Generate sysadmin bash history" 
Output: Realistic command sequences that a real admin would use
```

#### 3. Output Types Generated 📝

**Authentication Logs** (`/var/log/auth.log`):
- Failed SSH attempts with realistic usernames
- Successful logins with proper timing
- Geographic distribution of attack sources
- Realistic attack patterns (brute force, dictionary attacks)

**User Activity** (`.bash_history`):
- Daily administrator tasks
- Security-related commands
- System maintenance activities
- Realistic timing and sequences

**System Tasks** (`todo.txt`):
- Maintenance schedules
- Security updates
- Backup verification
- Monitoring tasks

### AI Prompt Engineering 🎯

The system uses carefully crafted prompts to ensure realistic data:

```python
prompt = f"""
Generate realistic {content_type} for a {persona['role']} at {persona['company']}.
The person is {persona['personality']}.
Include realistic timestamps, IP addresses, and technical details.
Make it look like a production system with real activity.
"""
```

---

## 🔧 Technical Details

### Security Model 🛡️

#### Network Isolation
- **Docker network isolation** → Containers can't access host directly
- **No privileged containers** → Limited system access
- **Read-only filesystems** → Where possible, prevent modification

#### Data Protection
- **No real user data** → Everything is AI-generated
- **Controlled exposure** → Only specific ports exposed
- **Log sanitization** → Remove any real system info

### Performance Specifications 📊

#### Resource Requirements
```yaml
Minimum System:
  RAM: 8GB (4GB for containers + 4GB for host)
  CPU: 2 cores
  Disk: 10GB free space
  Network: 100 Mbps

Recommended System:
  RAM: 16GB 
  CPU: 4 cores
  Disk: 50GB SSD
  Network: 1 Gbps
```

#### Container Resource Limits
```yaml
elasticsearch:
  memory: 2GB
  cpu: 1.0

logstash:
  memory: 1GB
  cpu: 0.5

kibana:
  memory: 1GB
  cpu: 0.5

honeypot:
  memory: 512MB
  cpu: 0.25
```

### Monitoring and Observability 👁️

#### Health Checks
Each service includes health monitoring:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:9200"]
  interval: 30s
  timeout: 10s
  retries: 3
```

#### Logging Strategy
- **Application logs** → Stored in Elasticsearch
- **Container logs** → Docker logging driver
- **System metrics** → Can integrate with Prometheus

---

## 🚀 Scalability & Extensions

### Horizontal Scaling 📈

#### Multiple Honeypots
```yaml
# Scale honeypots across different services
services:
  honeypot-web:
    ports: ["8080:80", "2224:22"]
  honeypot-db:
    ports: ["8081:80", "2225:22"]
  honeypot-ftp:
    ports: ["8082:80", "2226:22", "2121:21"]
```

#### Load Balancing
```yaml
nginx:
  image: nginx
  ports: ["80:80"]
  depends_on: [honeypot-web, honeypot-db]
```

### Vertical Scaling 📊

#### Elasticsearch Cluster
```yaml
elasticsearch-node1:
  environment:
    - "cluster.name=honeypot-cluster"
    - "node.name=node-1"
elasticsearch-node2:
  environment:
    - "cluster.name=honeypot-cluster"
    - "node.name=node-2"
```

### Extension Points 🔌

#### 1. Additional Services
- **FTP Honeypot** → Monitor file transfer attacks
- **Database Honeypot** → Capture SQL injection attempts
- **Email Honeypot** → Trap spam and phishing

#### 2. Enhanced AI
- **Dynamic Responses** → AI responds to commands in real-time
- **Behavioral Learning** → AI adapts based on attack patterns
- **Multi-language Support** → Generate content in different languages

#### 3. Integration Points
- **SIEM Integration** → Send alerts to security systems
- **Threat Intelligence** → Enrich data with external sources
- **API Endpoints** → Custom applications can query data

### Advanced Features 🎓

#### 1. Machine Learning Analytics
```python
# Anomaly detection pipeline
from sklearn.ensemble import IsolationForest

def detect_anomalies(log_data):
    # Identify unusual attack patterns
    # Flag suspicious behavior
    # Generate alerts
```

#### 2. Geographic Threat Mapping
```yaml
# Enhanced Logstash configuration
filter {
  geoip {
    source => "source_ip"
    target => "geoip"
  }
}
```

#### 3. Real-time Alerting
```yaml
# Watcher configuration for Elasticsearch
{
  "trigger": {
    "schedule": {"interval": "1m"}
  },
  "input": {
    "search": {
      "request": {
        "body": {
          "query": {
            "bool": {
              "filter": [
                {"range": {"@timestamp": {"gte": "now-1m"}}},
                {"match": {"message": "Failed password"}}
              ]
            }
          }
        }
      }
    }
  }
}
```

---

## 🔍 Troubleshooting Architecture

### Common Architectural Issues 🐛

#### 1. Service Dependencies
**Problem**: Services start in wrong order
**Solution**: Proper `depends_on` configuration
```yaml
kibana:
  depends_on:
    elasticsearch:
      condition: service_healthy
```

#### 2. Network Connectivity
**Problem**: Services can't communicate
**Diagnosis**:
```bash
# Check network
docker network inspect genai-honeypot_default

# Test connectivity
docker compose exec kibana ping elasticsearch
```

#### 3. Data Pipeline Breaks
**Problem**: Logs not flowing through
**Diagnosis**:
```bash
# Check each stage
docker compose logs filebeat
docker compose logs logstash
curl localhost:9200/_cat/indices
```

### Performance Tuning 🏎️

#### 1. Elasticsearch Optimization
```yaml
environment:
  - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
  - "discovery.type=single-node"
  - "xpack.security.enabled=false"
```

#### 2. Logstash Pipeline Tuning
```yaml
environment:
  - "LS_JAVA_OPTS=-Xmx512m -Xms512m"
pipeline.workers: 2
pipeline.batch.size: 125
```

---

## 📊 Architecture Metrics

### Key Performance Indicators 📈

#### System Health
- **Service uptime** → 99%+ availability target
- **Response time** → Sub-second dashboard loading
- **Throughput** → 1000+ events per second processing

#### Data Quality
- **Log coverage** → 100% of honeypot activities captured
- **Processing latency** → <5 seconds from event to dashboard
- **Data retention** → 30 days default, configurable

#### Security Effectiveness
- **Attack detection rate** → >95% of attempts logged
- **False positive rate** → <1% of legitimate traffic flagged
- **Analysis time** → Real-time processing and alerting

---

## 🎯 Conclusion

This architecture provides:

### ✅ Benefits Achieved
- **Realistic deception** through AI-generated content
- **Professional monitoring** with enterprise-grade tools
- **Scalable design** that grows with your needs
- **Educational value** for learning cybersecurity
- **Research capabilities** for threat analysis

### 🚀 Future Enhancements
- **Multi-cloud deployment** for broader threat coverage
- **Advanced AI responses** for deeper attacker engagement
- **Automated threat hunting** with machine learning
- **Integration ecosystem** with security tools

**This architecture creates a powerful, realistic, and educational cybersecurity research platform!** 🛡️✨