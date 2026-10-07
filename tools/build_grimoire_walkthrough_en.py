#!/usr/bin/env python3
"""
Render the English Observ Incident walkthrough PDF (faithful translation of the
author's Uzbek analysis), embedding the investigation screenshots. Typo
'GFTFOBins' corrected to 'GTFOBins'. Chromium renders the PDF.

Usage: python3 build_grimoire_walkthrough_en.py <figures_dir> <out_pdf>
"""
import base64
import os
import subprocess
import sys

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def main():
    figs = sys.argv[1] if len(sys.argv) > 1 else "grimoire/figures"
    out = sys.argv[2] if len(sys.argv) > 2 else "grimoire/walkthrough-en.pdf"

    def F(name, cap):
        p = os.path.join(figs, name)
        b = base64.b64encode(open(p, "rb").read()).decode()
        return (f'<img src="data:image/png;base64,{b}"/>'
                f'<div class="cap">{cap}</div>')

    def mitre(*ids):
        return ('<div class="mitre">' +
                "".join(f"<span>{i}</span>" for i in ids) + "</div>")

    html = f"""<!doctype html><html><head><meta charset=utf-8>
<title>Observ Incident — Walkthrough</title>
<style>
 body{{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
   line-height:1.55;color:#1a1a1a;max-width:860px;margin:0 auto;padding:24px}}
 h1{{border-bottom:3px solid #38bdf8;padding-bottom:.3rem}}
 h2{{border-bottom:1px solid #ddd;padding-bottom:.2rem;margin-top:1.9rem}}
 h3{{margin-top:1.3rem}}
 code{{background:#f4f4f6;padding:.1rem .3rem;border-radius:4px;font-size:.88em}}
 pre{{background:#0f172a;color:#e2e8f0;padding:.8rem;border-radius:8px;overflow:auto;font-size:.82em}}
 img{{max-width:100%;border:1px solid #cbd5e1;border-radius:8px;margin:.5rem 0 .2rem;display:block}}
 .cap{{font-size:.8rem;color:#475569;margin:0 0 1rem;font-style:italic}}
 table{{border-collapse:collapse;width:100%;margin:1rem 0}}
 th,td{{border:1px solid #ccc;padding:.4rem .6rem;text-align:left;font-size:.9em;vertical-align:top}}
 th{{background:#f0f9ff}}
 .box{{background:#eff6ff;border-left:4px solid #3b82f6;padding:.6rem .9rem;margin:.7rem 0;font-size:.93em}}
 .facts{{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:.6rem 1rem;font-size:.9em}}
 .flag{{color:#b45309;font-weight:bold}}
 .mitre{{margin:.5rem 0}}
 .mitre span{{display:inline-block;background:#fff1f2;border:1px solid #fecdd3;color:#9f1239;
   border-radius:5px;padding:.1rem .45rem;margin:.15rem .3rem .15rem 0;font-family:monospace;font-size:.76rem}}
 ul{{margin:.4rem 0 .6rem}} li{{margin:.25rem 0}}
</style></head><body>

<h1>Observ Incident — Walkthrough</h1>
<div class="facts">
<b>Lab:</b> Observ Incident (Grimoire, defensive) &middot;
<b>Difficulty:</b> Intermediate (defender's perspective) &middot;
<b>Flags:</b> 2 × <code>OS{{…}}</code><br>
<b>Environment facts (from the evidence):</b> attacker <code>10.10.14.7</code> &middot;
web01 (monitoring portal, external) &middot; internal01 <code>172.20.0.3</code> (internal-only) &middot;
accounts observed: <code>developer</code>, <code>svc_backup</code>.<br>
<span style="color:#64748b">Defensive walkthrough — evidence-based.</span>
</div>

<h2>1. Scenario and scope</h2>
<p>The investigation began when the external monitoring portal <b>web01</b>'s Apache
<code>access.log</code> showed — from a single source, <code>10.10.14.7</code> — recon of
<code>robots.txt</code>, login attempts on <code>/index.php</code>, and a sequence of POSTs to
<code>/monitor/diag.php</code> within a short window. The scope covers two hosts: the externally
facing <b>web01</b> (monitoring portal) and the internal-segment-only <b>internal01</b>
(<code>172.20.0.3</code>). The evidence provided is HTTP/SSH logs from both hosts, system logs,
<code>.bash_history</code> files, the <code>netcheck.py</code> module recovered on web01, and the
<code>stage.txt</code> file on internal01. The objective is to reconstruct the intrusion step by
step (initial access → credential reuse → privilege escalation → internal lateral movement), tie
each step to concrete evidence, and recover both flag values while determining the scope of impact.</p>

<h2>2. Evidence inventory</h2>
{F("01_evidence_tree.png", "Fig 1 — the triage bundle: web01 and internal01 logs, shell histories, a recovered module, and a staged file.")}
<table>
<tr><th>Artifact</th><th>What it is (fact)</th></tr>
<tr><td><code>web01/var/log/apache2/access.log</code></td><td>external HTTP requests to the portal</td></tr>
<tr><td><code>web01/var/log/observ/diag_debug.log</code></td><td>application log of the diagnostics <code>host</code> values</td></tr>
<tr><td><code>web01/var/log/auth.log</code></td><td>SSH authentication and sudo events</td></tr>
<tr><td><code>web01/home/developer/.bash_history</code></td><td>commands run by the developer account</td></tr>
<tr><td><code>web01/tmp/.x/netcheck.py</code></td><td>recovered Python module (planted by the attacker)</td></tr>
<tr><td><code>web01/var/www/html/config.php</code></td><td>application database configuration</td></tr>
<tr><td><code>internal01/var/log/auth.log</code></td><td>SSH (publickey) + sudo events</td></tr>
<tr><td><code>internal01/home/svc_backup/.bash_history</code></td><td>commands run by svc_backup</td></tr>
<tr><td><code>internal01/tmp/.exfil/stage.txt</code></td><td>file staged by the attacker (exfil staging)</td></tr>
</table>
<p><b>Triage approach.</b> I started with <code>web01/var/log/apache2/access.log</code>, because it
is the only externally visible surface and chronologically shows the intrusion's entry point first:
the source IP found there is the key that correlates events across every host. From there I moved to
<code>diag_debug.log</code> to see which parameter carried the commands, then to <code>auth.log</code>
and the <code>.bash_history</code> files, reconstructing the cause and effect of each step.</p>

<h2>3. Initial access (web01)</h2>
{F("02_access_log.png", "Fig 2 — access.log: requests from the attacker IP (10.10.14.7) against diag.php and index.php.")}
<h3>3.1 What it shows</h3>
<p>All requests come from a single source — <code>10.10.14.7</code>. They begin with a recon pattern:
<code>GET /robots.txt</code> (200) — the attacker enumerates paths automatically or manually. At
<code>02:14:20</code> and <code>02:14:25</code> there are two POSTs to <code>/index.php</code>: the first
returns 200 (the login page re-rendered — a failed attempt), the second 302 (a redirect). The 200 → 302
transition shows that a session was granted at the HTTP layer, i.e. authentication succeeded (flagged as
an <i>authentication bypass</i> in the timeline). From this point the attacker holds access to the
authenticated panel.</p>

<h3>3.2 Command injection in the diagnostics function</h3>
{F("03_diag_debug.png", "Fig 3 — diag_debug.log: the host parameter carries shell metacharacters.")}
<p>The <code>diag_debug.log</code> is the most important technical evidence. The entry at
<code>02:14:48</code> with <code>host=8.8.8.8</code> is a legitimate example: an external IP as input. But
in the following entries the target carries <code>;</code> (a semicolon) and arbitrary shell commands:</p>
<ul>
<li><code>127.0.0.1; id</code> — identify the executing user (discovery);</li>
<li><code>127.0.0.1; uname -a</code> — OS/kernel (discovery);</li>
<li><code>127.0.0.1; cat /var/www/html/config.php</code> — <b>reading the configuration</b>, i.e. access to secrets;</li>
<li><code>127.0.0.1; echo &lt;base64&gt; | base64 -d &gt; /tmp/.obs_marker</code> — staging an encoded value on the host (this later becomes the first flag).</li>
</ul>
<p>The vulnerable point is the <code>host</code> parameter on <code>/monitor/diag.php</code>. The
application passes this value into a shell command (for example a <code>ping</code> or similar diagnostic)
without any sanitisation; any command placed after <code>;</code> runs with web-server privileges. This is
classic <b>OS Command Injection</b>.</p>
{mitre("T1190 Exploit Public-Facing Application", "T1059.004 Unix Shell", "T1082 System Information Discovery", "T1552.001 Credentials In Files")}
<div class="box"><b>Why it matters:</b> the injection yields two things at once — command execution on the
host (RCE) and reading the configuration file. The session opened in the source (the <code>index.php</code>
bypass) is what exposed the diagnostics function to the external attacker.</div>

<h2>4. Credential reuse and SSH foothold</h2>
{F("05_authlog_web01.png", "Fig 4 — auth.log: password SSH login for developer, then sudo (note ENV=PYTHONPATH).")}
<p>About a minute after reading <code>config.php</code>, an SSH login as <b>developer</b> from the same
external IP (<code>10.10.14.7</code>) appears at <code>02:17:03</code>. This is <b>credential reuse</b>: the
DB password obtained through the injection was reused as the <code>developer</code> system account's
password. The source IP ties the web events and the SSH login into one chain.</p>
<p><b>Reading a config beats brute force.</b> Because <code>config.php</code> is a web-server-readable
file, the password can be obtained in a single command — quietly (a handful of requests), with no lockout
and no <code>Failed password</code> noise, so the detection likelihood is near zero. That is why the log
shows not "many failed passwords" but a single successful login — which is itself a strong detection
signal.</p>
{mitre("T1552.001 Credentials In Files", "T1078 Valid Accounts", "T1021.004 Remote Services: SSH")}

<h2>5. Privilege escalation on web01 (PYTHONPATH hijack)</h2>
{F("06_bash_developer.png", "Fig 5 — developer history: sudo -l, writing the module to /tmp/.x, then sudo with PYTHONPATH.")}
{F("07_netcheck.png", "Fig 6 — the recovered netcheck.py: os.setuid(0) then a shell.")}
<h3>5.1 Technique</h3>
<p>The <code>.bash_history</code> exposes the whole logic:</p>
<ul>
<li><code>sudo -l</code> — enumerate allowed commands; here <code>developer</code> may run
<code>/usr/bin/python3 /opt/health/check.py</code> passwordless.</li>
<li><code>mkdir -p /tmp/.x</code> — create a writable directory.</li>
<li><code>echo "import os; os.setuid(0); os.system('/bin/bash')" &gt; /tmp/.x/netcheck.py</code> — plant a
malicious file named after the <code>netcheck</code> module that the health check imports.</li>
<li><code>sudo PYTHONPATH=/tmp/.x /usr/bin/python3 /opt/health/check.py</code> — the command is run under
sudo, deliberately carrying <code>PYTHONPATH</code>.</li>
</ul>
<p>This is the <b>PYTHONPATH hijack</b> technique. In this configuration sudo does not strip
<code>PYTHONPATH</code> (unless <code>env_reset</code>/<code>env_keep</code> are set to do so), so when
Python resolves the import it searches <code>PYTHONPATH=/tmp/.x</code> first, loads the attacker's module,
and <code>os.system('/bin/bash')</code> opens a root shell. The <code>auth.log</code> records
<code>ENV=PYTHONPATH=/tmp/.x</code> at <code>02:18:22</code>, after which <code>cat /root/proof.txt</code>
and the following steps run as root.</p>
{mitre("T1548.003 Abuse Elevation Control: Sudo", "T1574.007 Hijack Execution Flow: Path Interception", "T1059.006 Command and Scripting Interpreter: Python")}
<div class="box"><b>Detection gold signal:</b> <code>ENV=PYTHONPATH=</code> (or <code>LD_PRELOAD</code>/
<code>LD_LIBRARY_PATH</code>) appearing in a sudo event — unusual in normal operation, and almost always
privilege escalation.</div>

<h3>First flag</h3>
{F("04_decode_flag1.png", "Fig 7 — base64-decoding the staged marker from diag_debug.log.")}
<p>The first flag was not handed out at the start of the chain — the attacker staged it himself, base64-encoded,
in <code>diag_debug.log</code>. Extracting the base64 from the log line and decoding it yields the flag; its
text summarises the finding (<i>web01 rce diag command injection</i>):</p>
<pre>grep 'base64 -d' evidence/web01/var/log/observ/diag_debug.log \\
  | grep -oE '[A-Za-z0-9+/=]{{20,}}' | base64 -d
<span class="flag">OS{{w3b01_rc3_d14g_c0mm4nd_1nj}}</span></pre>

<h2>6. Lateral movement / pivot to internal01</h2>
{F("08_authlog_internal.png", "Fig 8 — internal01 auth.log: publickey login for svc_backup from 172.20.0.2 (web01), then sudo.")}
<p>After gaining root on web01, the <code>.bash_history</code> shows the attacker running
<code>cat ~/.ssh/config</code> and <code>cat ~/.ssh/svc_backup_id_ed25519</code> — an SSH config pointing to
the internal host (internal01, <code>172.20.0.3</code>) and a private key. Using that key, at
<code>02:19:40</code> he logged into internal01 as <b>svc_backup</b>. The most important detail is the source
address: <code>from 172.20.0.2</code>, i.e. web01's internal interface. The intrusion is now no longer coming
from outside the perimeter — it is moving <b>east-west</b>, from the DMZ/web layer into the internal segment.
web01 acted as the <b>pivot</b>. The attacker then ran <code>cat /root/proof.txt</code> and staging commands,
leading to the next step.</p>
{mitre("T1021.004 Remote Services: SSH", "T1552.004 Unsecured Credentials: Private Keys", "T1078 Valid Accounts")}
<div class="box"><b>Why it matters:</b> the internal segment is treated as "internal-only" and trusted, but a
compromised web01 sitting in that segment can reach it directly. Even with segmentation in place, host-to-host
trust and long-lived static keys undermine that trust.</div>

<h2>7. Privilege escalation on internal01 (sudo tar)</h2>
{F("09_bash_svcbackup.png", "Fig 9 — svc_backup history: sudo -l, then sudo tar --checkpoint-action=exec=/bin/sh, then staging in /tmp/.exfil.")}
<h3>7.1 Technique</h3>
<p>The svc_backup history starts with recon — <code>id</code> / <code>hostname</code> / <code>ip addr</code> —
then <code>sudo -l</code> reveals that <code>tar</code> is runnable passwordless. The attacker used the
<b>GTFOBins</b> <code>tar</code> technique:</p>
<pre>sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh</pre>
<p><code>--checkpoint-action</code> runs an arbitrary command at the first checkpoint. The result is a
<code>/bin/sh</code> opened as <b>root</b> (auth.log <code>02:21:10 ... COMMAND=/usr/bin/tar ...</code> and
<code>session opened for user root</code>). The attacker then:</p>
<ul>
<li><code>cat /root/proof.txt</code> — confirm root access;</li>
<li><code>mkdir -p /tmp/.exfil</code> — create a hidden staging directory (T1074.001 Data Staged);</li>
<li><code>echo OS{{...}} &gt; /tmp/.exfil/stage.txt</code> — write the second flag;</li>
<li><code>tar czf /tmp/.exfil/backup.tgz /root /etc/shadow</code> — archive the most sensitive files
(the root directory and password hashes) for exfiltration (T1003.008 <code>/etc/passwd</code> and
<code>/etc/shadow</code>).</li>
</ul>
{mitre("T1548.003 Abuse Elevation Control: Sudo", "T1059.004 Unix Shell", "T1003.008 /etc/passwd and /etc/shadow", "T1074.001 Local Data Staging")}

<h3>Second flag</h3>
{F("10_flag2.png", "Fig 10 — the staged file left on internal01.")}
<p>The second flag is in <code>/tmp/.exfil</code> — the file staged after gaining root. Its text summarises
the whole chain (<i>internal root sudo tar pivot</i>): root on the internal host via <code>sudo tar</code>,
reached through the pivot.</p>
<pre>cat evidence/internal01/tmp/.exfil/stage.txt
<span class="flag">OS{{1nt3rn4l_r00t_sud0_tar_pivot}}</span></pre>

<h2>8. Timeline (facts)</h2>
<table>
<tr><th>Time (UTC)</th><th>Host</th><th>Event</th></tr>
<tr><td>02:14:02</td><td>web01</td><td>recon: <code>GET /robots.txt</code> from 10.10.14.7</td></tr>
<tr><td>02:14:20–25</td><td>web01</td><td>repeated <code>POST /index.php</code> → dashboard (authentication bypass)</td></tr>
<tr><td>02:15:01–16:12</td><td>web01</td><td>command injection via <code>host</code> on <code>diag.php</code></td></tr>
<tr><td>02:17:03</td><td>web01</td><td>SSH as <code>developer</code> from 10.10.14.7 (reused password)</td></tr>
<tr><td>02:18:22</td><td>web01</td><td>sudo <code>python3 check.py</code> with <code>PYTHONPATH=/tmp/.x</code> → root</td></tr>
<tr><td>02:19:40</td><td>internal01</td><td>SSH publickey as <code>svc_backup</code> from 172.20.0.2 (pivot)</td></tr>
<tr><td>02:21:10</td><td>internal01</td><td>sudo <code>tar --checkpoint-action</code> → root; staging in /tmp/.exfil</td></tr>
</table>

<h2>9. Detections and lessons</h2>
<p>The following recommendations map to each stage of the attack chain — concrete, actionable detections and
fixes, ordered top to bottom.</p>

<h3>9.1 Detect shell metacharacters in diagnostic inputs (T1190 / T1059.004)</h3>
<ul>
<li>Alert, in a WAF or the app, on shell metacharacters (<code>; | &amp;&amp; || $() `` &gt;</code>) in
<code>host</code>/<code>ip</code>/<code>target</code>-style parameters.</li>
<li>Validate input with a strict allow-list: accept only a valid IP/hostname; reject and log everything else.</li>
<li>Best fixed in the app: do not build a shell string at all — use <code>subprocess</code> with an argument
array, or a pure library call.</li>
<li><b>Signal:</b> <code>host=</code> values in <code>diag_debug.log</code> that do not match an IP/hostname
regex → high-confidence alert.</li>
</ul>

<h3>9.2 Detect environment injection in sudo (T1548.003 / T1574.007)</h3>
<ul>
<li><b>Alert:</b> <code>ENV=PYTHONPATH=</code> / <code>LD_PRELOAD=</code> / <code>LD_LIBRARY_PATH=</code> /
<code>PERL5LIB=</code> / <code>BASH_ENV=</code> in sudo events — almost always privilege escalation.</li>
<li>Ensure sudoers has <code>env_reset</code> on and <code>env_keep</code> minimal; set <code>secure_path</code>.</li>
<li>In general, avoid making interpreters (python, perl, bash) sudo-runnable — they are bypassable via
reflection/imports.</li>
</ul>

<h3>9.3 Detect GTFOBins patterns (T1548.003)</h3>
<ul>
<li>Alert on these patterns in sudo/process command lines: <code>tar --checkpoint-action</code>,
<code>find -exec</code>, <code>vi/vim -c</code>, <code>less</code>/<code>man</code> then a shell,
<code>awk 'BEGIN{{system(...)}}'</code>, <code>env</code>, <code>nmap --interactive</code>.</li>
<li>Keep sudo rights least-privilege: grant specific commands <i>and arguments</i>, not whole binaries.</li>
</ul>

<h3>9.4 Correlate a single source IP across web + auth + downstream SSH (T1078 / T1021.004)</h3>
<ul>
<li>In the SIEM, join one IP that appears in different log types in the same window: <code>access.log</code>
(10.10.14.7), SSH in <code>auth.log</code> (same IP), then internal-segment SSH (source = the compromised host).</li>
<li>In a short window, "web interaction → SSH login" is a classic signal.</li>
<li>Alert with a first-seen rule for SSH logins ("this user logging in from this IP for the first time").</li>
</ul>

<h3>9.5 Alert on SSH from the DMZ/web layer into the internal segment (lateral movement)</h3>
<ul>
<li>Alert/block SSH from DMZ/web hosts (web01) into internal hosts (internal01, <code>172.20.0.2 →</code>) —
abnormal in normal operation.</li>
<li>Make east-west traffic default-deny; allow only the required source→destination pairs.</li>
</ul>

<h3>9.6 Secrets and credential hygiene</h3>
<ul>
<li>Files like <code>config.php</code> must not be web-server-readable: restrict permissions
(<code>640</code>/<code>600</code>, owner = app user), deny reads from outside the web root; never store literal
passwords in code — use a secret manager.</li>
<li><b>Do not reuse passwords:</b> the app/DB password must not equal an OS account password; use unique,
random passwords and a password manager.</li>
<li>Do not keep SSH private keys openly in users' home directories; use a passphrase/FIDO for keys, short-lived
certificates or an SSH CA; remove unused keys.</li>
</ul>

<h3>9.7 File integrity and exfil/staging detection</h3>
<ul>
<li>Set FIM on <code>/etc/shadow</code>, <code>/root</code>, sudoers and the SSH directories — an unauthorised
read/write is an immediate signal.</li>
<li>Alert on hidden directories under <code>/tmp</code>, <code>/var/tmp</code>, <code>/dev/shm</code>
(<code>/tmp/.x</code>, <code>/tmp/.exfil</code>) and on archives (<code>.tgz</code>, <code>.tar.gz</code>).</li>
<li>Correlate "large archive creation + a subsequent outbound connection" (exfiltration).</li>
</ul>

<h3>9.8 Log centralisation and process</h3>
<ul>
<li>Ship logs from all hosts to the SIEM in real time — a local attacker with root can delete local logs
(in this lab the logs were preserved, but assume the worst in production).</li>
<li>Write automatic anomaly-detection rules for web and SSH logs and test them regularly (purple-team).</li>
</ul>

<h3>9.9 MITRE ATT&CK summary</h3>
<table>
<tr><th>Stage</th><th>Technique</th><th>ATT&amp;CK</th></tr>
<tr><td>Initial access</td><td>Public-facing app OS command injection</td><td>T1190, T1059.004</td></tr>
<tr><td>Discovery / credential</td><td>System info + reading config.php</td><td>T1082, T1552.001</td></tr>
<tr><td>Access</td><td>Credential reuse (SSH password)</td><td>T1078, T1021.004</td></tr>
<tr><td>Privilege escalation (web01)</td><td>PYTHONPATH hijack / sudo env</td><td>T1548.003, T1574.007</td></tr>
<tr><td>Lateral movement</td><td>Pivot to internal host with SSH key</td><td>T1021.004, T1552.004</td></tr>
<tr><td>Privilege escalation (internal01)</td><td>GTFOBins sudo tar --checkpoint-action</td><td>T1548.003, T1059.004</td></tr>
<tr><td>Credential access / exfil</td><td>/etc/shadow dump, staging in /tmp</td><td>T1003.008, T1074.001</td></tr>
</table>

<div class="box"><b>One-sentence summary:</b> the authentication bypass on the external portal and the
command-injection weakness in the <code>host</code> parameter were the start of the chain; the secret obtained
from it led to credential reuse, the sudo-env and GTFOBins weaknesses to root, and the exposed SSH key to a
pivot into the internal segment — each link small on its own, but chained together they opened the whole
organisation.</div>

</body></html>"""

    htmlpath = "/tmp/claude-0/gwt_en.html"
    with open(htmlpath, "w") as f:
        f.write(html)
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu",
                    "--no-pdf-header-footer", f"--print-to-pdf={out}",
                    f"file://{htmlpath}"], capture_output=True)
    print("[+] wrote", out)


if __name__ == "__main__":
    main()
