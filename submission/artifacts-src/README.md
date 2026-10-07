# Observ — UGC Submission Package

Chained-host offensive lab (2 machines, pivoting) for the OffSec UGC program.

- **Name:** Observ
- **Type:** Chained-host offensive VM lab (2 hosts)
- **Difficulty:** Intermediate
- **Flags:** 4 (`local.txt` + `proof.txt` on each host)
- **Reliability:** 15/15 clean-redeploy autopwn runs (see `test-results.txt`)

## Package contents

The archive root holds the four required items (`autopwn.py`, `build-guide.md`,
`walkthrough.pdf`, `artifacts.zip`). This README and the remaining material live
inside `artifacts.zip`:

| File / dir | Purpose |
|------------|---------|
| `autopwn.py` *(root)* | non-interactive full-chain exploit; prints all four flags |
| `build-guide.md` *(root)* | how to build both machines (Docker + standalone VM scripts) |
| `walkthrough.pdf` *(root)* | PDF rendering of the walkthrough |
| `README.md` | this overview |
| `walkthrough.md` | full official solution, with a Lessons section |
| `credentials.txt` | every username/password on the chain |
| `mitre-attack.md` | MITRE ATT&CK mapping for each stage |
| `test-results.txt` | reliability ("15x15") test evidence |
| `docker-compose.yml`, `web/`, `internal/`, `build/` | all source + build scripts |

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
# from the root of the unpacked artifacts.zip:
docker compose up --build -d                 # build + run both machines
../autopwn.py 127.0.0.1 80 2222              # solve + print 4 flags
docker compose down -v                        # tear down
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
