# Observ — UGC Submission (Chain / Attack)

Chained-host offensive lab, 2 machines, with mandatory pivoting.

- **Name:** Observ
- **Lab type:** VM Submission → Chain → Attack
- **CVE-based:** No (configuration/logic vulnerabilities)
- **Difficulty:** Intermediate
- **Machines:** 2 (`web` entry/pivot, `internal` pivot target)
- **Flags:** 4 — `local.txt` + `proof.txt` on each host (format `OS{...}`)
- **Reliability:** autopwn succeeds on 15/15 clean redeploys

## Package root (this archive)

| File | Purpose |
|------|---------|
| `autopwn.py` | non-interactive full-chain exploit; prints all four flags |
| `build-guide.md` | machine ordering, networking, build steps |
| `walkthrough.pdf` | full official solution + lessons |
| `artifacts.zip` | all source, build scripts and supporting docs |
| `readme.md` | this file |

## Chain

```
attacker ──► web (M1)  ──pivot──►  internal (M2, 172.20.0.3, internal-only)
```

1. **M1** SQLi auth bypass → OS command injection (`www-data`) → credential
   reuse (`developer`) → `sudo` + PYTHONPATH hijack (`root`).
2. **Pivot** via a leaked SSH key to the internal-only host.
3. **M2** key-based SSH (`svc_backup`) → `sudo tar` GTFOBins (`root`).

## Flags (declare these exact values in the submission form)

| Machine | Location | Flag |
|---------|----------|------|
| web (M1) | User (`/home/developer/local.txt`) | `OS{w3b_f00th0ld_ch41n3d_t0_r00t_9f2c}` |
| web (M1) | Root (`/root/proof.txt`) | `OS{m1_r00t_pyth0np4th_h1j4ck_a71d}` |
| internal (M2) | User (`/home/svc_backup/local.txt`) | `OS{p1v0t3d_t0_1nt3rn4l_h0st_c3d8}` |
| internal (M2) | Root (`/root/proof.txt`) | `OS{d0ubl3_pwn_tar_g7f0b1ns_r00t_4e90}` |

## Verify

```bash
# unpack artifacts.zip, then from its root:
docker compose up --build -d
../autopwn.py 127.0.0.1 80 2222     # prints all four OS{...} flags
docker compose down -v
```

Intentionally vulnerable software — authorized training use only.
