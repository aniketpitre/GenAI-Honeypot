# GenAI-Honeypot 🕵️‍♂️🧑‍💻🚨

## Overview

GenAI-Honeypot is an advanced, AI-powered honeypot system designed to simulate a realistic Linux web server environment. It uses Google Gemini generative AI to create authentic system files, logs, and user activity, making it highly convincing to attackers and penetration testers.

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

3. **Service Startup**  
	 Nginx and SSHD are started automatically.  
	 Generated files are copied into the container and permissions set.

4. **Activity Simulation**  
	 Background scripts (optional) can update logs and histories to simulate ongoing activity.

5. **Security Analysis**  
	 Allows attacker-like actions (e.g., reading `/etc/shadow`, privilege escalation) for realism.  
	 Can be extended to log or alert on suspicious actions.

---

## How to Run 🏁

1. **Clone the Repository**
	 ```bash
	 git clone https://github.com/aniketpitre/GenAI-Honeypot.git
	 cd GenAI-Honeypot
	 ```

2. **Set Your Gemini API Key and Build**
	 ```bash
	 export GEMINI_API_KEY=your_gemini_api_key
	 bash build_and_run.sh
	 ```
	 This will build the Docker image, generate files, and start the honeypot container.

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

5. **Test Security and Monitoring**
	 - Try attacker commands:
		 ```bash
		 docker exec honeypot-test cat /etc/shadow
		 docker exec honeypot-test whoami
		 ```
	 - Check logs for suspicious activity.

---

## Working Functionality ⚙️

- **Authentic Environment:**  
	Mimics a real Debian web server with plausible user and attacker activity.
- **AI-Generated Content:**  
	Uses Gemini API to create files that evolve over time.
- **Service Exposure:**  
	SSH and web server are accessible for real interaction and testing.
- **Extensible Monitoring:**  
	Can be enhanced with adaptive response scripts and stealth monitoring.

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
- Implement adaptive response scripts for stealth monitoring and alerting.
- Integrate with SIEM or security dashboards for real-time detection.

---

## License 📄

MIT License

---

## Author

Created by [aniketpitre](https://github.com/aniketpitre)