"""
Tinlance FDSE Toolkit — Incident Response Playbook Generator
=============================================================
Produces a client-specific Incident Response Playbook mapped to
ThreatFade alert levels, MITRE ATT&CK TTPs, and NIS2/DORA obligations.

Every ThreatFade alert severity maps to a specific response procedure:
  CRITICAL → Immediate containment (0-2 hours)
  HIGH     → Urgent investigation (2-24 hours)
  MEDIUM   → Scheduled remediation (1-7 days)
  LOW      → Planned improvement (1-4 weeks)

Usage:
    python ir_playbook.py --client "Acme Corp" --out ./output
    python ir_playbook.py --demo
"""

import argparse
import os
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ── Colours ────────────────────────────────────────────────────────────────
TEAL  = "00e5c8"; DARK  = "080a0f"; DARK2 = "0d1018"
LIGHT = "e8ecf4"; MUTED = "888888"; GREEN = "2ecc71"
CRIT  = "ff4d6d"; HIGH  = "ff8c42"; MED   = "f5c842"
LOW   = "4ecdc4"; INFO  = "6c8ebf"

def rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

def set_cell_bg(cell, hex_color):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  hex_color.lstrip("#"))
    tcPr.append(shd)

def add_run(para, text, bold=False, color=None, size=10, italic=False):
    run = para.add_run(text)
    run.bold = bold; run.italic = italic
    run.font.size = Pt(size); run.font.name = "Arial"
    if color: run.font.color.rgb = rgb(color)
    return run

def page_margins(doc):
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2)
        s.top_margin  = s.bottom_margin = Cm(2.5)

def hdr_bar(doc, label):
    t = doc.add_table(rows=1, cols=1); t.style = "Table Grid"
    c = t.rows[0].cells[0]; set_cell_bg(c, "080a0f")
    p = c.paragraphs[0]
    add_run(p, "TINLANCE.", bold=True, color=TEAL, size=11)
    add_run(p, f"  ·  {label}", color=MUTED, size=9)

def divider(doc, color=TEAL):
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    b.set(qn("w:val"),   "single")
    b.set(qn("w:sz"),    "6")
    b.set(qn("w:space"), "1")
    b.set(qn("w:color"), color.lstrip("#"))
    pBdr.append(b); pPr.append(pBdr)

def h(doc, text, level=1, color=DARK):
    p = doc.add_heading(text, level=level)
    for r in p.runs:
        r.font.color.rgb = rgb(color)
        r.font.name = "Arial"
    return p

def body(doc, text, color="444444"):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(10); r.font.name = "Arial"
    r.font.color.rgb = rgb(color)
    p.paragraph_format.space_after = Pt(6)
    return p

def bullet(doc, text, color="444444"):
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run(text)
    r.font.size = Pt(10); r.font.name = "Arial"
    r.font.color.rgb = rgb(color)
    return p

def numbered(doc, text, color="444444"):
    p = doc.add_paragraph(style="List Number")
    r = p.add_run(text)
    r.font.size = Pt(10); r.font.name = "Arial"
    r.font.color.rgb = rgb(color)
    return p

def alert_box(doc, severity, title, steps, nis2_note=None):
    sev_colors = {
        "CRITICAL": CRIT, "HIGH": HIGH,
        "MEDIUM":   MED,  "LOW":  LOW, "INFO": INFO
    }
    sc = sev_colors.get(severity, INFO)

    # Severity header
    t = doc.add_table(rows=1, cols=2); t.style = "Table Grid"
    c0, c1 = t.rows[0].cells
    set_cell_bg(c0, sc); set_cell_bg(c1, sc)
    add_run(c0.paragraphs[0], f"🚨 {severity}", bold=True, color="080a0f", size=11)
    add_run(c1.paragraphs[0], title,            bold=True, color="080a0f", size=11)

    # Steps table
    steps_t = doc.add_table(rows=len(steps), cols=3)
    steps_t.style = "Table Grid"
    for i, (time_box, owner, action) in enumerate(steps):
        bg = "f5f5f5" if i % 2 == 0 else "ffffff"
        c0, c1, c2 = steps_t.rows[i].cells
        set_cell_bg(c0, sc if i == 0 else bg)
        set_cell_bg(c1, "0d1018")
        set_cell_bg(c2, bg)
        add_run(c0.paragraphs[0], time_box, bold=(i==0), color="080a0f" if i==0 else "444444", size=9)
        add_run(c1.paragraphs[0], owner,    bold=True,   color=TEAL, size=9)
        add_run(c2.paragraphs[0], action,                color="444444", size=9)

    if nis2_note:
        p = doc.add_paragraph()
        add_run(p, "⚖️  NIS2 Obligation: ", bold=True, color=TEAL, size=9)
        add_run(p, nis2_note, color="444444", size=9)
    doc.add_paragraph()


# ══════════════════════════════════════════════════════════════════════════════
# PLAYBOOK DATA
# ══════════════════════════════════════════════════════════════════════════════

PLAYBOOK_DATA = {
    "alerts": [
        {
            "severity": "CRITICAL",
            "title": "Active C2 Beacon Detected (ThreatFade z-score ≥ 7.0)",
            "trigger": "ThreatFade detects outbound traffic with z-score ≥ 7.0 consistent with Cobalt Strike, Merlin QUIC, or similar C2 framework. Active adversary presence confirmed.",
            "mitre": ["T1071.001 — Application Layer Protocol", "T1573 — Encrypted Channel", "T1041 — Exfiltration Over C2"],
            "sla": "Response must begin within 15 minutes. Containment within 2 hours.",
            "steps": [
                ("T+0 min",  "SOC Analyst",    "Verify ThreatFade alert — check z-score, entropy, affected host IP, and beacon interval"),
                ("T+5 min",  "SOC Lead",       "Declare Critical Incident — notify CISO and IR team via out-of-band channel (not email)"),
                ("T+10 min", "Network Eng",    "Isolate affected host(s) at switch level — do NOT power off (preserve memory for forensics)"),
                ("T+15 min", "Firewall Admin", "Block C2 destination IP/domain at perimeter firewall — add to blocklist"),
                ("T+20 min", "SOC Analyst",    "Capture full packet dump of C2 traffic — preserve as evidence"),
                ("T+30 min", "IR Lead",        "Begin lateral movement sweep — run ThreatFade across full network for additional beacons"),
                ("T+1 hr",   "CISO",           "Assess data exfiltration scope — check DLP logs, outbound data volumes"),
                ("T+2 hrs",  "CISO / Legal",   "Determine NIS2 notification obligation — if personal data involved, 24hr CSIRT notification clock starts"),
                ("T+4 hrs",  "IR Lead",        "Deploy ThreatFade endpoint agent on all hosts — identify full scope of compromise"),
                ("T+24 hrs", "CISO",           "Submit NIS2 early warning to national CSIRT if incident qualifies (Article 23)"),
                ("T+72 hrs", "CISO / Legal",   "Submit NIS2 full notification if required — impact, scope, containment measures"),
            ],
            "nis2": "Article 23 — Significant incidents affecting continuity of services must be reported to national CSIRT within 24 hours (early warning) and 72 hours (full notification).",
        },
        {
            "severity": "CRITICAL",
            "title": "Ransomware / Destructive Malware Indicators",
            "trigger": "ThreatFade or BugFlow detects mass file encryption activity, shadow copy deletion, or rapid lateral movement consistent with ransomware deployment.",
            "mitre": ["T1486 — Data Encrypted for Impact", "T1490 — Inhibit System Recovery", "T1021 — Remote Services"],
            "sla": "Response must begin within 5 minutes. Network isolation within 15 minutes.",
            "steps": [
                ("T+0 min",  "SOC Analyst",  "Verify ransomware indicators — check for VSS deletion, file extension changes, ransom notes"),
                ("T+5 min",  "IR Lead",      "Initiate Emergency Response — activate IR retainer or call Tinlance emergency line immediately"),
                ("T+10 min", "Network Eng",  "EMERGENCY: Segment network — isolate ALL affected VLANs from internet and backups"),
                ("T+15 min", "Backup Admin", "CRITICAL: Verify backup integrity — ensure backups are NOT connected to affected network"),
                ("T+20 min", "CISO",         "Notify executive team and legal counsel — board notification may be required"),
                ("T+30 min", "IR Lead",      "Identify patient zero — find initial infection vector via ThreatFade timeline"),
                ("T+1 hr",   "Legal",        "Assess regulatory notification obligations — NIS2, GDPR, sector-specific requirements"),
                ("T+2 hrs",  "CISO",         "Decision point: pay or recover — document decision and rationale formally"),
                ("T+4 hrs",  "IR Team",      "Begin recovery from clean backups — prioritise critical systems first"),
                ("T+24 hrs", "CISO",         "Submit NIS2 early warning to CSIRT"),
            ],
            "nis2": "Article 23 — Ransomware affecting essential services constitutes a significant incident. 24-hour early warning mandatory. Law enforcement notification recommended.",
        },
        {
            "severity": "HIGH",
            "title": "Lateral Movement Detected",
            "trigger": "ThreatFade detects anomalous SMB/WMI/RDP traffic between internal hosts. Z-score ≥ 4.0 with cross-subnet movement pattern.",
            "mitre": ["T1021.002 — SMB/Windows Admin Shares", "T1021.006 — Windows Remote Management", "T1018 — Remote System Discovery"],
            "sla": "Investigation must begin within 2 hours. Containment plan within 8 hours.",
            "steps": [
                ("T+0 hr",  "SOC Analyst", "Confirm lateral movement alert — map source host, destination hosts, protocol, and timestamps"),
                ("T+1 hr",  "SOC Lead",    "Correlate with ThreatFade C2 detections — determine if lateral movement is post-compromise activity"),
                ("T+2 hrs", "IR Lead",     "Map full movement path — identify all hosts accessed since initial compromise"),
                ("T+4 hrs", "SOC Analyst", "Check for credential dumping indicators on source host — Mimikatz patterns, LSASS access"),
                ("T+6 hrs", "IR Lead",     "Contain movement — implement temporary ACLs between affected segments"),
                ("T+8 hrs", "IT Admin",    "Force password reset on all accounts accessed from compromised host"),
                ("T+12 hrs","CISO",        "Assess scope — determine if privileged accounts were accessed"),
                ("T+24 hrs","IR Lead",     "Deploy network segmentation to prevent recurrence"),
            ],
            "nis2": "Article 21(2)(e) — Network segmentation failures must be addressed as part of NIS2 security measures. Document containment actions for audit trail.",
        },
        {
            "severity": "HIGH",
            "title": "Exposed Credentials Detected (ReconOS / BugFlow)",
            "trigger": "ReconOS OSINT scan or BugFlow detects active credentials, API keys, or tokens exposed in public repositories, DNS records, or paste sites.",
            "mitre": ["T1552.001 — Credentials in Files", "T1078 — Valid Accounts", "T1589 — Gather Victim Identity Information"],
            "sla": "Credentials must be revoked within 2 hours of detection.",
            "steps": [
                ("T+0 hr",  "SOC Analyst",  "Confirm credential exposure — identify credential type, scope, and public exposure duration"),
                ("T+30 min","DevOps Lead",   "IMMEDIATELY revoke/rotate all exposed credentials — do not wait for investigation to complete"),
                ("T+1 hr",  "Security Eng", "Audit access logs for exposed credential usage — determine if credentials were already abused"),
                ("T+2 hrs", "DevOps Lead",   "Remove exposed credentials from all repositories — purge git history if needed"),
                ("T+3 hrs", "Security Eng", "Scan all repositories and CI/CD pipelines for additional credential exposure"),
                ("T+4 hrs", "IR Lead",      "If credentials were abused — escalate to CRITICAL and initiate full IR procedure"),
                ("T+24 hrs","DevOps Lead",   "Implement pre-commit hooks (TruffleHog/git-secrets) to prevent recurrence"),
            ],
            "nis2": "Article 21(2)(h) — Policies on cryptography and credential management are required. Credential exposure events must be documented.",
        },
        {
            "severity": "MEDIUM",
            "title": "Vulnerability Discovered — High CVSS (7.0–8.9)",
            "trigger": "BugFlow scan identifies a HIGH severity vulnerability (CVSS 7.0–8.9) on an internet-facing or critical internal system.",
            "mitre": ["T1190 — Exploit Public-Facing Application", "T1203 — Exploitation for Client Execution"],
            "sla": "Patch or mitigate within 7 days. Interim controls within 48 hours.",
            "steps": [
                ("Day 1",  "SOC Analyst",  "Confirm vulnerability — validate CVSS score, affected versions, and exploitability"),
                ("Day 1",  "IT Admin",     "Implement interim mitigation — WAF rule, network ACL, or service isolation"),
                ("Day 2",  "Dev / IT",     "Test patch in non-production environment"),
                ("Day 3",  "Change Mgmt",  "Raise emergency change request — document risk and business impact"),
                ("Day 5",  "IT Admin",     "Deploy patch to production during maintenance window"),
                ("Day 7",  "SOC Analyst",  "Verify patch — re-run BugFlow scan to confirm remediation"),
                ("Day 7",  "Security Eng", "Update asset register with patched version — close vulnerability ticket"),
            ],
            "nis2": "Article 21(2)(e) — Patch management is a core NIS2 requirement. Document all patch actions with timestamps for regulatory audit.",
        },
        {
            "severity": "LOW",
            "title": "Security Misconfiguration Detected",
            "trigger": "BugFlow or ThreatFade identifies a security misconfiguration — missing headers, default credentials, weak TLS, open ports, or SNMP defaults.",
            "mitre": ["T1602 — Data from Configuration Repository", "T1040 — Network Sniffing"],
            "sla": "Remediation plan within 1 week. Fix implemented within 4 weeks.",
            "steps": [
                ("Week 1", "SOC Analyst",  "Document misconfiguration — record affected system, configuration item, and risk"),
                ("Week 1", "IT Admin",     "Assign owner — confirm who is responsible for the affected system"),
                ("Week 2", "IT Admin",     "Develop remediation plan — test fix in non-production first"),
                ("Week 3", "Change Mgmt",  "Schedule maintenance window for production fix"),
                ("Week 4", "IT Admin",     "Implement fix — verify via re-scan"),
                ("Week 4", "SOC Analyst",  "Close finding in tracker — update report"),
            ],
            "nis2": "Article 21 — Misconfigurations contribute to organisational risk. Track and document all remediation actions.",
        },
    ],
    "contacts": [
        ("Role",            "Name",         "Contact",              "Escalation Level"),
        ("CISO / Security Lead",   "[Name]",  "[Email / Phone]",  "All Critical + High"),
        ("IR Lead",                "[Name]",  "[Email / Phone]",  "All Critical"),
        ("SOC Lead",               "[Name]",  "[Email / Phone]",  "All alerts"),
        ("Legal / Compliance",     "[Name]",  "[Email / Phone]",  "NIS2 / GDPR incidents"),
        ("IT / Network Admin",     "[Name]",  "[Email / Phone]",  "Containment actions"),
        ("Executive Sponsor",      "[Name]",  "[Email / Phone]",  "Critical only"),
        ("Tinlance Support",       "Chinaemerem Nwachukwu", "nwachukwuchinaemerem8@gmail.com", "Technical escalation 24/7"),
        ("National CSIRT",         "[Country CSIRT]", "[CSIRT contact]", "NIS2 Article 23 reporting"),
    ],
    "comms_templates": [
        ("Internal Alert — Security Team",
         "SECURITY INCIDENT ALERT\nSeverity: [CRITICAL/HIGH/MEDIUM]\nDate/Time: [DATETIME]\nIncident ID: INC-[NUMBER]\nAffected Systems: [LIST]\nSummary: [2 sentences max]\nImmediate Actions Taken: [LIST]\nNext Update: [TIME]\nIncident Lead: [NAME]"),
        ("Executive Notification",
         "EXECUTIVE SECURITY BRIEFING\nDate: [DATE]\nIncident: [ONE LINE DESCRIPTION]\nBusiness Impact: [PLAIN ENGLISH — no jargon]\nCurrent Status: [Contained / Active / Investigating]\nCustomer Impact: [Yes/No — details]\nRegulatory Obligation: [Yes/No — NIS2/GDPR notification required?]\nNext Steps: [3 bullet points]\nNext Update: [TIME]"),
        ("NIS2 Early Warning (24hr — Article 23)",
         "TO: [National CSIRT]\nFROM: [Organisation Name, Contact]\nSUBJECT: NIS2 Early Warning Notification\n\nDate of incident: [DATE]\nDate detected: [DATE]\nIncident type: [Ransomware / C2 / Data breach / DDoS / Other]\nAffected services: [LIST]\nGeographic scope: [Countries/regions affected]\nInitial assessment: [Is it a significant incident? Yes/No with brief reasoning]\nActions taken so far: [LIST]\nOngoing impact: [Yes/No]\n\nThis is an early warning notification per NIS2 Article 23. A full notification will follow within 72 hours."),
    ],
}


# ══════════════════════════════════════════════════════════════════════════════
# BUILD PLAYBOOK
# ══════════════════════════════════════════════════════════════════════════════

def build_ir_playbook(client_name: str, out_path: str):
    doc = Document()
    page_margins(doc)

    hdr_bar(doc, "Incident Response Playbook — FDSE Engagement")
    doc.add_paragraph()

    # Title
    p = doc.add_heading("Incident Response Playbook", 1)
    for r in p.runs: r.font.color.rgb = rgb(DARK); r.font.name = "Arial"
    p = doc.add_paragraph()
    add_run(p, f"Prepared for: {client_name}", bold=True, color="00b8a0", size=14)
    p = doc.add_paragraph()
    add_run(p, f"Powered by ThreatFade v0.2.0-beta  ·  Tinlance Limited  ·  {datetime.now().strftime('%B %d, %Y')}",
            color=MUTED, size=9)
    divider(doc)

    # Purpose
    h(doc, "Purpose & Scope", 2, DARK)
    body(doc, f"This Incident Response Playbook provides {client_name}'s security team with step-by-step response procedures for every alert severity generated by ThreatFade v0.2.0-beta. Each procedure is mapped to MITRE ATT&CK TTPs, assigned response SLAs, and linked to NIS2/DORA compliance obligations where applicable.")
    body(doc, "This playbook is a living document. Review and update after every major incident and at minimum quarterly.")
    doc.add_paragraph()

    # Severity overview
    h(doc, "Alert Severity Levels & Response SLAs", 2, DARK)
    t = doc.add_table(rows=6, cols=4); t.style = "Table Grid"
    headers = ["Severity", "ThreatFade Trigger", "Response SLA", "Escalation"]
    for ci, hd in enumerate(headers):
        set_cell_bg(t.rows[0].cells[ci], "080a0f")
        add_run(t.rows[0].cells[ci].paragraphs[0], hd, bold=True, color=TEAL, size=9)

    sev_rows = [
        (CRIT,  "CRITICAL", "z-score ≥ 7.0 or ransomware indicators", "15 min response, 2 hr containment", "CISO + IR Team + Legal"),
        (HIGH,  "HIGH",     "z-score 5.0–6.9 or CVSS 7.0–8.9",       "2 hr response, 8 hr containment",   "SOC Lead + IR Lead"),
        (MED,   "MEDIUM",   "z-score 3.0–4.9 or CVSS 4.0–6.9",       "24 hr response, 7 day remediation",  "SOC Lead"),
        (LOW,   "LOW",      "z-score 1.0–2.9 or CVSS 0.1–3.9",       "1 week response, 4 week remediation","SOC Analyst"),
        (INFO,  "INFO",     "Informational / configuration gap",       "Scheduled remediation cycle",        "IT Admin"),
    ]
    for ri, (color, *vals) in enumerate(sev_rows, 1):
        for ci, val in enumerate(vals):
            bg = "f5f5f5" if ri % 2 == 0 else "ffffff"
            set_cell_bg(t.rows[ri].cells[ci], color if ci == 0 else bg)
            add_run(t.rows[ri].cells[ci].paragraphs[0], val,
                    bold=(ci == 0), color="080a0f" if ci == 0 else "444444", size=9)
    doc.add_paragraph()

    # Contact list
    h(doc, "Incident Response Contacts", 2, DARK)
    body(doc, "Complete this table before your first engagement. All contacts must be reachable 24/7 for Critical incidents via out-of-band channel (phone/WhatsApp — not email).")
    ct = doc.add_table(rows=len(PLAYBOOK_DATA["contacts"]), cols=4)
    ct.style = "Table Grid"
    for ri, row in enumerate(PLAYBOOK_DATA["contacts"]):
        bg = "080a0f" if ri == 0 else ("f5f5f5" if ri % 2 == 0 else "ffffff")
        for ci, val in enumerate(row):
            set_cell_bg(ct.rows[ri].cells[ci], bg)
            add_run(ct.rows[ri].cells[ci].paragraphs[0], val,
                    bold=(ri == 0), color=TEAL if ri == 0 else "444444", size=9)
    doc.add_paragraph()

    # Response procedures
    h(doc, "Response Procedures by Alert Type", 2, DARK)
    body(doc, "Each procedure below maps directly to a ThreatFade alert. Column headers: TIME — elapsed from detection | OWNER — responsible team | ACTION — exact step to take.")
    doc.add_paragraph()

    for alert in PLAYBOOK_DATA["alerts"]:
        h(doc, f"{alert['severity']} — {alert['title']}", 3, DARK)

        p = doc.add_paragraph()
        add_run(p, "Trigger: ", bold=True, color=TEAL, size=10)
        add_run(p, alert["trigger"], color="444444", size=10)

        p = doc.add_paragraph()
        add_run(p, "MITRE ATT&CK: ", bold=True, color=TEAL, size=10)
        add_run(p, "  ·  ".join(alert["mitre"]), color="444444", size=10)

        p = doc.add_paragraph()
        add_run(p, "Response SLA: ", bold=True, color=TEAL, size=10)
        add_run(p, alert["sla"], bold=True,
                color=CRIT if "CRITICAL" in alert["severity"] else HIGH, size=10)

        doc.add_paragraph()
        alert_box(doc, alert["severity"], "Step-by-step procedure",
                  alert["steps"], alert.get("nis2"))

    # Communication templates
    h(doc, "Communication Templates", 2, DARK)
    body(doc, "Use these templates exactly as written. Customise bracketed fields only. Do not improvise communications during an active incident.")
    doc.add_paragraph()

    for title, template in PLAYBOOK_DATA["comms_templates"]:
        h(doc, title, 3, DARK)
        t = doc.add_table(rows=1, cols=1); t.style = "Table Grid"
        c = t.rows[0].cells[0]
        set_cell_bg(c, "0d1018")
        p = c.paragraphs[0]
        add_run(p, template, color=TEAL, size=9)
        c.paragraphs[0].paragraph_format.space_after = Pt(0)
        doc.add_paragraph()

    # Post-incident review
    h(doc, "Post-Incident Review Checklist", 2, DARK)
    body(doc, "Complete within 5 business days of incident closure. Schedule a 1-hour review meeting with all responders.")
    for item in [
        "Timeline documented — from first detection to full containment",
        "Root cause identified — initial access vector confirmed",
        "Detection gap analysis — could ThreatFade have detected this earlier?",
        "Response gap analysis — what slowed containment?",
        "Playbook updated — incorporate lessons learned",
        "Controls improved — new rules, ACLs, or patches implemented",
        "NIS2 post-incident report submitted if required (Article 23)",
        "Executive debrief completed",
        "Tinlance notified — share findings to improve ThreatFade detection rules",
    ]:
        bullet(doc, item)
    doc.add_paragraph()

    # Footer
    divider(doc)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, f"Tinlance Limited  ·  RC: 7962164  ·  tinlance.com  ·  {client_name}  ·  CONFIDENTIAL",
            color=MUTED, size=8)

    doc.save(out_path)
    print(f"  ✓ IR Playbook: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tinlance IR Playbook Generator")
    parser.add_argument("--client", default="Client Organisation", help="Client name")
    parser.add_argument("--out",    default=".", help="Output directory")
    parser.add_argument("--demo",   action="store_true")
    args = parser.parse_args()

    if args.demo:
        args.client = "Acme Financial Services Ltd"

    Path(args.out).mkdir(parents=True, exist_ok=True)
    slug = args.client.replace(" ", "_")[:30]
    out  = str(Path(args.out) / f"Tinlance_IR_Playbook_{slug}.docx")
    build_ir_playbook(args.client, out)
    print(f"  ✓ Done.")
