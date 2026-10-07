#!/usr/bin/env bash
# ===========================================================================
# Observ -- build script for Machine 2 (internal backup host)
#
# Provisions a CLEAN Ubuntu 22.04 host into the vulnerable "internal" machine.
# Run as root on the base VM template:   sudo ./build-internal.sh
#
# Build order: build M1 first, then copy the public key it emitted
# (build/out/svc_backup.pub) to  ./svc_backup.pub  next to this script.
#
# On the chain network this host must receive the static address 172.20.0.3
# on the internal segment and MUST NOT be exposed on the external segment --
# it is reachable only by pivoting through M1.
#
# Mirrors artifacts/internal/Dockerfile + provision/setup.sh.
# ===========================================================================
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/../internal"                   # artifacts/internal
PUB="$HERE/svc_backup.pub"

[ -f "$PUB" ] || { echo "ERROR: $PUB not found. Build M1 first and copy build/out/svc_backup.pub here."; exit 1; }

export DEBIAN_FRONTEND=noninteractive
echo "[build] installing packages..."
apt-get update
apt-get install -y --no-install-recommends \
    openssh-server sudo python3 iproute2 net-tools

echo "[build] configuring sshd (key auth only, no root, no password)..."
sed -i 's/#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/#\?PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config

echo "[build] creating svc_backup (no password; key login only)..."
id svc_backup >/dev/null 2>&1 || useradd -m -s /bin/bash svc_backup
passwd -l svc_backup
mkdir -p /home/svc_backup/.ssh
cp "$PUB" /home/svc_backup/.ssh/authorized_keys

echo "[build] installing sudo rule + flags..."
cp "$SRC/provision/sudoers.d/svc_backup" /etc/sudoers.d/svc_backup
echo 'OS{p1v0t3d_t0_1nt3rn4l_h0st_c3d8}' > /home/svc_backup/local.txt
echo 'OS{d0ubl3_pwn_tar_g7f0b1ns_r00t_4e90}' > /root/proof.txt

echo "[build] permissions..."
chown -R svc_backup:svc_backup /home/svc_backup/.ssh /home/svc_backup/local.txt
chmod 700 /home/svc_backup/.ssh
chmod 600 /home/svc_backup/.ssh/authorized_keys
chmod 644 /home/svc_backup/local.txt
chmod 440 /etc/sudoers.d/svc_backup
chmod 600 /root/proof.txt

echo "[build] enabling ssh on boot..."
systemctl enable ssh 2>/dev/null || true

echo "[build] M2 done."
