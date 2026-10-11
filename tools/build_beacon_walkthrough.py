#!/usr/bin/env python3
"""
Assemble a WORKING-DRAFT Beacon Incident walkthrough PDF: embeds the figures and
fills only factual/structural scaffolding (captions, citations, timeline, flag
recovery). Analytical prose is left as [AUTHOR: ...] prompts — per OffSec rules
the author writes the analysis themselves. Chromium renders the PDF.

Usage: python3 build_beacon_walkthrough.py <figures_dir> <out_pdf>
"""
import base64
import os
import sys

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def main():
    figs = sys.argv[1] if len(sys.argv) > 1 else "grimoire2/figures"
    out = sys.argv[2] if len(sys.argv) > 2 else "grimoire2/walkthrough-draft.pdf"

    def F(name, cap):
        b = base64.b64encode(open(os.path.join(figs, name), "rb").read()).decode()
        return f'<img src="data:image/png;base64,{b}"/><div class="cap">{cap}</div>'

    html = f"""<!doctype html><html><head><meta charset=utf-8>
<title>Beacon Incident — Walkthrough (working draft)</title>
<style>
 body{{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.5;
   color:#1a1a1a;max-width:860px;margin:0 auto;padding:24px}}
 h1{{border-bottom:3px solid #38bdf8;padding-bottom:.3rem}}
 h2{{border-bottom:1px solid #ddd;padding-bottom:.2rem;margin-top:1.8rem}}
 code{{background:#f4f4f6;padding:.1rem .3rem;border-radius:4px;font-size:.88em}}
 pre{{background:#0f172a;color:#e2e8f0;padding:.8rem;border-radius:8px;overflow:auto;font-size:.82em}}
 img{{max-width:100%;border:1px solid #cbd5e1;border-radius:8px;margin:.5rem 0 .2rem;display:block}}
 .cap{{font-size:.8rem;color:#475569;margin:0 0 1rem;font-style:italic}}
 table{{border-collapse:collapse;width:100%;margin:1rem 0}}
 th,td{{border:1px solid #ccc;padding:.4rem .6rem;text-align:left;font-size:.9em}}
 th{{background:#f0f9ff}}
 .author{{background:#fff7ed;border-left:4px solid #fb923c;padding:.6rem .9rem;margin:.6rem 0;
   color:#7c2d12;font-size:.92em}}
 .banner{{background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;padding:.8rem 1rem;color:#7f1d1d}}
 .facts{{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:.6rem 1rem;font-size:.9em}}
 .flag{{color:#b45309;font-weight:bold}}
</style></head><body>

<h1>Beacon Incident — Walkthrough</h1>
<div class="banner"><b>WORKING DRAFT.</b> Figures and factual scaffolding (captions, citations,
timeline, flag recovery) are filled in. Every <b>[AUTHOR: …]</b> block is yours to write in your own
words before submitting — OffSec does not accept AI-written Grimoire walkthroughs. Delete this banner
and the final "Author-only" appendix before exporting the version you submit.</div>

<div class="facts">
<b>Lab:</b> Beacon Incident (Grimoire, defensive) &middot; <b>Difficulty:</b> Intermediate &middot;
<b>Flags:</b> 2 × <code>OS{{…}}</code><br>
<b>Environment:</b> Northwind Trading &middot; host <code>FIN-WKS-07</code> &middot; user
<code>NORTHWIND\\j.morgan</code> &middot; C2 <code>cdn.lifestyle-deals.net</code> (203.0.113.45).
</div>

<h2>1. Scenario &amp; scope</h2>
<div class="author">[AUTHOR: 2–4 sentences — what alerted, which host/user, and what you are asked to
determine. Use only the provided evidence.]</div>

<h2>2. Evidence inventory</h2>
{F("01_tree.png", "Fig 1 — the triage bundle: email, Sysmon, PowerShell 4104, Security 4688/4624, scheduled task, EDR file-access, and proxy logs.")}
<div class="author">[AUTHOR: one line on your triage order and why.]</div>

<h2>3. Delivery &amp; initial execution</h2>
{F("02_phish.png", "Fig 2 — the phishing email: spoofed sender, SPF/DMARC fail, macro-enabled attachment.")}
{F("03_macro.png", "Fig 3 — static triage of the macro: Document_Open launches hidden encoded PowerShell.")}
{F("04_sysmon.png", "Fig 4 — Sysmon EID 1: WINWORD → cmd → powershell -enc, then schtasks.")}
<div class="author">[AUTHOR: explain the lure and the authentication failures, then the process tree —
Office spawning cmd/powershell with <code>-enc -w hidden -nop</code>. Name the techniques (T1566.001,
T1204.002, T1059.001).]</div>
<h3>First flag</h3>
{F("05_decode.png", "Fig 5 — decoding the -enc value (Base64 of UTF-16LE).")}
<pre>B=$(grep -oE -- '-enc [A-Za-z0-9+/=]+' evidence/FIN-WKS-07/sysmon_process_creation.log \\
      | head -1 | awk '{{print $2}}')
python3 -c "import base64,sys;print(base64.b64decode(sys.argv[1]).decode('utf-16-le'))" "$B"
<span class="flag">OS{{m4cr0_enc_p0w3rsh3ll_dr0pp3r}}</span></pre>

<h2>4. Command &amp; control / second stage</h2>
{F("06_4104.png", "Fig 6 — PowerShell 4104 script-block logging (decoded content; payload redacted in this bundle).")}
<div class="author">[AUTHOR: explain what script-block logging revealed and the C2 indicator; tie it to
the proxy evidence in §7. Techniques: T1027/T1140, T1105, T1071.001.]</div>

<h2>5. Persistence</h2>
{F("08_schtask.png", "Fig 7 — scheduled task masquerading as a Microsoft Edge update, every 10 minutes.")}
<div class="author">[AUTHOR: explain the scheduled-task persistence and the masquerading name
(T1053.005, T1036.004).]</div>

<h2>6. Credential access</h2>
{F("07_credaccess.png", "Fig 8 — EDR: powershell.exe reading the Chrome credential store (Login Data / cookies).")}
<div class="author">[AUTHOR: explain why a non-browser process reading the browser credential store is
suspicious (T1555.003).]</div>

<h2>7. Collection &amp; exfiltration</h2>
{F("09_proxy.png", "Fig 9 — proxy log: beacon GETs to /api/task and a 5 MB POST to /api/upload.")}
<div class="author">[AUTHOR: explain the beaconing cadence and the large upload to the C2 domain
(T1074.001 staging, T1041 exfil over C2).]</div>
<h3>Second flag</h3>
{F("10_flag2.png", "Fig 10 — the staged exfil manifest left under C:\\Users\\Public\\.stage.")}
<pre>cat evidence/FIN-WKS-07/C_Users_Public/.stage/exfil_manifest.txt
<span class="flag">OS{{br0ws3r_cr3ds_b34c0n_3xf1l}}</span></pre>

<h2>8. Timeline (facts)</h2>
<table>
<tr><th>Time (UTC)</th><th>Event</th></tr>
<tr><td>09:11</td><td>phishing email delivered (SPF/DMARC fail)</td></tr>
<tr><td>09:14:52</td><td>user opens <code>Invoice_Q3.docm</code> (WINWORD)</td></tr>
<tr><td>09:15:03</td><td>WINWORD → cmd → <code>powershell -enc</code> (hidden)</td></tr>
<tr><td>09:15:20</td><td>second stage pulled from C2 (<code>GET /u/x.ps1</code>)</td></tr>
<tr><td>09:16:40</td><td>scheduled task persistence created</td></tr>
<tr><td>09:18:30</td><td>browser credential store accessed</td></tr>
<tr><td>09:20 → 09:41</td><td>beacon GETs; 5 MB POST upload to C2</td></tr>
</table>

<h2>9. Detections &amp; lessons</h2>
<div class="author">[AUTHOR: write your own recommendations. Ideas: alert on Office spawning
cmd/powershell; <code>-enc -w hidden</code>; Script Block Logging + long Base64; <code>schtasks</code>
from powershell + masquerading names; non-browser processes reading browser credential stores;
beacon/large POST to newly-registered domains. See <code>artifacts.zip/mitre-attack.md</code>.]</div>

<hr>
<h2>Author-only appendix — DELETE before submitting</h2>
<div class="facts">Reference answers (full citations in <code>artifacts.zip/answer-key.md</code>):<br>
phish_sender = billing@vendor-portal-support.com &middot; victim = FIN-WKS-07 / j.morgan &middot;
initial_exec = encoded PowerShell &middot; flag1 = OS{{m4cr0_enc_p0w3rsh3ll_dr0pp3r}} &middot;
persistence = scheduled task &middot; cred_access = browser credential store &middot;
c2_domain = cdn.lifestyle-deals.net &middot; flag2 = OS{{br0ws3r_cr3ds_b34c0n_3xf1l}}
</div>
</body></html>"""

    hp = "/tmp/claude-0/beacon_wt.html"
    open(hp, "w").write(html)
    import subprocess
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu",
                    "--no-pdf-header-footer", f"--print-to-pdf={out}", f"file://{hp}"],
                   capture_output=True)
    print("[+] wrote", out)


if __name__ == "__main__":
    main()
