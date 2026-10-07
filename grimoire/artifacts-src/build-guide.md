# Observ Incident (Grimoire) — Build Guide

Defensive / investigation lab. There is **no live VM**: the learner is given a
triage evidence bundle and must reconstruct the intrusion from it.

- **Lab type:** Grimoire (defensive, evidence-driven)
- **Scenario:** the defender's view of the "Observ" intrusion (web01 → internal01)
- **Difficulty:** Intermediate *(from a defender's perspective — see note below)*
- **Flags:** 2 × `OS{...}`, both recoverable only by correct analysis

## Design against the four Grimoire principles

1. **Evidence-driven** — every answer is derivable from an artifact
   (`answer-key.md` cites the exact file for each). Nothing requires guessing.
2. **Narrative coherence** — all artifacts describe one intrusion: SQLi →
   command injection → credential reuse → sudo/PYTHONPATH root → pivot →
   sudo tar root → staging.
3. **Defensive mindset** — the task is detection/investigation/reasoning over
   logs, histories and a recovered artifact; no exploitation of live systems.
4. **Realistic telemetry** — Apache access log, an application debug log, Linux
   `auth.log` (SSH + sudo), shell histories, a recovered malicious module, and
   a staged exfil file, in realistic on-disk paths.

## Regenerating the evidence (deterministic)

```bash
python3 build/generate_evidence.py evidence
```

This writes `evidence/` with both flags embedded (one base64 in
`web01/.../diag_debug.log`, one in `internal01/tmp/.exfil/stage.txt`).

## Grading learner answers

```bash
python3 grader/grade.py answers.txt      # answers.txt: key = value per line
```

The grader checks the two flags plus six derived facts (see `questions.md`)
and prints a score out of 8.

## Flags

| Flag | Value | Recovery |
|------|-------|----------|
| web01 | `OS{w3b01_rc3_d14g_c0mm4nd_1nj}` | base64-decode the marker in `diag_debug.log` |
| internal01 | `OS{1nt3rn4l_r00t_sud0_tar_pivot}` | staged in `internal01/tmp/.exfil/stage.txt` |

## Difficulty note

Per OffSec guidance, difficulty is rated from the perspective of a
**defensive** practitioner with appropriate skills; analysts from a purely
offensive background may find it harder, which should not change the rating.

## ⚠️ Walkthrough authorship (OffSec rule)

OffSec does **not** permit walkthroughs that are generated, drafted, or
substantially written by AI for Grimoire submissions. The `walkthrough.pdf` in
this package is a **human-authored** document. A section skeleton and the
factual `answer-key.md` are provided as scaffolding only; the author must write
the analysis/narrative themselves before submitting.
