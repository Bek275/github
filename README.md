# Observ — OffSec-style Vulnerable Lab (with pivoting)

A deliberately vulnerable, Docker-based penetration-testing lab in the style of
OffSec Proving Grounds / OSCP practice machines. It is a **two-machine network
pivoting** scenario: you compromise an internet-facing web host, then pivot
through it to reach and root an internal host that is not directly reachable.

> ⚠️ **Ethical / legal notice**
> Every host in this lab is **intentionally insecure**. It exists only for
> **authorized security training and CTF practice**. Run it on an isolated host
> on a lab network. **Never** expose it to an untrusted network or the public
> internet, and only attack systems you own or are explicitly authorized to test.

---

## Topology

```
   attacker (your host)
          │  http://127.0.0.1   ssh 127.0.0.1:2222
          ▼
   ┌──────────────┐          ┌──────────────────┐
   │  web  (M1)   │   int    │  internal  (M2)  │
   │ 172.20.0.2   │─────────▶│   172.20.0.3     │
   │ ext + int    │  only    │   int only       │
   └──────────────┘          └──────────────────┘
```

- **Machine 1 — `web`** is reachable from your host (ports 80 and 2222→22) and
  sits on both the external and internal networks. It is your foothold and your
  pivot point.
- **Machine 2 — `internal`** has **no published ports**. It lives only on the
  `172.20.0.0/24` internal network and can be reached **only by pivoting through
  Machine 1**. That is the core exercise.

## Difficulty

Intermediate. The full compromise is a chain of six distinct techniques across
two hosts (web exploitation, credential reuse, two different privilege
escalations, and a network pivot).

## Requirements

- Docker + Docker Compose
- An attacking toolkit on your host (nmap, curl/Burp, gobuster, an SSH client,
  and a pivoting tool such as OpenSSH `-J`/`-D`, `proxychains`, `chisel`, or
  `sshuttle`).

## Build & run

```bash
docker compose up --build -d     # build + start both machines
docker compose ps                # confirm both are up
docker compose down              # stop & remove when finished
```

Then point your tools at the target:

| Service        | Address                |
|----------------|------------------------|
| Web (M1)       | `http://127.0.0.1`     |
| SSH (M1)       | `127.0.0.1:2222`       |
| Internal (M2)  | not directly reachable |

## Flags

OffSec convention — two flags **per host**:

| Host           | User flag               | Root flag               |
|----------------|-------------------------|-------------------------|
| `web` (M1)     | `/home/developer/local.txt` | `/root/proof.txt`   |
| `internal` (M2)| `/home/svc_backup/local.txt`| `/root/proof.txt`   |

Each flag is an `OS{...}` token.

## Repository layout

```
.
├── docker-compose.yml        # two services + two networks (the pivot topology)
├── web/                      # Machine 1 — web / pivot host
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── src/                  # the vulnerable PHP monitoring portal
│   └── provision/            # users, DB seed, sudo/privesc target, loot, flags
├── internal/                 # Machine 2 — internal backup host (pivot target)
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── provision/            # svc_backup key, sudo rule, flags
└── WALKTHROUGH.md            # full official solution (spoilers)
```

## Intended path (no spoilers)

1. Enumerate M1's web service and get a foothold through it.
2. Escalate to a regular user, then to root on M1.
3. Discover the second network and the internal host from M1.
4. Pivot through M1 to reach M2.
5. Get a foothold on M2 and escalate to root.

The complete step-by-step solution is in [`WALKTHROUGH.md`](./WALKTHROUGH.md).
