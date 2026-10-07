# ---------------------------------------------------------------------------
# "Observ" lab -- Machine 2 (internal backup host): pivot target + final root.
#
# Reachable ONLY from Machine 1 (no published ports). Authorized lab use only.
# ---------------------------------------------------------------------------
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-server sudo python3 \
        iproute2 net-tools \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/run/sshd \
    && sed -i 's/#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config \
    && sed -i 's/#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config \
    && sed -i 's/#\?PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config

COPY provision/sudoers.d/svc_backup /etc/sudoers.d/svc_backup
COPY provision/setup.sh /provision/setup.sh
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /provision/setup.sh /entrypoint.sh && /provision/setup.sh

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
