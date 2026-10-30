# Honeypot sensor: SSH + web lure. Contains NO secrets and NO log shipper;
# logs go to /var/log/honeypot, which a Filebeat sidecar reads.
FROM ubuntu:25.10

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
        openssh-server nginx-light rsyslog ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/run/sshd /var/log/honeypot && \
    useradd -m -s /bin/bash sysadmin

COPY sshd_honeypot.conf /etc/ssh/sshd_config.d/honeypot.conf
COPY rsyslog.conf /etc/rsyslog.conf
COPY nginx-honeypot.conf /etc/nginx/conf.d/honeypot.conf
COPY site/ /var/www/html/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && rm -f /etc/nginx/sites-enabled/default

EXPOSE 22 80
VOLUME ["/var/log/honeypot"]
ENTRYPOINT ["/entrypoint.sh"]
