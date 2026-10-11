# Beacon Incident — Answer Key (reviewer reference)

> Factual solution key for reviewers/graders. This is **not** the learner
> walkthrough. Per OffSec Grimoire rules the student-facing `walkthrough.pdf`
> must be written by a human author — see `build-guide.md`.

| key | Answer | Where in the evidence |
|-----|--------|-----------------------|
| `phish_sender` | `billing@vendor-portal-support.com` | `email/Invoice_Q3_phish.eml` (From; SPF/DMARC fail) |
| `victim_host` | `FIN-WKS-07` / `NORTHWIND\j.morgan` | all FIN-WKS-07 logs |
| `initial_exec` | encoded PowerShell (`-enc`) launched by the macro | macro summary; sysmon; 4688 |
| `flag1` | `OS{m4cr0_enc_p0w3rsh3ll_dr0pp3r}` | Base64 of the `-enc` value (UTF-16LE) → decodes to a stub with the marker |
| `persistence` | scheduled task `MicrosoftEdgeUpdateTaskMachineCore` (every 10 min) | `scheduled_task_*.xml`; sysmon schtasks line |
| `cred_access` | browser credential store (Chrome `Login Data` / cookies) | `file_access_sensitive.log` |
| `c2_domain` | `cdn.lifestyle-deals.net` (203.0.113.45) | `proxy/squid_access.log`; 4104; stub |
| `flag2` | `OS{br0ws3r_cr3ds_b34c0n_3xf1l}` | `C_Users_Public/.stage/exfil_manifest.txt` |

## Recovering the two flags

- **flag1 (UTF-16LE Base64).** The `-enc` value is Base64 of UTF-16LE text.
  Decode it (any of):
  ```bash
  # from the sysmon line, extract the Base64 after "-enc" then:
  python3 -c "import sys,base64;print(base64.b64decode(sys.argv[1]).decode('utf-16-le'))" <B64>
  # or in PowerShell:
  [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('<B64>'))
  ```
  The decoded stub contains `$marker = 'OS{m4cr0_enc_p0w3rsh3ll_dr0pp3r}'`.
- **flag2.** `cat` the staged manifest under `C:\Users\Public\.stage`:
  `OS{br0ws3r_cr3ds_b34c0n_3xf1l}`.

## Kill chain (fact summary)

1. Spearphishing email with a macro document (SPF/DMARC fail).
2. User opens it; `Document_Open` launches hidden encoded PowerShell.
3. Second stage pulled from the C2 domain (proxy GET of `x.ps1`).
4. Persistence: scheduled task masquerading as an Edge update, every 10 min.
5. Credential access: browser credential store (Chrome Login Data / cookies).
6. Beaconing + a large upload (POST) to the C2 domain; data staged under
   `C:\Users\Public\.stage`.
