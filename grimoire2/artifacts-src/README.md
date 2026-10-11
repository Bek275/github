# Beacon Incident — Grimoire (defensive) lab

A defensive, evidence-driven investigation lab: a **Windows phishing-to-exfil
intrusion** on a finance workstation, seen from the SOC. The learner is handed a
triage evidence bundle and reconstructs the kill chain, recovering two `OS{...}`
flags. No live VM and no operational malware — telemetry only.

- **Lab type:** VM Submission → Grimoire (defensive)
- **Difficulty:** Intermediate (defender's perspective)
- **Flags:** 2 × `OS{...}`

## Package root (outer archive, password-protected)

Per the Grimoire form, the submission zip is **password-protected** and contains:

| File | Purpose |
|------|---------|
| `walkthrough.pdf` | **human-authored** solution (AI-written walkthroughs are not allowed) |
| `artifacts.zip` | evidence bundle + generator + grader + docs |

## Inside `artifacts.zip`

| Path | Purpose |
|------|---------|
| `evidence/` | the telemetry the learner investigates (email, Sysmon, 4104, 4688/4624, scheduled task, EDR file-access, proxy) |
| `questions.md` | investigation tasks + answer keys to fill in |
| `answer-key.md` | reviewer solution key (not the learner walkthrough) |
| `build/generate_evidence.py` | deterministically regenerates `evidence/` |
| `grader/grade.py` | scores a learner `answers.txt` (out of 8) |
| `mitre-attack.md` | ATT&CK detection mapping |
| `build-guide.md` | build/grading guide + Grimoire principles + safety note |
| `README.md` | this file |

## Flags

| Flag | Value | Recovery |
|------|-------|----------|
| flag1 | `OS{m4cr0_enc_p0w3rsh3ll_dr0pp3r}` | Base64 (UTF-16LE) decode of the `-enc` value |
| flag2 | `OS{br0ws3r_cr3ds_b34c0n_3xf1l}` | staged manifest under `C:\Users\Public\.stage` |

## Quick check

```bash
python3 build/generate_evidence.py evidence
python3 grader/grade.py answers.txt
```

Educational, fictitious defensive scenario — authorized training only. Ships no
operational malware; malicious payloads are redacted/defanged.
