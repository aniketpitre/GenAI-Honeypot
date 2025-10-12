FROM ubuntu:22.04

ARG GEMINI_API_KEY
ENV GEMINI_API_KEY=${GEMINI_API_KEY}


RUN apt-get update && \
    apt-get install --no-install-recommends -y python3 python3-pip openssh-server nginx-full wget rsyslog && \
    mkdir -p /var/run/sshd /home/sysadmin /var/log && \
    useradd -m sysadmin && echo 'sysadmin:sysadmin' | chpasswd && \
    echo 'root:toor' | chpasswd && \
    echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config && \
    echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config && \
    echo 'AllowUsers sysadmin root admin' >> /etc/ssh/sshd_config && \
    echo 'SyslogFacility AUTH' >> /etc/ssh/sshd_config && \
    echo 'LogLevel VERBOSE' >> /etc/ssh/sshd_config && \
    echo 'UsePAM yes' >> /etc/ssh/sshd_config && \
    wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-8.14.0-amd64.deb && \
    dpkg -i filebeat-8.14.0-amd64.deb && \
    rm filebeat-8.14.0-amd64.deb

COPY requirements.txt /tmp/requirements.txt
COPY persona_config.json /tmp/persona_config.json
COPY generation_script.py /tmp/generation_script.py

COPY filebeat/filebeat.yml /etc/filebeat/filebeat.yml
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN pip3 install --no-cache-dir -r /tmp/requirements.txt


COPY generated_files/home/sysadmin/.bash_history /home/sysadmin/.bash_history
COPY generated_files/home/sysadmin/todo.txt /home/sysadmin/todo.txt
RUN chmod 644 /home/sysadmin/.bash_history /home/sysadmin/todo.txt

EXPOSE 22 80
# Avoid exposing Docker-specific environment variables
ENV DOCKER_HIDE=1
ENTRYPOINT ["/entrypoint.sh"]
