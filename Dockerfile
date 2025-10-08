FROM ubuntu:22.04

ARG GEMINI_API_KEY
ENV GEMINI_API_KEY=${GEMINI_API_KEY}

RUN apt-get update && \
    apt-get install -y python3 python3-pip openssh-server && \
    mkdir -p /var/run/sshd /home/sysadmin /var/log && \
    useradd -m sysadmin && echo 'sysadmin:sysadmin' | chpasswd && \
    echo 'root:root' | chpasswd && \
    echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config && \
    echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

COPY requirements.txt /tmp/requirements.txt
COPY persona_config.json /tmp/persona_config.json
COPY generation_script.py /tmp/generation_script.py

RUN pip3 install --no-cache-dir -r /tmp/requirements.txt


COPY generated_files/var/log/auth.log /var/log/auth.log
COPY generated_files/home/sysadmin/.bash_history /home/sysadmin/.bash_history
COPY generated_files/home/sysadmin/todo.txt /home/sysadmin/todo.txt
RUN chmod 644 /var/log/auth.log /home/sysadmin/.bash_history /home/sysadmin/todo.txt

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
