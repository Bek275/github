#!/usr/bin/env python3
"""
Render realistic terminal screenshots of the Observ Incident (Grimoire)
investigation, by running each command against the real evidence and
screenshotting the result. Figures are for the author to paste into their
walkthrough (they still write the analysis prose themselves).

Usage: python3 make_grimoire_shots.py <evidence_dir> <out_dir>
"""
import html
import os
import re
import subprocess
import sys

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
PROMPT = "analyst@soc:~/observ-incident$"
ANSI = re.compile(r"\x1b\[[0-9;]*m")

# (filename, title, command)  -- command runs with cwd = evidence_dir's parent
STEPS = [
    ("01_evidence_tree", "Evidence bundle received", "find evidence -type f | sort"),
    ("02_access_log", "web01 — external HTTP activity (attacker IP + diag.php)",
     "grep -nE 'diag.php|index.php|robots' evidence/web01/var/log/apache2/access.log"),
    ("03_diag_debug", "web01 — diagnostics debug log reveals command injection",
     "cat evidence/web01/var/log/observ/diag_debug.log"),
    ("04_decode_flag1", "web01 — decode the staged base64 marker (flag 1)",
     "grep 'base64 -d' evidence/web01/var/log/observ/diag_debug.log | "
     "grep -oE '[A-Za-z0-9+/=]{20,}' | base64 -d"),
    ("05_authlog_web01", "web01 — SSH login + sudo PYTHONPATH in auth.log",
     "cat evidence/web01/var/log/auth.log"),
    ("06_bash_developer", "web01 — attacker commands (developer history)",
     "cat evidence/web01/home/developer/.bash_history"),
    ("07_netcheck", "web01 — recovered malicious module (PYTHONPATH hijack)",
     "cat evidence/web01/tmp/.x/netcheck.py"),
    ("08_authlog_internal", "internal01 — pivot in (publickey) + sudo tar",
     "cat evidence/internal01/var/log/auth.log"),
    ("09_bash_svcbackup", "internal01 — attacker commands + staged exfil",
     "cat evidence/internal01/home/svc_backup/.bash_history"),
    ("10_flag2", "internal01 — recover staged value (flag 2)",
     "cat evidence/internal01/tmp/.exfil/stage.txt"),
]


def run(cmd, cwd):
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return ANSI.sub("", (p.stdout + p.stderr)).rstrip("\n")


def render(fname, title, cmd, output, out_dir):
    body = html.escape(output) or "(no output)"
    cmd_h = html.escape(cmd)
    lines = output.count("\n") + cmd.count("\n") + 8
    height = min(1400, max(240, lines * 21 + 120))
    doc = f"""<!doctype html><html><head><meta charset=utf-8><style>
    html,body{{margin:0;background:#0b1021}}
    .term{{font-family:'DejaVu Sans Mono',Menlo,Consolas,monospace;font-size:14px;
      line-height:1.45;color:#e6e6e6;padding:18px 20px}}
    .bar{{background:#1b2140;color:#9aa4d4;padding:8px 14px;border-radius:9px 9px 0 0;
      font-family:sans-serif;font-size:12.5px}}
    .dot{{height:11px;width:11px;border-radius:50%;display:inline-block;margin-right:6px}}
    .wrap{{margin:14px;border-radius:10px;overflow:hidden;border:1px solid #2a3157;
      box-shadow:0 8px 30px rgba(0,0,0,.4)}}
    .body{{background:#0b1021}}
    .p{{color:#6ee7b7}} .c{{color:#e6e6e6}} .o{{color:#cbd5e1;white-space:pre-wrap}}
    .flag{{color:#fbbf24;font-weight:bold}}
    .title{{font-family:sans-serif;color:#94a3b8;font-size:12px;margin:14px 16px 0}}
    </style></head><body>
    <div class="title">{html.escape(title)}</div>
    <div class="wrap"><div class="bar"><span class="dot" style="background:#ff5f56"></span>
    <span class="dot" style="background:#ffbd2e"></span><span class="dot" style="background:#27c93f"></span>
    &nbsp; {PROMPT.split('$')[0]} — investigation</div>
    <div class="body"><div class="term"><span class="p">{PROMPT}</span> <span class="c">{cmd_h}</span>
<div class="o">{_hl(body)}</div></div></div></div>
    </body></html>"""
    hpath = os.path.join(out_dir, fname + ".html")
    ppath = os.path.join(out_dir, fname + ".png")
    with open(hpath, "w") as f:
        f.write(doc)
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu",
                    "--hide-scrollbars", "--force-device-scale-factor=2",
                    f"--window-size=980,{height}",
                    f"--screenshot={ppath}", f"file://{hpath}"],
                   capture_output=True)
    os.remove(hpath)
    print(f"[+] {ppath}")


def _hl(text):
    # highlight OS{...} flags
    return re.sub(r"(OS\{[^}]*\})", r'<span class="flag">\1</span>', text)


def main():
    ev = sys.argv[1] if len(sys.argv) > 1 else "evidence"
    out = sys.argv[2] if len(sys.argv) > 2 else "figures"
    cwd = os.path.dirname(os.path.abspath(ev)) or "."
    os.makedirs(out, exist_ok=True)
    out = os.path.abspath(out)
    for fname, title, cmd in STEPS:
        output = run(cmd, cwd)
        render(fname, title, cmd, output, out)


if __name__ == "__main__":
    main()
