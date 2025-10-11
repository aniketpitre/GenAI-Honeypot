# GenAI-Honeypot 🕵️‍♂️🧑‍💻🚨 (v1.1)

## Overview

GenAI-Honeypot is an advanced, AI-powered honeypot system designed to simulate a realistic Linux web server environment. It uses Google Gemini generative AI to create authentic system files, logs, and user activity, making it highly convincing to attackers and penetration testers.

New in v1.1: a full Elastic Stack (Elasticsearch, Logstash, Kibana) setup via docker-compose. The honeypot ships its container logs to Logstash (GELF), gets indexed into Elasticsearch, and visualized in Kibana—with dashboards you can embed directly in your app.

### Key Features

- **Realistic System Simulation** 🖥️  
	Generates believable log files, bash histories, and sysadmin to-do lists using generative AI.
- **Service Emulation** 🔒🌐  
	Runs SSH and Nginx web server inside a Docker container, exposing ports for real interaction.
- **Activity Simulation** 🔄  
	Periodically updates files to mimic ongoing sysadmin and attacker activity.
- **Stealth Monitoring** 👀  
	(Optional) Can be extended to log suspicious actions or trigger alerts for attacker behaviors.
- **Easy Deployment** 🚀  
	One-command setup using Docker and environment variables.

---

## How It Works

1. **File Generation**  
	 Uses `generation_script.py` and Gemini API to create `/var/log/auth.log`, `.bash_history`, and `todo.txt` based on prompts in `persona_config.json`.  
	 Files are placed in realistic locations inside the container.

2. **Containerized Environment**  
	 Dockerfile sets up Ubuntu 22.04 with Python, OpenSSH, and Nginx.  
	 Creates `sysadmin` and `root` users with known credentials for testing.  
	 Exposes SSH (port 2223) and HTTP (port 80) for external access.

3. **Centralized Logging (ELK)**  
	 Docker Compose launches Elasticsearch, Logstash, Kibana, and the honeypot together.  
	 Honeypot logs are shipped to Logstash via GELF UDP and indexed into Elasticsearch.  
	 Kibana provides live dashboards at http://localhost:5601.

3. **Service Startup**  
	 Nginx and SSHD are started automatically.  
	 Generated files are copied into the container and permissions set.

4. **Activity Simulation**  
	 Background scripts (optional) can update logs and histories to simulate ongoing activity.

5. **Security Analysis**  
	 Allows attacker-like actions (e.g., reading `/etc/shadow`, privilege escalation) for realism.  
	 Can be extended to log or alert on suspicious actions.

---

## How to Run 🏁 (v1.1)

1. **Clone the Repository**
	 ```bash
	 git clone https://github.com/aniketpitre/GenAI-Honeypot.git
	 cd GenAI-Honeypot
	 ```

2. **Set Your Gemini API Key and Start the Stack**
	 ```bash
	 export GEMINI_API_KEY=your_gemini_api_key
	 bash build_and_run.sh
	 ```
	 This generates AI artifacts and starts Elasticsearch (9200), Kibana (5601), Logstash (12201/udp), and the honeypot (2223, 80) via docker-compose.

3. **Access the Honeypot**
	 - **SSH:**  
		 ```bash
		 ssh sysadmin@localhost -p 2223
		 # Password: sysadmin

		 ssh root@localhost -p 2223
		 # Password: toor
		 ```
	 - **Web Server:**  
		 Open your browser at [http://localhost:80](http://localhost:80) or run:
		 ```bash
		 curl http://localhost:80
		 ```

4. **Inspect Generated Files**
	 - Inside the container:
		 ```bash
		 docker exec honeypot-test cat /var/log/auth.log
		 docker exec honeypot-test cat /home/sysadmin/.bash_history
		 docker exec honeypot-test cat /home/sysadmin/todo.txt
		 ```

5. **View Dashboards (Kibana)**
	 - Open Kibana: http://localhost:5601
	 - Create a data view (index pattern) matching `honeypot-*` and build dashboards (e.g., failed SSH attempts, accepted logins, IP distribution).

6. **Test Security and Monitoring**
	 - Try attacker commands:
		 ```bash
		 docker exec honeypot-test cat /etc/shadow
		 docker exec honeypot-test whoami
		 ```
	 - Check Kibana Discover and dashboards for incoming events.

---

## Working Functionality ⚙️

- **Authentic Environment:**  
	Mimics a real Debian web server with plausible user and attacker activity.
- **AI-Generated Content:**  
	Uses Gemini API to create files that evolve over time.
- **Service Exposure:**  
	SSH and web server are accessible for real interaction and testing.
- **Centralized Monitoring:**  
	All container logs flow to ELK; build dashboards in Kibana and embed them.

---

## Credentials & Ports 🔑

- **SSH:**  
	- User: `sysadmin` / Password: `sysadmin`
	- User: `root` / Password: `toor`
	- Port: `2223`
- **Web:**  
	- Port: `80`

---

## Extending the Honeypot 🛠️

- Add more AI-generated files or prompts in `persona_config.json`.
- Implement adaptive response scripts inside the container or ship simulator logs to Logstash (Beats/GELF).
- Integrate with SIEM or security dashboards for real-time detection.

---

## Embedding Kibana in Your App (Step 5)

1. In Kibana, open your dashboard and click Share → Embed code → Iframe.
2. Copy the `<iframe>` snippet.
3. Paste it into your React app where alerts were listed.
4. Ensure Kibana is accessible from the browser where your React app runs (CORS/Content Security Policy may apply).

Tip: For production, consider securing Kibana and proxying it through your app domain.

---

## License 📄

MIT License

---

## Author

Created by [aniketpitre](https://github.com/aniketpitre)