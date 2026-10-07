#!/bin/bash
# Build-time provisioning for Machine 2 (internal backup host). Lab use only.
set -e

echo "[setup] creating svc_backup..."
useradd -m -s /bin/bash svc_backup
# No password login; access is via the SSH key leaked on Machine 1.
passwd -l svc_backup

echo "[setup] preparing .ssh (authorized_keys installed at runtime)..."
# The authorized key is provided by M1 at runtime via the shared /pivot volume;
# the entrypoint installs it. No key material is baked into this image.
mkdir -p /home/svc_backup/.ssh
chown -R svc_backup:svc_backup /home/svc_backup/.ssh
chmod 700 /home/svc_backup/.ssh

chmod 440 /etc/sudoers.d/svc_backup

echo "[setup] placing flags..."
echo 'OS{p1v0t3d_t0_1nt3rn4l_h0st_c3d8}' > /home/svc_backup/local.txt
chown svc_backup:svc_backup /home/svc_backup/local.txt
chmod 644 /home/svc_backup/local.txt

echo 'OS{d0ubl3_pwn_tar_g7f0b1ns_r00t_4e90}' > /root/proof.txt
chmod 600 /root/proof.txt

echo "[setup] done."
