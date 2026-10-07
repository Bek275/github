#!/usr/bin/env bash
# ===========================================================================
# Observ -- reliability / determinism test ("15x15")
#
# OffSec requires that proofs and the walkthrough be verified on a CLEAN
# redeploy. This harness operationalises that: it redeploys the whole lab from
# scratch N times and runs the full autopwn each time. A submission is only
# deployment-ready if autopwn succeeds on EVERY redeploy (N/N).
#
# "Clean redeploy" = `docker compose down -v` (drops containers + the pivot
# key volume + DB state) followed by `docker compose up -d` (fresh containers,
# freshly minted pivot keypair, fresh database seed).
#
# Usage:   tools/reliability-test.sh [N]        (default N = 15)
# ===========================================================================
set -u
cd "$(dirname "$0")/.."                      # repo root

RUNS="${1:-15}"
PROJECT="$(basename "$PWD")"                 # compose project name
EXTNET="${PROJECT}_ext"
ATTACKER_IMG="observ-attacker:latest"

log()  { printf '\033[1;34m[*]\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m[+]\033[0m %s\n' "$*"; }
err()  { printf '\033[1;31m[-]\033[0m %s\n' "$*"; }

log "building attacker image ..."
docker build -q -t "$ATTACKER_IMG" -f tools/Dockerfile.attacker tools >/dev/null

log "building lab images ..."
docker compose build -q >/dev/null

PASS=0; FAIL=0; RESULTS=()
START=$(date +%s)

for n in $(seq 1 "$RUNS"); do
    printf '\n\033[1;33m===== redeploy %s/%s =====\033[0m\n' "$n" "$RUNS"

    docker compose down -v --remove-orphans >/dev/null 2>&1
    docker compose up -d >/dev/null 2>&1

    # M1's address on the external (attacker-facing) network
    M1_IP=$(docker inspect -f \
      "{{(index .NetworkSettings.Networks \"$EXTNET\").IPAddress}}" observ-web 2>/dev/null)
    if [ -z "$M1_IP" ]; then err "run $n: could not find M1 ext IP"; FAIL=$((FAIL+1)); RESULTS+=("X"); continue; fi

    # run the full chain from the attacker container on the ext network
    OUT=$(docker run --rm --network "$EXTNET" -v "$PWD/submission:/opt:ro" \
            "$ATTACKER_IMG" -c "python3 /opt/autopwn.py $M1_IP 80 22" 2>&1)
    FLAGS=$(printf '%s\n' "$OUT" | grep -c 'OBSERV{')

    if printf '%s\n' "$OUT" | grep -q 'ALL FOUR FLAGS CAPTURED' && [ "$FLAGS" -ge 4 ]; then
        ok "run $n: PASS (4/4 flags)"; PASS=$((PASS+1)); RESULTS+=(".")
    else
        err "run $n: FAIL"; printf '%s\n' "$OUT" | tail -15; FAIL=$((FAIL+1)); RESULTS+=("X")
    fi
done

docker compose down -v --remove-orphans >/dev/null 2>&1
END=$(date +%s)

echo
echo "================= RELIABILITY RESULT ================="
printf 'matrix : [%s]\n' "$(IFS=''; echo "${RESULTS[*]}")"
printf 'passed : %s/%s\n' "$PASS" "$RUNS"
printf 'failed : %s/%s\n' "$FAIL" "$RUNS"
printf 'time   : %ss\n' "$((END-START))"
echo "======================================================"

if [ "$PASS" -eq "$RUNS" ]; then
    ok "${RUNS}/${RUNS} -- deterministic, deployment-ready"
    exit 0
else
    err "NOT deployment-ready: ${FAIL} failing redeploy(s)"
    exit 1
fi
