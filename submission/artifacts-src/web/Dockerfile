# ---------------------------------------------------------------------------
# "Observ" lab -- Machine 1 (web / pivot host): foothold + first privesc.
#
# WARNING: DELIBERATELY INSECURE. Authorized security training / CTF only.
# Never expose to an untrusted network or the public internet.
# ---------------------------------------------------------------------------
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        apache2 libapache2-mod-php php php-mysql \
        mariadb-server mariadb-client \
        openssh-server sudo python3 \
        iputils-ping iproute2 net-tools curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/run/sshd \
    && sed -i 's/#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config \
    && sed -i 's/#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Web application
RUN rm -f /var/www/html/index.html
COPY src/ /var/www/html/

# Privilege-escalation target (sudo + python health check) and sudo rule
COPY provision/opt/health/ /opt/health/
COPY provision/sudoers.d/developer /etc/sudoers.d/developer

# Flag
COPY provision/local.txt /home/developer_local.txt

# Provisioning
COPY provision/setup.sh /provision/setup.sh
COPY provision/db-init.sql /provision/db-init.sql
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /provision/setup.sh /entrypoint.sh && /provision/setup.sh

EXPOSE 22 80
ENTRYPOINT ["/entrypoint.sh"]
