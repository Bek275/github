#!/bin/bash
# Build-time provisioning for Machine 1 (web / pivot host). Lab use only.
set -e

echo "[setup] creating users..."
# Low-priv service/dev account. Password is reused from the app DB config.
useradd -m -s /bin/bash developer
echo 'developer:Pr0dDbAcc3ss!2023' | chpasswd

echo "[setup] placing web files..."
chown -R www-data:www-data /var/www/html
find /var/www/html -type d -exec chmod 755 {} \;
find /var/www/html -type f -exec chmod 644 {} \;

echo "[setup] placing privesc target..."
# The legitimate helper lives in site-packages, NOT next to check.py. Because
# Python searches the script's own directory before PYTHONPATH, keeping
# netcheck.py out of /opt/health is what makes the PYTHONPATH hijack possible.
SITE_PKGS=$(python3 -c 'import sys; print([p for p in sys.path if p.endswith("dist-packages")][0])')
mv /opt/health/netcheck.py "$SITE_PKGS/netcheck.py"
chown root:root "$SITE_PKGS/netcheck.py"
chmod 644 "$SITE_PKGS/netcheck.py"
chown -R root:root /opt/health
chmod 755 /opt/health
chmod 755 /opt/health/check.py
chmod 440 /etc/sudoers.d/developer

echo "[setup] placing developer loot (flag, notes, ssh config)..."
# NOTE: the svc_backup private key is minted at runtime by the entrypoint and
# dropped into ~/.ssh/svc_backup_id_ed25519 (no key is baked into the image).
mkdir -p /home/developer/.ssh
mv /home/developer_local.txt /home/developer/local.txt
cat > /home/developer/.ssh/config <<'EOF'
# Internal maintenance hosts
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
chown -R developer:developer /home/developer
chmod 700 /home/developer/.ssh
chmod 644 /home/developer/local.txt

echo "[setup] placing root flag..."
echo 'OS{m1_r00t_pyth0np4th_h1j4ck_a71d}' > /root/proof.txt
chmod 600 /root/proof.txt

echo "[setup] seeding MariaDB..."
mkdir -p /var/run/mysqld
chown -R mysql:mysql /var/run/mysqld /var/lib/mysql
mariadb-install-db --user=mysql --datadir=/var/lib/mysql >/dev/null 2>&1 || true
mysqld_safe --skip-networking=0 &
for i in $(seq 1 30); do
    mysqladmin ping --silent 2>/dev/null && break
    sleep 1
done
mysql < /provision/db-init.sql
mysqladmin shutdown 2>/dev/null || true
sleep 2

echo "[setup] done."
