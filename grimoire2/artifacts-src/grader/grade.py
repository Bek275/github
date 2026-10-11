#!/usr/bin/env python3
"""
Beacon Incident -- grader (Grimoire / defensive lab).

Checks a learner's answers against the solution. Answers file format: one
`key = value` per line (blank lines and lines starting with '#' are ignored).

Usage:  python3 grade.py answers.txt
"""
import re
import sys

SOLUTION = {
    "flag1":        ("OS{m4cr0_enc_p0w3rsh3ll_dr0pp3r}", "flag 1 (Base64 inside the -enc value)"),
    "flag2":        ("OS{br0ws3r_cr3ds_b34c0n_3xf1l}", "flag 2 (staged exfil manifest)"),
    "phish_sender": ("billing@vendor-portal-support.com", "spoofed sender of the phishing email"),
    "c2_domain":    ("cdn.lifestyle-deals.net", "external C2 / upload domain"),
    "victim_host":  (re.compile(r"fin-wks-07|j\.morgan", re.I), "compromised host / user"),
    "initial_exec": (re.compile(r"enc|encoded", re.I), "how code first ran (encoded PowerShell)"),
    "persistence":  (re.compile(r"sched|schtask|task", re.I), "persistence mechanism (scheduled task)"),
    "cred_access":  (re.compile(r"browser|login ?data|chrome|credential|cookie", re.I),
                     "credential access (browser credential store)"),
}


def norm(s):
    return s.strip().strip('"').strip("'")


def parse(path):
    ans = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            ans[k.strip().lower()] = norm(v)
    return ans


def main():
    if len(sys.argv) != 2:
        print("usage: grade.py answers.txt"); return 2
    ans = parse(sys.argv[1])
    correct = 0
    print("=" * 62)
    for key, (expect, label) in SOLUTION.items():
        got = ans.get(key, "")
        ok = bool(expect.search(got)) if isinstance(expect, re.Pattern) else got.lower() == expect.lower()
        correct += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {key:13} {label}")
        if not ok:
            print(f"        your answer: {got or '<empty>'}")
    print("=" * 62)
    print(f"SCORE: {correct}/{len(SOLUTION)}")
    return 0 if correct == len(SOLUTION) else 1


if __name__ == "__main__":
    sys.exit(main())
