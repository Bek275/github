#!/bin/bash
# Runtime entrypoint for Machine 1 (web / pivot host).
set -e

mkdir -p /var/run/mysqld /var/run/sshd
chown -R mysql:mysql /var/run/mysqld

echo "[entrypoint] provisioning pivot keypair..."
# Mint a throwaway keypair once per volume lifetime. The private key is dropped
# into developer's home (the "leaked" key); the public key is shared with M2 via
# the /pivot volume. Nothing secret is ever stored in the image or the repo.
KEY=/home/developer/.ssh/svc_backup_id_ed25519
if [ ! -f "$KEY" ]; then
    ssh-keygen -t ed25519 -N '' -C 'svc_backup@observ-internal' -f "$KEY" >/dev/null
    chown developer:developer "$KEY" "$KEY.pub"
    chmod 600 "$KEY"
fi
mkdir -p /pivot
cp "$KEY.pub" /pivot/authorized_keys
chmod 644 /pivot/authorized_keys

echo "[entrypoint] starting MariaDB..."
mysqld_safe --skip-networking=0 &
for i in $(seq 1 30); do
    mysqladmin ping --silent 2>/dev/null && break
    sleep 1
done

echo "[entrypoint] starting SSH..."
/usr/sbin/sshd

echo "[entrypoint] starting Apache (foreground)..."
. /etc/apache2/envvars
exec /usr/sbin/apache2ctl -DFOREGROUND
