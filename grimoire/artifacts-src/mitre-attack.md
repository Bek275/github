# Observ Incident — MITRE ATT&CK (detection mapping)

Techniques a defender should identify in the evidence, with the artifact that
reveals each.

| Technique (ID) | Evidence / detection opportunity |
|----------------|----------------------------------|
| Exploit Public-Facing Application (T1190) | repeated `POST /index.php` then dashboard access (access.log) |
| Command and Scripting Interpreter: Unix Shell (T1059.004) | `host=127.0.0.1; <cmd>` entries in `diag_debug.log` |
| Unsecured Credentials: Credentials In Files (T1552.001) | `host=...; cat /var/www/html/config.php`; DB pass in config |
| Valid Accounts: Local Accounts (T1078.003) | SSH `Accepted password for developer` from attacker IP |
| Remote Services: SSH (T1021.004) | `auth.log` on both hosts |
| Abuse Elevation Control: Sudo (T1548.003) | sudo of the python health-check; sudo `tar` on internal01 |
| Hijack Execution Flow: Path Interception / PYTHONPATH (T1574.007) | sudo `ENV=PYTHONPATH=/tmp/.x`; recovered `tmp/.x/netcheck.py` |
| Unsecured Credentials: Private Keys (T1552.004) | `cat ~/.ssh/svc_backup_id_ed25519` in bash history |
| Lateral Movement / Internal Proxy (T1090.001) | pivot from 172.20.0.2 to 172.20.0.3 (internal01 auth.log) |
| Archive Collected Data (T1560.001) | `tar czf /tmp/.exfil/backup.tgz` in svc_backup history |

## Suggested detections (teaching points)

- Alert on shell metacharacters (`;`, `|`, `` ` ``) in diagnostic/ping inputs.
- Alert on `sudo` invocations that carry `PYTHONPATH`/`LD_*`/`PERL5LIB` in `ENV=`.
- Alert on `tar`/`find`/`vi` run under `sudo` with `--checkpoint-action`/`-exec`.
- Correlate a single source IP across web auth, app logs and downstream SSH.
- Flag SSH **from a web/DMZ host** into an internal segment (east-west pivot).
