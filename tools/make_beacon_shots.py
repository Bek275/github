#!/usr/bin/env python3
"""
Render terminal screenshots of the Beacon Incident (Grimoire) investigation by
running each command against the generated evidence and screenshotting the
result. Figures are for the author to paste into their (human-written)
walkthrough.

Usage: python3 make_beacon_shots.py <evidence_dir> <out_dir>
"""
import html
import os
import re
import subprocess
import sys

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
PROMPT = "analyst@soc:~/beacon-incident$"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
H = "evidence/FIN-WKS-07"

STEPS = [
    ("01_tree", "Evidence bundle received", "find evidence -type f | sort"),
    ("02_phish", "Phishing email — spoofed sender, SPF/DMARC fail",
     "sed -n '1,9p' evidence/email/Invoice_Q3_phish.eml"),
    ("03_macro", "Static triage of the attached macro (defanged)",
     "sed -E 's/-enc [A-Za-z0-9+/=]+/-enc <BASE64>/' evidence/extracted/Invoice_Q3_macro_summary.txt"),
    ("04_sysmon", "Sysmon EID 1 — WINWORD spawns encoded PowerShell, then schtasks",
     f"sed -E 's/-enc [A-Za-z0-9+/=]+/-enc <BASE64>/g' {H}/sysmon_process_creation.log | cut -c1-150"),
    ("05_decode", "Decode the -enc value (Base64 UTF-16LE) → flag 1",
     f"B=$(grep -oE -- '-enc [A-Za-z0-9+/=]+' {H}/sysmon_process_creation.log | head -1 | awk '{{print $2}}'); "
     "python3 -c \"import base64,sys;print(base64.b64decode(sys.argv[1]).decode('utf-16-le'))\" \"$B\""),
    ("06_4104", "PowerShell 4104 script-block logging",
     f"cat {H}/powershell_4104_scriptblock.log"),
    ("07_credaccess", "EDR — powershell reads the browser credential store",
     f"cat {H}/file_access_sensitive.log"),
    ("08_schtask", "Persistence — scheduled task masquerading as an Edge update",
     f"sed -n '1,16p' {H}/scheduled_task_MicrosoftEdgeUpdateTaskMachineCore.xml"),
    ("09_proxy", "Proxy log — beacon + large upload to the C2 domain",
     "cat evidence/proxy/squid_access.log"),
    ("10_flag2", "Staged exfil manifest → flag 2",
     f"cat {H}/C_Users_Public/.stage/exfil_manifest.txt"),
]


def run(cmd, cwd):
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return ANSI.sub("", (p.stdout + p.stderr)).rstrip("\n")


def hl(text):
    return re.sub(r"(OS\{[^}]*\})", r'<span class="flag">\1</span>', text)


def render(fname, title, cmd, output, out_dir):
    cmd_disp = cmd if len(cmd) < 120 else cmd[:117] + "..."
    body = hl(html.escape(output) or "(no output)")
    lines = output.count("\n") + 9
    height = min(1500, max(230, lines * 21 + 120))
    doc = f"""<!doctype html><html><head><meta charset=utf-8><style>
    html,body{{margin:0;background:#0b1021}}
    .term{{font-family:'DejaVu Sans Mono',Menlo,Consolas,monospace;font-size:13.5px;
      line-height:1.45;color:#e6e6e6;padding:16px 18px}}
    .bar{{background:#1b2140;color:#9aa4d4;padding:8px 14px;border-radius:9px 9px 0 0;
      font-family:sans-serif;font-size:12.5px}}
    .dot{{height:11px;width:11px;border-radius:50%;display:inline-block;margin-right:6px}}
    .wrap{{margin:14px;border-radius:10px;overflow:hidden;border:1px solid #2a3157}}
    .body{{background:#0b1021}} .p{{color:#6ee7b7}} .o{{color:#cbd5e1;white-space:pre-wrap;word-break:break-all}}
    .flag{{color:#fbbf24;font-weight:bold}}
    .title{{font-family:sans-serif;color:#94a3b8;font-size:12px;margin:14px 16px 0}}
    </style></head><body>
    <div class="title">{html.escape(title)}</div>
    <div class="wrap"><div class="bar"><span class="dot" style="background:#ff5f56"></span>
    <span class="dot" style="background:#ffbd2e"></span><span class="dot" style="background:#27c93f"></span>
    &nbsp; soc — investigation</div>
    <div class="body"><div class="term"><span class="p">{PROMPT}</span> {html.escape(cmd_disp)}
<div class="o">{body}</div></div></div></div></body></html>"""
    hp = os.path.join(out_dir, fname + ".html")
    pp = os.path.join(out_dir, fname + ".png")
    open(hp, "w").write(doc)
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu",
                    "--hide-scrollbars", "--force-device-scale-factor=2",
                    f"--window-size=1000,{height}", f"--screenshot={pp}",
                    f"file://{hp}"], capture_output=True)
    os.remove(hp)
    print(f"[+] {pp}")


def main():
    ev = sys.argv[1] if len(sys.argv) > 1 else "evidence"
    out = sys.argv[2] if len(sys.argv) > 2 else "figures"
    cwd = os.path.dirname(os.path.abspath(ev)) or "."
    os.makedirs(out, exist_ok=True)
    out = os.path.abspath(out)
    for fname, title, cmd in STEPS:
        render(fname, title, cmd, run(cmd, cwd), out)


if __name__ == "__main__":
    main()
