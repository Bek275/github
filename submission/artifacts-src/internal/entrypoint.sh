#!/bin/bash
# Runtime entrypoint for Machine 2 (internal backup host).
set -e
mkdir -p /var/run/sshd

echo "[entrypoint] waiting for pivot public key from M1..."
for i in $(seq 1 60); do
    [ -f /pivot/authorized_keys ] && break
    sleep 1
done

if [ -f /pivot/authorized_keys ]; then
    install -o svc_backup -g svc_backup -m 600 \
        /pivot/authorized_keys /home/svc_backup/.ssh/authorized_keys
    echo "[entrypoint] authorized_keys installed for svc_backup."
else
    echo "[entrypoint] WARNING: pivot key never appeared; svc_backup login will fail."
fi

echo "[entrypoint] starting SSH (foreground)..."
exec /usr/sbin/sshd -D
