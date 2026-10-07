# Observ — Build Guide

How to build the two-machine **Observ** chain. Two paths are provided: the
**Docker** path (authoritative, used for all reliability testing) and the
**standalone VM** build scripts (for deployment onto VM templates).

- **Lab type:** chained-host offensive (2 VMs)
- **Difficulty:** Intermediate
- **Base OS (both hosts):** Ubuntu 22.04 LTS
- **Flags:** `local.txt` + `proof.txt` on each host (4 total)

## Submission package layout

The submission archive root contains the four required items; everything else
lives inside `artifacts.zip`:

```
<submission>.zip
├── autopwn.py          # non-interactive full-chain exploit (prints 4 flags)
├── build-guide.md      # this file
├── walkthrough.pdf     # full solution + lessons
└── artifacts.zip
     ├── README.md, credentials.txt, mitre-attack.md, test-results.txt, walkthrough.md
     ├── docker-compose.yml          # authoritative, tested build
     ├── web/ , internal/            # per-machine sources (Dockerfile, provisioning)
     └── build/build-web.sh, build-internal.sh   # standalone VM build scripts
```

## Network

| Host | Role | External segment | Internal segment |
|------|------|------------------|------------------|
| `web` (M1) | entry + pivot | yes (HTTP 80, SSH 22) | `172.20.0.2` |
| `internal` (M2) | pivot target | **none** | `172.20.0.3` |

M2 has no external interface. It is reachable only from M1. This enforces the
pivoting objective.

## Services

- **M1:** Apache + PHP (vulnerable "Observ" portal), MariaDB (local), OpenSSH.
- **M2:** OpenSSH only (key-based login for `svc_backup`).

## Build order (important)

Build **M1 first**, then **M2**. M1 mints the `svc_backup` keypair and keeps the
private key; M2 must trust the matching public key. This models the runtime key
exchange and avoids committing any private key to the package.

### Option A — Docker (authoritative, tested 15/15)

Run from the root of the unpacked `artifacts.zip`:

```bash
docker compose up --build -d      # builds + starts both machines
docker compose ps                 # confirm both Up
docker compose down -v            # tear down (also clears the pivot key volume)
```

M1 is published on the host at `127.0.0.1:80` (web) and `127.0.0.1:2222` (SSH).
The pivot keypair is generated at runtime by M1's entrypoint and shared to M2
through a Docker volume (`/pivot`).

### Option B — Standalone VM build scripts

Run on two clean Ubuntu 22.04 templates, as root (paths relative to the
unpacked `artifacts.zip`):

```bash
# on M1:
sudo build/build-web.sh
#   -> emits build/out/svc_backup.pub

# copy that public key to M2, next to build-internal.sh, then on M2:
sudo build/build-internal.sh
```

Assign the internal addresses (`172.20.0.2` / `172.20.0.3`) on the internal
segment and ensure M2 has **no** external NIC.

## Flag placement

| Host | User flag | Root flag |
|------|-----------|-----------|
| M1 `web` | `/home/developer/local.txt` | `/root/proof.txt` |
| M2 `internal` | `/home/svc_backup/local.txt` | `/root/proof.txt` |

(Difficulty per proof/flag is set in the submission form; points are derived by
the platform.)

## Verifying the build

From an attacker with `curl`, `ssh`, `sshpass`, `python3` (autopwn.py is at the
package root):

```bash
./autopwn.py <M1_IP> 80 22        # Docker on host: ./autopwn.py 127.0.0.1 80 2222
```

A clean build prints all four `OBSERV{...}` flags and exits 0. The full
reliability harness (`tools/reliability-test.sh 15`) redeploys clean 15 times
and requires 15/15 — see `test-results.txt`.

## Software / CVE note

The chain is built from **configuration and logic vulnerabilities** (SQLi,
OS command injection, credential reuse, two sudo misconfigurations, a leaked
key, and network pivoting) rather than a pinned CVE in third-party software, so
there is no out-of-date-CVE concern. All techniques map to current MITRE
ATT&CK entries (see `mitre-attack.md`).

## AI-Resistance (AI-R)

The intended path is not a single well-known CVE with a copy-paste public
exploit. Solving requires chaining independent findings and — critically —
recognising that the `netcheck` import is hijackable **only** because the real
module lives in site-packages while `PYTHONPATH` is preserved across `sudo`
(a reasoning step, not a signature), then pivoting across an isolated network
segment to a host an automated single-target tool cannot even see.
