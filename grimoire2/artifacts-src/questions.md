# Beacon Incident — Investigation Tasks

You are a SOC analyst at **Northwind Trading**. The finance workstation
**FIN-WKS-07** generated several alerts this morning after the user opened an
email attachment. You have been handed a triage evidence bundle (`evidence/`).
Reconstruct what happened using **only** the provided artifacts.

Record your findings in an `answers.txt` file (`key = value` per line) and
check them with `grader/grade.py answers.txt`.

| key | Question |
|-----|----------|
| `phish_sender` | What was the spoofed sender address of the phishing email? |
| `victim_host` | Which host/user was compromised? |
| `initial_exec` | How did code first execute after the document was opened? |
| `flag1` | Decode the Base64 in the PowerShell `-enc` value (it is UTF-16LE) and recover the marker. `OS{...}` |
| `persistence` | What persistence mechanism did the attacker create? |
| `cred_access` | What sensitive data store did the attacker access for credentials? |
| `c2_domain` | What external domain was used for beaconing and upload? |
| `flag2` | Recover the marker from the file the attacker staged for exfiltration. `OS{...}` |

## Evidence index

```
evidence/
├── email/Invoice_Q3_phish.eml                      the lure (headers, SPF/DMARC)
├── extracted/Invoice_Q3_macro_summary.txt          static triage of the macro (defanged)
├── FIN-WKS-07/
│   ├── sysmon_process_creation.log                 EID 1 process tree
│   ├── powershell_4104_scriptblock.log             script-block logging
│   ├── file_access_sensitive.log                   access to the browser credential store
│   ├── security_4688_4624.log                      process creation + logon
│   ├── scheduled_task_MicrosoftEdgeUpdateTaskMachineCore.xml   persistence
│   └── C_Users_Public/.stage/exfil_manifest.txt    staged artifact
└── proxy/squid_access.log                          beacon + upload traffic
```

> Defensive lab: investigate and reason from the evidence. No exploitation,
> live systems, or operational malware are involved — the bundle is telemetry
> for detection and analysis only.
