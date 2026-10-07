# Observ — MITRE ATT&CK Mapping

Each stage of the intended chain mapped to MITRE ATT&CK (Enterprise) tactics
and techniques, as required for UGC submission.

| Stage | Host | Tactic | Technique (ID) |
|-------|------|--------|----------------|
| Port/service enumeration | M1 | Reconnaissance | Active Scanning (T1595) |
| Web content discovery (`robots.txt`, `/monitor/`) | M1 | Discovery | — / Active Scanning: Wordlist Scanning (T1595.003) |
| SQL injection auth bypass | M1 | Initial Access | Exploit Public-Facing Application (T1190) |
| OS command injection → shell | M1 | Execution | Command and Scripting Interpreter: Unix Shell (T1059.004) |
| Read `config.php` secrets | M1 | Credential Access | Unsecured Credentials: Credentials In Files (T1552.001) |
| Reuse DB password for `developer` | M1 | Lateral/Privilege | Valid Accounts: Local Accounts (T1078.003) |
| SSH as developer | M1 | Persistence/Lateral | Remote Services: SSH (T1021.004) |
| `sudo` + PYTHONPATH import hijack | M1 | Privilege Escalation | Abuse Elevation Control Mechanism: Sudo and Sudo Caching (T1548.003) |
| — PYTHONPATH module planting | M1 | Privilege Escalation | Hijack Execution Flow: Path Interception / Python (T1574.007) |
| Discover second interface / internal host | M1 | Discovery | System Network Configuration Discovery (T1016) |
| Loot leaked SSH private key | M1 | Credential Access | Unsecured Credentials: Private Keys (T1552.004) |
| Pivot through M1 to reach M2 | — | Lateral Movement | Internal Proxy / Protocol Tunneling (T1090.001 / T1572) |
| SSH to svc_backup with key | M2 | Lateral Movement | Remote Services: SSH (T1021.004) |
| `sudo tar` checkpoint-action (GTFOBins) | M2 | Privilege Escalation | Abuse Elevation Control Mechanism: Sudo and Sudo Caching (T1548.003) |

## Primary ATT&CK coverage summary

- **T1190** Exploit Public-Facing Application
- **T1059.004** Unix Shell execution
- **T1552.001 / T1552.004** Unsecured Credentials (files, private keys)
- **T1078.003** Valid Local Accounts (credential reuse)
- **T1548.003** Sudo abuse (two distinct mechanisms)
- **T1574.007** Path Interception (PYTHONPATH)
- **T1021.004** SSH
- **T1090 / T1572** Pivoting / tunnelling across network segments
