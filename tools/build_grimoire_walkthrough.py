#!/usr/bin/env python3
"""
Assemble a WORKING-DRAFT Grimoire walkthrough PDF: embeds the investigation
screenshots and fills in only the factual/structural scaffolding (headings,
literal figure captions, evidence citations, timeline, flag-recovery commands).

Analytical prose is intentionally left as [AUTHOR: ...] prompts — per OffSec
rules the author must write the analysis themselves. Renders with chromium.

Usage: python3 build_grimoire_walkthrough.py <figures_dir> <out_pdf>
"""
import base64
import os
import subprocess
import sys

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def img(fig_dir, name):
    p = os.path.join(fig_dir, name)
    b = base64.b64encode(open(p, "rb").read()).decode()
    return f'<img src="data:image/png;base64,{b}"/>'


def main():
    figs = sys.argv[1] if len(sys.argv) > 1 else "grimoire/figures"
    out = sys.argv[2] if len(sys.argv) > 2 else "grimoire/walkthrough-draft.pdf"

    def F(n):
        return img(figs, n)

    html = f"""<!doctype html><html><head><meta charset=utf-8>
<title>Observ Incident — Walkthrough (working draft)</title>
<style>
 body{{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
   line-height:1.5;color:#1a1a1a;max-width:860px;margin:0 auto;padding:24px}}
 h1{{border-bottom:3px solid #38bdf8;padding-bottom:.3rem}}
 h2{{border-bottom:1px solid #ddd;padding-bottom:.2rem;margin-top:2rem}}
 code{{background:#f4f4f6;padding:.1rem .3rem;border-radius:4px;font-size:.9em}}
 pre{{background:#0f172a;color:#e2e8f0;padding:.8rem;border-radius:8px;overflow:auto;font-size:.85em}}
 img{{max-width:100%;border:1px solid #cbd5e1;border-radius:8px;margin:.4rem 0;display:block}}
 .cap{{font-size:.8rem;color:#475569;margin:.2rem 0 1rem}}
 table{{border-collapse:collapse;width:100%;margin:1rem 0}}
 th,td{{border:1px solid #ccc;padding:.4rem .6rem;text-align:left;font-size:.9em}}
 th{{background:#f0f9ff}}
 .author{{background:#fff7ed;border-left:4px solid #fb923c;padding:.6rem .9rem;margin:.6rem 0;
   color:#7c2d12;font-size:.92em}}
 .banner{{background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;padding:.8rem 1rem;color:#7f1d1d}}
 .facts{{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:.6rem 1rem;font-size:.9em}}
 .flag{{color:#b45309;font-weight:bold}}
 @media print{{a{{color:inherit;text-decoration:none}}}}
</style></head><body>

<h1>Observ Incident — Walkthrough</h1>
<div class="banner"><b>WORKING DRAFT.</b> The figures and the factual scaffolding
(captions, citations, timeline, flag recovery) are filled in. Every
<b>[AUTHOR: …]</b> block is yours to write in your own words before submitting.
OffSec does not accept AI-written Grimoire walkthroughs, so the analysis must be
authored by you. Delete this banner and the final "Author-only" appendix before
exporting the version you submit.</div>

<div class="facts">
<b>Lab:</b> Observ Incident (Grimoire, defensive) &middot;
<b>Difficulty:</b> Intermediate (defender's perspective) &middot;
<b>Flags:</b> 2 × <code>OS{{…}}</code><br>
<b>Environment facts (from the evidence):</b> attacker <code>10.10.14.7</code> &middot;
web01 (monitoring portal, external) &middot; internal01 <code>172.20.0.3</code> (internal-only) &middot;
accounts seen: <code>developer</code>, <code>svc_backup</code>.
</div>

<h2>1. Scenario &amp; scope</h2>
<div class="author">[AUTHOR: In 2–4 sentences, state what triggered the
investigation, which hosts are in scope, and what you are being asked to
determine. Use only the provided evidence.]</div>

<h2>2. Evidence inventory</h2>
{F("01_evidence_tree.png")}
<div class="cap">Fig 1 — the triage bundle: web01 and internal01 logs, shell
histories, a recovered module, and a staged file.</div>
<table>
<tr><th>Artifact</th><th>What it is (fact)</th></tr>
<tr><td><code>web01/var/log/apache2/access.log</code></td><td>external HTTP requests to the portal</td></tr>
<tr><td><code>web01/var/log/observ/diag_debug.log</code></td><td>application log of the diagnostics <code>host</code> values</td></tr>
<tr><td><code>web01/var/log/auth.log</code></td><td>SSH authentication and sudo events</td></tr>
<tr><td><code>web01/home/developer/.bash_history</code></td><td>commands run by the developer account</td></tr>
<tr><td><code>web01/tmp/.x/netcheck.py</code></td><td>recovered Python module</td></tr>
<tr><td><code>web01/var/www/html/config.php</code></td><td>application DB configuration</td></tr>
<tr><td><code>internal01/var/log/auth.log</code></td><td>SSH (publickey) + sudo events</td></tr>
<tr><td><code>internal01/home/svc_backup/.bash_history</code></td><td>commands run by svc_backup</td></tr>
<tr><td><code>internal01/tmp/.exfil/stage.txt</code></td><td>file staged by the attacker</td></tr>
</table>
<div class="author">[AUTHOR: one line on your triage approach — which artifact
you started with and why.]</div>

<h2>3. Initial access (web01)</h2>
{F("02_access_log.png")}
<div class="cap">Fig 2 — access.log: requests from <code>10.10.14.7</code> hit
<code>/robots.txt</code>, repeated <code>POST /index.php</code>, then
<code>/monitor/dashboard.php</code> and several <code>POST /monitor/diag.php</code>.</div>
{F("03_diag_debug.png")}
<div class="cap">Fig 3 — diag_debug.log: the <code>host</code> parameter carries
shell metacharacters (<code>127.0.0.1; id</code>, <code>; cat …config.php</code>,
a base64 <code>echo … | base64 -d</code>).</div>
<div class="author">[AUTHOR: explain what Fig 2–3 show — the source IP, the
login attempts vs. the successful dashboard access, and how the <code>host</code>
field on <code>/monitor/diag.php</code> gives command execution. Name the
vulnerable parameter.]</div>

<h2>4. Credential reuse &amp; SSH foothold</h2>
{F("05_authlog_web01.png")}
<div class="cap">Fig 4 — auth.log: <code>Accepted password for developer from
10.10.14.7</code>, followed by a sudo event (note the <code>ENV=PYTHONPATH=…</code>).</div>
<div class="author">[AUTHOR: connect the DB password in <code>config.php</code>
to the <code>developer</code> SSH login — explain the credential reuse and why
reading a world-readable config beats brute force.]</div>

<h2>5. Privilege escalation on web01 (PYTHONPATH hijack)</h2>
{F("06_bash_developer.png")}
<div class="cap">Fig 5 — developer history: <code>sudo -l</code>, a module written to
<code>/tmp/.x/netcheck.py</code>, then <code>sudo PYTHONPATH=/tmp/.x … check.py</code>.</div>
{F("07_netcheck.png")}
<div class="cap">Fig 6 — the recovered <code>netcheck.py</code>: <code>os.setuid(0)</code>
then a shell.</div>
<div class="author">[AUTHOR: explain the technique — the allowed sudo health
check imports <code>netcheck</code>, sudo preserves <code>PYTHONPATH</code>, so a
planted module runs as root. Map it to MITRE T1548.003 / T1574.007.]</div>
<h3>First flag</h3>
{F("04_decode_flag1.png")}
<div class="cap">Fig 7 — base64-decoding the staged marker from diag_debug.log.</div>
<pre>grep 'base64 -d' evidence/web01/var/log/observ/diag_debug.log \\
  | grep -oE '[A-Za-z0-9+/=]{{20,}}' | base64 -d
<span class="flag">OS{{w3b01_rc3_d14g_c0mm4nd_1nj}}</span></pre>

<h2>6. Lateral movement / pivot to internal01</h2>
{F("08_authlog_internal.png")}
<div class="cap">Fig 8 — internal01 auth.log: <code>Accepted publickey for
svc_backup from 172.20.0.2</code> (web01's internal address), then a sudo event.</div>
<div class="author">[AUTHOR: explain how the attacker found the internal host and
the svc_backup key on web01 (see developer history / <code>~/.ssh</code>), and
that the SSH into 172.20.0.3 comes <em>from</em> web01 — an east-west pivot.]</div>

<h2>7. Privilege escalation on internal01 (sudo tar)</h2>
{F("09_bash_svcbackup.png")}
<div class="cap">Fig 9 — svc_backup history: <code>sudo -l</code>, then
<code>sudo tar … --checkpoint-action=exec=/bin/sh</code>, then staging under
<code>/tmp/.exfil</code>.</div>
<div class="author">[AUTHOR: explain the GTFOBins <code>sudo tar</code> abuse via
<code>--checkpoint-action</code>. Map to MITRE T1548.003.]</div>
<h3>Second flag</h3>
{F("10_flag2.png")}
<div class="cap">Fig 10 — the staged file left on internal01.</div>
<pre>cat evidence/internal01/tmp/.exfil/stage.txt
<span class="flag">OS{{1nt3rn4l_r00t_sud0_tar_pivot}}</span></pre>

<h2>8. Timeline (facts)</h2>
<table>
<tr><th>Time (UTC)</th><th>Host</th><th>Event</th></tr>
<tr><td>02:14:02</td><td>web01</td><td>recon: <code>GET /robots.txt</code> from 10.10.14.7</td></tr>
<tr><td>02:14:20–25</td><td>web01</td><td>repeated <code>POST /index.php</code> → dashboard (auth bypass)</td></tr>
<tr><td>02:15:01–16:12</td><td>web01</td><td>command injection via <code>host</code> on <code>diag.php</code></td></tr>
<tr><td>02:17:03</td><td>web01</td><td>SSH <code>developer</code> from 10.10.14.7 (reused password)</td></tr>
<tr><td>02:18:22</td><td>web01</td><td>sudo <code>python3 check.py</code> with <code>PYTHONPATH=/tmp/.x</code> → root</td></tr>
<tr><td>02:19:40</td><td>internal01</td><td>SSH publickey <code>svc_backup</code> from 172.20.0.2 (pivot)</td></tr>
<tr><td>02:21:10</td><td>internal01</td><td>sudo <code>tar --checkpoint-action</code> → root; staging in /tmp/.exfil</td></tr>
</table>

<h2>9. Detections &amp; lessons</h2>
<div class="author">[AUTHOR: write your own recommendations. Ideas to develop:
alert on shell metacharacters in diagnostic inputs; alert on
<code>sudo</code> with <code>ENV=PYTHONPATH/LD_*</code>; alert on
<code>sudo tar/find/vi --checkpoint-action/-exec</code>; correlate one source IP
across web/auth/downstream SSH; flag SSH from a DMZ host into an internal
segment. See <code>artifacts.zip/mitre-attack.md</code>.]</div>

<hr>
<h2>Author-only appendix — DELETE before submitting</h2>
<div class="facts">
Reference answers (full citations in <code>artifacts.zip/answer-key.md</code>):<br>
attacker_ip = 10.10.14.7 &middot; cmdi_param = host &middot;
reused_account = developer &middot; privesc_web01 = PYTHONPATH hijack &middot;
flag_web01 = OS{{w3b01_rc3_d14g_c0mm4nd_1nj}} &middot; pivot_ip = 172.20.0.3 &middot;
gtfobins_binary = tar &middot; flag_internal = OS{{1nt3rn4l_r00t_sud0_tar_pivot}}
</div>
</body></html>"""

    htmlpath = "/tmp/claude-0/gwt_draft.html"
    with open(htmlpath, "w") as f:
        f.write(html)
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu",
                    "--no-pdf-header-footer", f"--print-to-pdf={out}",
                    f"file://{htmlpath}"], capture_output=True)
    print("[+] wrote", out)


if __name__ == "__main__":
    main()
