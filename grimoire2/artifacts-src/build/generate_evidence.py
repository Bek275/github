#!/usr/bin/env python3
"""
Beacon Incident -- evidence generator (Grimoire / defensive lab).

Deterministically writes the triage evidence bundle a learner investigates.
Scenario (defender's view only): a finance workstation at Northwind Trading
received a phishing email with a macro document. Telemetry then shows an
encoded PowerShell launch, a scheduled-task persistence entry, access to a
browser credential store, and beacon/upload traffic to an external host.

This is a DETECTION/ANALYSIS bundle: malicious payloads are intentionally
NOT shipped. Where the real intrusion carried operational code, the artifact
is redacted/defanged and only the indicators a defender would see remain.

Two OS{...} flags are embedded and recoverable only by correct analysis:
  * flag 1 -- Base64 (UTF-16LE) inside the PowerShell -enc value decodes to a
    short IR stub containing the marker (payload redacted),
  * flag 2 -- in the staged file the attacker left behind.

Usage:  python3 generate_evidence.py [output_dir]   (default: ./evidence)
"""
import base64
import os
import sys

# ---- scenario constants ---------------------------------------------------
DATE = "2026-10-03"
HOST = "FIN-WKS-07"
USER = "NORTHWIND\\j.morgan"
HOST_IP = "10.50.12.37"
C2_DOMAIN = "cdn.lifestyle-deals.net"
C2_IP = "203.0.113.45"
PHISH_FROM = "billing@vendor-portal-support.com"
PHISH_SRC_IP = "198.51.100.23"
ATTACH = "Invoice_Q3.docm"

FLAG1 = "OS{m4cr0_enc_p0w3rsh3ll_dr0pp3r}"   # inside the -enc Base64 (UTF-16LE)
FLAG2 = "OS{br0ws3r_cr3ds_b34c0n_3xf1l}"     # in the staged exfil file

# The -enc value decodes to this SHORT, DEFANGED IR stub (no working payload).
# A defender decoding the Base64 recovers the marker and the C2 indicator; the
# operational loader is deliberately not present in this training bundle.
STUB = (
    "# [IR note] encoded launcher recovered from script-block logging\n"
    "# operational payload REDACTED for this training bundle\n"
    f"$marker = '{FLAG1}'\n"
    f"# external host seen in proxy logs: {C2_DOMAIN}\n"
)
# PowerShell -enc is Base64 of UTF-16LE text.
ENC = base64.b64encode(STUB.encode("utf-16-le")).decode()


def w(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.rstrip("\n") + "\n")
    print(f"[+] wrote {path}")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "evidence"

    # --- phishing email ----------------------------------------------------
    w(f"{out}/email/Invoice_Q3_phish.eml", "\n".join([
        f"Return-Path: <{PHISH_FROM}>",
        f"Received: from mail.vendor-portal-support.com ([{PHISH_SRC_IP}])",
        f"        by mx.northwind.local; {DATE} 09:11:04 +0000",
        "Authentication-Results: mx.northwind.local; spf=fail; dkim=none; dmarc=fail",
        f"From: Vendor Billing <{PHISH_FROM}>",
        "To: <j.morgan@northwind.local>",
        "Subject: OVERDUE Invoice Q3 - immediate payment required",
        f"Date: {DATE} 09:11:03 +0000",
        'Content-Type: multipart/mixed; boundary="b1"',
        "",
        "--b1",
        "Content-Type: text/plain",
        "",
        "Dear Customer, your Q3 invoice is overdue. Open the attached document and",
        "enable editing / enable content to view the payment details.",
        "",
        "--b1",
        f'Content-Type: application/vnd.ms-word.document.macroEnabled.12; name="{ATTACH}"',
        "Content-Transfer-Encoding: base64",
        f'Content-Disposition: attachment; filename="{ATTACH}"',
        "",
        "UEsDBBQABgAIAAAAIQ... [macro-enabled document body truncated] ...AAAA==",
        "--b1--",
    ]))

    # --- extracted macro (defanged: shows it launches encoded PowerShell) --
    w(f"{out}/extracted/Invoice_Q3_macro_summary.txt", "\n".join([
        "Static triage of the attached document's VBA project (olevba summary):",
        "",
        "  Module: ThisDocument",
        "  AutoExec: Document_Open  (runs automatically when the document opens)",
        "  Suspicious: builds a command string and calls Shell(...) with vbHide",
        "  Suspicious: launches powershell with '-nop -w hidden -enc <Base64>'",
        "",
        "The exact encoded value as launched (see Sysmon / 4104 for full context):",
        f"  powershell -nop -w hidden -enc {ENC}",
        "",
        "(The document's full macro body is not reproduced here; the behavioural",
        " indicators above are what matters for detection.)",
    ]))

    # --- Sysmon process creation (EID 1) -----------------------------------
    w(f"{out}/{HOST}/sysmon_process_creation.log", "\n".join([
        f"{DATE} 09:14:52 EID=1 User={USER} "
        "Image=C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE "
        f"ParentImage=C:\\Windows\\explorer.exe CommandLine=\"WINWORD.EXE /n {ATTACH}\"",
        f"{DATE} 09:15:03 EID=1 User={USER} Image=C:\\Windows\\System32\\cmd.exe "
        "ParentImage=C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE "
        f"CommandLine=\"cmd.exe /c powershell -nop -w hidden -enc {ENC}\"",
        f"{DATE} 09:15:03 EID=1 User={USER} "
        "Image=C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe "
        f"ParentImage=C:\\Windows\\System32\\cmd.exe CommandLine=\"powershell -nop -w hidden -enc {ENC}\"",
        f"{DATE} 09:16:40 EID=1 User={USER} Image=C:\\Windows\\System32\\schtasks.exe "
        "ParentImage=powershell.exe CommandLine=\"schtasks /create "
        "/tn MicrosoftEdgeUpdateTaskMachineCore /sc minute /mo 10 /tr <redacted> /f\"",
        f"{DATE} 09:18:30 EID=1 User={USER} Image=powershell.exe ParentImage=powershell.exe "
        "CommandLine=\"powershell <accessed browser credential store - see file-access log>\"",
    ]))

    # --- PowerShell Operational 4104 (script block logging, defanged) ------
    w(f"{out}/{HOST}/powershell_4104_scriptblock.log", "\n".join([
        f"{DATE} 09:15:04 EventID=4104 Level=Warning ScriptBlockText=<<<",
        STUB.rstrip("\n"),
        ">>>",
        f"{DATE} 09:15:22 EventID=4104 Level=Warning ScriptBlockText=<<<",
        "# second script block observed; body redacted in this training bundle.",
        f"# indicator: repeated outbound requests to http://{C2_DOMAIN}/ (see proxy log)",
        ">>>",
    ]))

    # --- browser credential-store access (detection indicator) -------------
    w(f"{out}/{HOST}/file_access_sensitive.log", "\n".join([
        "Sensitive file-access indicators (EDR):",
        f"{DATE} 09:18:30 Process=powershell.exe Account={USER} Action=Read "
        "Path=C:\\Users\\j.morgan\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data",
        f"{DATE} 09:18:34 Process=powershell.exe Account={USER} Action=Read "
        "Path=C:\\Users\\j.morgan\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Network\\Cookies",
        "# unusual: powershell.exe reading the browser credential store",
    ]))

    # --- Windows Security 4688 / 4624 --------------------------------------
    w(f"{out}/{HOST}/security_4688_4624.log", "\n".join([
        f"{DATE} 09:10:59 EventID=4624 LogonType=2 Account={USER} Source=Interactive  (normal morning logon)",
        f"{DATE} 09:15:03 EventID=4688 NewProcess=powershell.exe Creator=cmd.exe Account={USER} "
        "CommandLine=\"powershell -nop -w hidden -enc <see sysmon>\"",
        f"{DATE} 09:16:40 EventID=4688 NewProcess=schtasks.exe Creator=powershell.exe Account={USER}",
    ]))

    # --- scheduled task XML (persistence) ----------------------------------
    w(f"{out}/{HOST}/scheduled_task_MicrosoftEdgeUpdateTaskMachineCore.xml", "\n".join([
        '<?xml version="1.0" encoding="UTF-16"?>',
        '<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">',
        "  <RegistrationInfo>",
        f"    <Date>{DATE}T09:16:40</Date>",
        f"    <Author>{USER}</Author>",
        "    <Description>Masquerades as a Microsoft Edge update task</Description>",
        "  </RegistrationInfo>",
        "  <Triggers><TimeTrigger><Repetition><Interval>PT10M</Interval></Repetition>",
        f"    <StartBoundary>{DATE}T09:20:00</StartBoundary></TimeTrigger></Triggers>",
        "  <Actions>",
        "    <Exec>",
        "      <Command>powershell.exe</Command>",
        "      <Arguments>-nop -w hidden -ep bypass -File C:\\Users\\Public\\x.ps1</Arguments>",
        "    </Exec>",
        "  </Actions>",
        "</Task>",
    ]))

    # --- proxy log (C2 beacon + exfil upload) ------------------------------
    w(f"{out}/proxy/squid_access.log", "\n".join([
        f"{DATE} 09:15:20 {HOST_IP} GET http://{C2_DOMAIN}/u/x.ps1 200 3488 \"PowerShell\"",
        f"{DATE} 09:20:01 {HOST_IP} GET http://{C2_DOMAIN}/api/task 200 12 \"-\"  (beacon)",
        f"{DATE} 09:30:01 {HOST_IP} GET http://{C2_DOMAIN}/api/task 200 12 \"-\"  (beacon)",
        f"{DATE} 09:41:55 {HOST_IP} POST http://{C2_DOMAIN}/api/upload 200 5242880 \"-\"  (large upload)",
        f"# {C2_DOMAIN} resolves to {C2_IP}; newly-registered, no business purpose",
    ]))

    # --- staged exfil file the attacker left behind ------------------------
    w(f"{out}/{HOST}/C_Users_Public/.stage/exfil_manifest.txt", "\n".join([
        "# staging manifest left under C:\\Users\\Public\\.stage",
        "collected: chrome_logindata.bin, cookies.bin, documents_Q3.zip",
        f"marker: {FLAG2}",
        f"upload_target: http://{C2_DOMAIN}/api/upload",
    ]))

    print("\n[*] evidence generated under:", out)
    print("[*] (flags are embedded; see answer-key.md for the solution)")


if __name__ == "__main__":
    main()
