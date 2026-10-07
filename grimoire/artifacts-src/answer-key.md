# Observ Incident — Answer Key (reviewer reference)

> Factual solution key for reviewers/graders. This is **not** the learner
> walkthrough. Per OffSec Grimoire rules, the student-facing `walkthrough.pdf`
> must be written by a human author — see `build-guide.md`.

| key | Answer | Where in the evidence |
|-----|--------|-----------------------|
| `attacker_ip` | `10.10.14.7` | `web01/var/log/apache2/access.log`, `auth.log` |
| `cmdi_param` | `host` | `web01/var/log/observ/diag_debug.log` (`host=127.0.0.1; id`) |
| `reused_account` | `developer` | config.php DB pass reused → `auth.log` SSH as developer |
| `privesc_web01` | PYTHONPATH hijack | `auth.log` sudo `ENV=PYTHONPATH=/tmp/.x`; `tmp/.x/netcheck.py`; bash history |
| `flag_web01` | `OS{w3b01_rc3_d14g_c0mm4nd_1nj}` | base64 in `diag_debug.log` line `echo <b64> | base64 -d` |
| `pivot_ip` | `172.20.0.3` | developer `.bash_history` ssh; internal01 `auth.log` from 172.20.0.2 |
| `gtfobins_binary` | `tar` | internal01 `auth.log` sudo tar `--checkpoint-action`; bash history |
| `flag_internal` | `OS{1nt3rn4l_r00t_sud0_tar_pivot}` | `internal01/tmp/.exfil/stage.txt` + bash history |

## Recovering the two flags

- **web01:** in `diag_debug.log` the attacker ran
  `echo <BASE64> | base64 -d > /tmp/.obs_marker`. Base64-decode `<BASE64>`:
  ```
  echo 'T1N7dz...' | base64 -d      ->  OS{w3b01_rc3_d14g_c0mm4nd_1nj}
  ```
- **internal01:** `home/svc_backup/.bash_history` shows
  `echo OS{...} > /tmp/.exfil/stage.txt`; the file is present at
  `internal01/tmp/.exfil/stage.txt`.

## Kill chain (fact summary)

1. Recon → SQLi auth bypass on `/index.php` (repeated POSTs then dashboard).
2. Command injection via `host` on `/monitor/diag.php` (`diag_debug.log`).
3. Credential reuse: `config.php` DB password reused for `developer` (SSH login).
4. Root on web01: `sudo` python health-check + preserved `PYTHONPATH` hijack.
5. Pivot: leaked `svc_backup` key → SSH to `172.20.0.3`.
6. Root on internal01: `sudo tar` GTFOBins checkpoint action.
7. Staging/exfil on internal01 (`/tmp/.exfil`).
