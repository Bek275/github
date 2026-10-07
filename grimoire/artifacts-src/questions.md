# Observ Incident — Investigation Tasks

You are a SOC analyst. An alert fired on **web01** (the Observ monitoring
portal) and an internal backup host, **internal01**, shortly after. You have
been handed a triage evidence bundle (`evidence/`). Reconstruct what happened
using **only** the provided artifacts.

Record your findings in an `answers.txt` file (`key = value` per line) and
check them with `grader/grade.py answers.txt`.

| key | Question |
|-----|----------|
| `attacker_ip` | From which source IP did the attacker interact with web01? |
| `cmdi_param` | Which HTTP parameter on `/monitor/diag.php` was abused for command execution? |
| `reused_account` | The attacker logged in over SSH as a local user. Which account's password had been reused (and where was it found)? |
| `privesc_web01` | What technique was used to gain root on web01 via the allowed `sudo` health-check? |
| `flag_web01` | Recover the canary the attacker staged on web01 (hint: a base64 value in the diagnostics debug log). `OS{...}` |
| `pivot_ip` | Which internal host did the attacker pivot to from web01? |
| `gtfobins_binary` | Which `sudo`-allowed binary gave root on internal01 (GTFOBins)? |
| `flag_internal` | Recover the value the attacker staged for exfiltration on internal01. `OS{...}` |

## Evidence index

```
evidence/
├── web01/
│   ├── var/log/apache2/access.log        external HTTP activity
│   ├── var/log/observ/diag_debug.log     app log of diagnostic 'host' values
│   ├── var/log/auth.log                   SSH + sudo
│   ├── home/developer/.bash_history       attacker's commands
│   ├── tmp/.x/netcheck.py                 recovered artifact
│   └── var/www/html/config.php            app configuration
└── internal01/
    ├── var/log/auth.log                   SSH (publickey) + sudo
    ├── home/svc_backup/.bash_history       attacker's commands
    └── tmp/.exfil/stage.txt                staged artifact
```

> Defensive lab: investigate and reason from the evidence. No exploitation or
> live systems are involved.
