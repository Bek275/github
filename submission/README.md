# Observ — UGC Submission Package

Chained-host offensive lab (2 machines, pivoting) for the OffSec UGC program.

- **Name:** Observ
- **Type:** Chained-host offensive VM lab (2 hosts)
- **Difficulty:** Intermediate
- **Flags:** 4 (`local.txt` + `proof.txt` on each host)
- **Reliability:** 15/15 clean-redeploy autopwn runs (see `test-results.txt`)

## Package contents

| File / dir | Purpose |
|------------|---------|
| `README.md` | this overview |
| `build-guide.md` | how to build both machines (Docker + standalone VM scripts) |
| `walkthrough.md` | full official solution, with a Lessons section |
| `walkthrough.pdf` | PDF rendering of the walkthrough |
| `autopwn.sh` | non-interactive full-chain exploit; prints all four flags |
| `credentials.txt` | every username/password on the chain |
| `mitre-attack.md` | MITRE ATT&CK mapping for each stage |
| `test-results.txt` | reliability ("15x15") test evidence |
| `artifacts/` | all source: web app, provisioning, Dockerfiles, build scripts |

## The chain at a glance

```
attacker ──► web (M1)  ──pivot──►  internal (M2)
             ext + int             int only (172.20.0.3)
```

1. **M1** SQLi auth bypass → OS command injection (`www-data`) → credential
   reuse (`developer`) → `sudo` + PYTHONPATH hijack (`root`).
2. **Pivot** via a leaked SSH key to the internal-only host.
3. **M2** key-based SSH (`svc_backup`) → `sudo tar` GTFOBins (`root`).

## Quick build & verify

```bash
cd artifacts && docker compose up --build -d      # build + run
./autopwn.sh 127.0.0.1 80 2222                     # solve + print 4 flags
cd .. && docker compose -f artifacts/docker-compose.yml down -v
```

## Notes for reviewers

- All vulnerabilities are configuration/logic based (SQLi, command injection,
  credential reuse, two sudo misconfigurations, a leaked key, pivoting). No
  out-of-date third-party CVE is relied upon.
- The pivot keypair is generated at build/deploy time; **no private key is
  shipped** in this package.
- Two **distinct** privilege-escalation techniques; the internal host is
  unreachable without pivoting through the entry host.
- This is intentionally vulnerable software for authorized training only.
