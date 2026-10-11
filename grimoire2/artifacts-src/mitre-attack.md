# Beacon Incident — MITRE ATT&CK (detection mapping)

Techniques a defender should identify in the evidence, with the artifact that
reveals each.

| Technique (ID) | Evidence / detection opportunity |
|----------------|----------------------------------|
| Phishing: Spearphishing Attachment (T1566.001) | `Invoice_Q3_phish.eml` (SPF/DMARC fail, macro doc) |
| User Execution: Malicious File (T1204.002) | macro `Document_Open` auto-exec; WINWORD → cmd |
| Command and Scripting Interpreter: PowerShell (T1059.001) | sysmon/4688 `powershell -nop -w hidden -enc` |
| Obfuscated/Encoded Command; Deobfuscate (T1027 / T1140) | Base64 UTF-16LE in the `-enc` value; 4104 script block |
| Ingress Tool Transfer (T1105) | proxy `GET http://<c2>/u/x.ps1` |
| Scheduled Task/Job (T1053.005) | `scheduled_task_*.xml`; sysmon schtasks line |
| Masquerading: Match Legitimate Name (T1036.004) | task named `MicrosoftEdgeUpdateTaskMachineCore` |
| Credentials from Web Browsers (T1555.003) | `file_access_sensitive.log` (Chrome Login Data / cookies) |
| Application Layer Protocol: Web (T1071.001) | beacon GETs to `/api/task` |
| Data Staged: Local Data Staging (T1074.001) | `C:\Users\Public\.stage\` manifest |
| Exfiltration Over C2 Channel (T1041) | proxy `POST /api/upload` (5 MB) |

## Suggested detections (teaching points)

- Alert on Office apps (WINWORD/EXCEL) spawning `cmd`/`powershell`.
- Alert on `powershell -enc`/`-EncodedCommand`, especially with `-w hidden -nop`.
- Enable Script Block Logging (4104) and alert on long Base64 blobs.
- Alert on `schtasks /create` from `powershell`, and on tasks whose names
  mimic vendor update tasks but whose action is `powershell ... -File`.
- Alert on non-browser processes reading browser `Login Data`/cookie stores.
- Flag beaconing (regular small GETs) and large POSTs to newly-registered,
  no-business-purpose domains.
