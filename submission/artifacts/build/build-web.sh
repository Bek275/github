#!/usr/bin/env bash
# ===========================================================================
# Observ -- build script for Machine 1 (web / pivot host)
#
# Provisions a CLEAN Ubuntu 22.04 host into the vulnerable "web" machine.
# Run as root on the base VM template:   sudo ./build-web.sh
#
# Build order for the chain: build M1 FIRST. This script emits the
# svc_backup public key to  ./out/svc_backup.pub  -- copy that file next to
# build-internal.sh before building M2 (mirrors the runtime key exchange).
#
# This mirrors artifacts/web/Dockerfile + provision/setup.sh exactly; the
# Docker build in ../ is the authoritative, tested reference.
# ===========================================================================
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/../web"                       # artifacts/web

export DEBIAN_FRONTEND=noninteractive
echo "[build] installing packages..."
apt-get update
apt-get install -y --no-install-recommends \
    apache2 libapache2-mod-php php php-mysql \
    mariadb-server mariadb-client openssh-server sudo python3 \
    iputils-ping iproute2 net-tools curl ca-certificates

echo "[build] hardening/relaxing sshd (password auth on, no root)..."
sed -i 's/#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config

echo "[build] deploying web application..."
rm -f /var/www/html/index.html
cp -r "$SRC/src/." /var/www/html/

echo "[build] deploying privesc target..."
mkdir -p /opt/health
cp "$SRC/provision/opt/health/check.py" /opt/health/check.py
SITE_PKGS=$(python3 -c 'import sys; print([p for p in sys.path if p.endswith("dist-packages")][0])')
cp "$SRC/provision/opt/health/netcheck.py" "$SITE_PKGS/netcheck.py"
cp "$SRC/provision/sudoers.d/developer" /etc/sudoers.d/developer

echo "[build] creating developer (password reused from DB config)..."
id developer >/dev/null 2>&1 || useradd -m -s /bin/bash developer
echo 'developer:Pr0dDbAcc3ss!2023' | chpasswd

echo "[build] placing flags, notes, ssh config..."
mkdir -p /home/developer/.ssh
cp "$SRC/provision/local.txt" /home/developer/local.txt
cat > /home/developer/.ssh/config <<'EOF'
Host backup-internal
    HostName 172.20.0.3
    User svc_backup
    IdentityFile ~/.ssh/svc_backup_id_ed25519
EOF
cat > /home/developer/notes.txt <<'EOF'
TODO (devops):
- The internal backup host (backup-internal, 172.20.0.3) is only reachable
  from this box. Use the svc_backup key in ~/.ssh to jump there.
- Rotate the shared DB/login password once ticket OPS-412 is done.
EOF
echo 'OBSERV{m1_r00t_pyth0np4th_h1j4ck_a71d}' > /root/proof.txt
chmod 600 /root/proof.txt

echo "[build] minting pivot keypair (private key -> developer, public -> ./out)..."
KEY=/home/developer/.ssh/svc_backup_id_ed25519
[ -f "$KEY" ] || ssh-keygen -t ed25519 -N '' -C 'svc_backup@observ-internal' -f "$KEY" >/dev/null
mkdir -p "$HERE/out"; cp "$KEY.pub" "$HERE/out/svc_backup.pub"

echo "[build] permissions..."
chown -R www-data:www-data /var/www/html
find /var/www/html -type d -exec chmod 755 {} \;
find /var/www/html -type f -exec chmod 644 {} \;
chown -R root:root /opt/health; chmod 755 /opt/health /opt/health/check.py
chmod 440 /etc/sudoers.d/developer
chown -R developer:developer /home/developer
chmod 700 /home/developer/.ssh; chmod 600 "$KEY"; chmod 644 /home/developer/local.txt

echo "[build] seeding MariaDB..."
service mariadb start 2>/dev/null || (mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld && mysqld_safe & sleep 8)
for i in $(seq 1 30); do mysqladmin ping --silent 2>/dev/null && break; sleep 1; done
mysql < "$SRC/provision/db-init.sql"

echo "[build] enabling services on boot..."
systemctl enable apache2 mariadb ssh 2>/dev/null || true

echo "[build] M1 done. Copy ./out/svc_backup.pub next to build-internal.sh."
