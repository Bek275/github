# Observ Incident — Grimoire (defensive) lab

A defensive, evidence-driven investigation lab: the **blue-team view of the
"Observ" intrusion**. The learner is handed a triage evidence bundle and
reconstructs the kill chain, recovering two `OS{...}` flags.

- **Lab type:** VM Submission → Grimoire (defensive)
- **Difficulty:** Intermediate (defender's perspective)
- **No live VM** — pure artifact analysis (DFIR / threat hunting)

## Package root (outer archive)

Per the Grimoire sample, the submission root holds just two items:

| File | Purpose |
|------|---------|
| `walkthrough.pdf` | **human-authored** solution (AI-written walkthroughs are not allowed) |
| `artifacts.zip` | evidence bundle + generator + grader + docs |

## Inside `artifacts.zip`

| Path | Purpose |
|------|---------|
| `evidence/` | the telemetry the learner investigates (logs, histories, artifacts) |
| `questions.md` | the investigation tasks + answer keys to fill in |
| `answer-key.md` | reviewer solution key (not the learner walkthrough) |
| `build/generate_evidence.py` | deterministically regenerates `evidence/` |
| `grader/grade.py` | scores a learner `answers.txt` (out of 8) |
| `mitre-attack.md` | ATT&CK detection mapping |
| `build-guide.md` | build/grading guide + Grimoire principles |
| `README.md` | this file |

## Flags

| Flag | Value | Recovery |
|------|-------|----------|
| web01 | `OS{w3b01_rc3_d14g_c0mm4nd_1nj}` | base64 marker in `diag_debug.log` |
| internal01 | `OS{1nt3rn4l_r00t_sud0_tar_pivot}` | staged file on internal01 |

## Quick check

```bash
python3 build/generate_evidence.py evidence      # (re)build the evidence
python3 grader/grade.py answers.txt               # score an answers file
```

Educational, fictitious defensive scenario — for authorized training only.
