#!/usr/bin/env python3
"""
Observ Incident -- grader (Grimoire / defensive lab).

Checks a learner's answers against the solution. Answers file format: one
`key = value` per line (blank lines and lines starting with '#' are ignored).

Usage:  python3 grade.py answers.txt
"""
import re
import sys

# key -> (accepted matcher, human label)
SOLUTION = {
    "flag_web01":     ("OS{w3b01_rc3_d14g_c0mm4nd_1nj}", "web01 flag (base64 in diag_debug.log)"),
    "flag_internal":  ("OS{1nt3rn4l_r00t_sud0_tar_pivot}", "internal01 flag (staged exfil note)"),
    "attacker_ip":    ("10.10.14.7", "attacker source IP"),
    "cmdi_param":     ("host", "vulnerable HTTP parameter (command injection)"),
    "reused_account": ("developer", "local account whose password was reused"),
    "privesc_web01":  (re.compile(r"python ?path", re.I), "web01 root technique (PYTHONPATH hijack)"),
    "pivot_ip":       ("172.20.0.3", "internal host pivoted to"),
    "gtfobins_binary":("tar", "GTFOBins binary used for root on internal01"),
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
    print("=" * 60)
    for key, (expect, label) in SOLUTION.items():
        got = ans.get(key, "")
        if isinstance(expect, re.Pattern):
            ok = bool(expect.search(got))
        else:
            ok = got.lower() == expect.lower()
        mark = "\033[1;32mPASS\033[0m" if ok else "\033[1;31mFAIL\033[0m"
        correct += ok
        print(f"[{mark}] {key:16} {label}")
        if not ok:
            print(f"         your answer: {got or '<empty>'}")
    total = len(SOLUTION)
    print("=" * 60)
    print(f"SCORE: {correct}/{total}")
    return 0 if correct == total else 1


if __name__ == "__main__":
    sys.exit(main())
