# Beacon Incident (Grimoire) — Build Guide

Defensive / investigation lab. There is **no live VM** and **no operational
malware**: the learner is given a triage evidence bundle (telemetry) and must
reconstruct a Windows phishing-to-exfiltration intrusion from it.

- **Lab type:** Grimoire (defensive, evidence-driven)
- **Scenario:** phishing → encoded PowerShell → scheduled-task persistence →
  browser credential access → beacon/exfil, on a finance workstation
- **Difficulty:** Intermediate *(defender's perspective)*
- **Flags:** 2 × `OS{...}`, both recoverable only by correct analysis

## Design against the four Grimoire principles

1. **Evidence-driven** — every answer is derivable from an artifact
   (`answer-key.md` cites the exact file for each).
2. **Narrative coherence** — all artifacts describe one intrusion, in order:
   phish → macro → encoded PowerShell → C2 pull → persistence → credential
   access → exfil.
3. **Defensive mindset** — detection/investigation/reasoning over email, Sysmon,
   PowerShell 4104, Security 4688/4624, a scheduled-task XML, EDR file-access and
   proxy logs. No exploitation.
4. **Realistic telemetry** — standard Windows/EDR/proxy sources in realistic
   formats and paths.

## Safety / content note

This bundle intentionally ships **no working payload**. Where the real intrusion
carried operational code, the artifact is redacted/defanged and only the
indicators a defender would observe remain (for example, the `-enc` Base64
decodes to a short IR stub with the marker, not a functional loader). This keeps
the lab suitable for training without distributing offensive tooling.

## Regenerating the evidence (deterministic)

```bash
python3 build/generate_evidence.py evidence
```

Writes `evidence/` with both flags embedded (one as Base64 UTF-16LE inside the
`-enc` value, one in the staged manifest).

## Grading learner answers

```bash
python3 grader/grade.py answers.txt      # answers.txt: key = value per line
```

The grader checks the two flags plus six derived facts (see `questions.md`) and
prints a score out of 8.

## Flags

| Flag | Value | Recovery |
|------|-------|----------|
| flag1 | `OS{m4cr0_enc_p0w3rsh3ll_dr0pp3r}` | Base64 (UTF-16LE) decode of the `-enc` value |
| flag2 | `OS{br0ws3r_cr3ds_b34c0n_3xf1l}` | staged manifest under `C:\Users\Public\.stage` |

## Difficulty note

Per OffSec guidance, difficulty is rated from the perspective of a **defensive**
practitioner; analysts from a purely offensive background may find it harder,
which should not change the rating.

## ⚠️ Walkthrough authorship (OffSec rule)

OffSec does **not** permit walkthroughs that are generated, drafted, or
substantially written by AI for Grimoire submissions. The `walkthrough.pdf` must
be **human-authored**. A section skeleton (with the figures and factual
scaffolding) and the `answer-key.md` are provided to speed you up, but write the
analysis/narrative in your own words before submitting.
