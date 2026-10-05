"""
Tinlance FDSE Toolkit — Report Generator
=========================================
Produces enterprise-grade PDF, Word (DOCX), and Excel reports from
ThreatFade, BugFlow, and ReconOS output data.

Audience layers:
  - Executive Summary  → board/CISO (plain English, business impact)
  - Technical Findings → security team (CVSS, evidence, remediation)
  - Compliance Mapping → NIS2/DORA gap assessment
  - Remediation Roadmap → prioritised action plan

Usage:
    python report_generator.py --input sample_input.json --format all --client "Acme Corp"
    python report_generator.py --input sample_input.json --format pdf
    python report_generator.py --input sample_input.json --format docx
    python report_generator.py --input sample_input.json --format excel
    python report_generator.py --demo   # generates a full demo report from built-in data
"""

import json
import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# ── PDF ────────────────────────────────────────────────────────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF

# ── DOCX ───────────────────────────────────────────────────────────────────────
from docx import Document as DocxDocument
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ── Excel ──────────────────────────────────────────────────────────────────────
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference

# ── Colours ────────────────────────────────────────────────────────────────────
TEAL        = colors.HexColor("#00e5c8")
TEAL_DARK   = colors.HexColor("#00b8a0")
DARK        = colors.HexColor("#080a0f")
DARK2       = colors.HexColor("#0d1018")
DARK3       = colors.HexColor("#12151e")
PINK        = colors.HexColor("#ff4d6d")
LIGHT       = colors.HexColor("#e8ecf4")
MUTED       = colors.HexColor("#8892a4")
WHITE       = colors.white
CRITICAL_C  = colors.HexColor("#ff4d6d")
HIGH_C      = colors.HexColor("#ff8c42")
MEDIUM_C    = colors.HexColor("#f5c842")
LOW_C       = colors.HexColor("#4ecdc4")
INFO_C      = colors.HexColor("#6c8ebf")
GREEN_C     = colors.HexColor("#2ecc71")

SEVERITY_COLORS = {
    "CRITICAL": CRITICAL_C,
    "HIGH":     HIGH_C,
    "MEDIUM":   MEDIUM_C,
    "LOW":      LOW_C,
    "INFO":     INFO_C,
}

CVSS_RANGES = {
    "CRITICAL": (9.0, 10.0),
    "HIGH":     (7.0, 8.9),
    "MEDIUM":   (4.0, 6.9),
    "LOW":      (0.1, 3.9),
    "INFO":     (0.0, 0.0),
}

NIS2_CONTROLS = [
    ("Risk management policies",           "Article 21(2)(a)"),
    ("Incident handling procedures",        "Article 21(2)(b)"),
    ("Business continuity & recovery",      "Article 21(2)(c)"),
    ("Supply chain security",              "Article 21(2)(d)"),
    ("Network & information system security","Article 21(2)(e)"),
    ("Policies on cryptography",           "Article 21(2)(h)"),
    ("Human resources security",           "Article 21(2)(i)"),
    ("Multi-factor authentication",        "Article 21(2)(j)"),
    ("Incident reporting (24hr/72hr)",     "Article 23"),
    ("Management accountability",          "Article 20"),
]

DORA_CONTROLS = [
    ("ICT risk management framework",       "Article 5-16"),
    ("ICT-related incident reporting",      "Article 17-23"),
    ("Digital operational resilience testing","Article 24-27"),
    ("ICT third-party risk management",    "Article 28-44"),
    ("Information sharing arrangements",   "Article 45"),
    ("Register of Information (RoI)",      "Article 28(3)"),
]


# ══════════════════════════════════════════════════════════════════════════════
# DATA MODEL
# ══════════════════════════════════════════════════════════════════════════════

def load_input(path: str) -> dict:
    with open(path) as f:
        return json.load(f)

def build_demo_data() -> dict:
    return {
        "meta": {
            "client_name":    "Acme Financial Services Ltd",
            "engagement_type":"Security Assessment & C2 Detection Audit",
            "start_date":     "2026-05-26",
            "end_date":       "2026-06-01",
            "assessor":       "Tinlance Limited — FDSE Team",
            "assessor_contact":"nwachukwuchinaemerem8@gmail.com",
            "classification": "CONFIDENTIAL",
            "version":        "1.0",
            "report_date":    datetime.now().strftime("%B %d, %Y"),
        },
        "executive": {
            "overall_risk":   "HIGH",
            "risk_score":     7.4,
            "summary":        (
                "Tinlance conducted a forward-deployed security assessment of Acme Financial "
                "Services' network infrastructure and endpoint environment between May 26 and "
                "June 1, 2026. The assessment identified 3 critical, 5 high, 4 medium, and "
                "2 low severity findings. The most significant finding is active C2 beacon "
                "traffic consistent with Cobalt Strike patterns detected on 3 internal hosts, "
                "indicating a likely active intrusion that requires immediate containment. "
                "Immediate remediation of critical findings is strongly recommended."
            ),
            "business_impact": (
                "If unaddressed, the active C2 activity exposes Acme to data exfiltration, "
                "ransomware deployment, and regulatory fines under NIS2 (up to €10 million or "
                "2% of global turnover). The 72-hour NIS2 incident reporting clock may already "
                "be running. Immediate containment and notification should be prioritised."
            ),
            "key_recommendations": [
                "Isolate the 3 affected hosts immediately and initiate incident response",
                "Engage CSIRT within 24 hours per NIS2 Article 23 requirements",
                "Deploy ThreatFade endpoint agent across all 847 endpoints within 48 hours",
                "Patch critical CVEs on internet-facing systems within 7 days",
                "Implement network segmentation to limit lateral movement",
            ]
        },
        "scope": {
            "in_scope": [
                "External perimeter — 14 internet-facing IP addresses",
                "Internal network — /16 subnet (847 active hosts)",
                "3 web applications (customer portal, admin panel, API gateway)",
                "Active Directory environment — 1 forest, 2 domains",
                "Endpoint fleet — Windows 10/11 (712 hosts), Linux (135 hosts)",
            ],
            "out_of_scope": [
                "OT/SCADA systems (separate engagement planned)",
                "Physical security controls",
                "Third-party SaaS applications",
            ],
            "methodology": "PTES (Penetration Testing Execution Standard) + MITRE ATT&CK framework. ThreatFade entropy/z-score analysis for network traffic. BugFlow Elite v6 for automated reconnaissance and vulnerability discovery.",
            "tools": ["ThreatFade v0.2.0-beta", "BugFlow Elite v6", "ReconOS OSINT Engine", "FusionOps v0.3.0", "Nmap", "Burp Suite Pro"],
        },
        "findings": [
            {
                "id": "TF-001",
                "title": "Active C2 Beacon Traffic — Cobalt Strike Pattern Detected",
                "severity": "CRITICAL",
                "cvss_score": 9.8,
                "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
                "affected_systems": ["192.168.10.45", "192.168.10.67", "192.168.11.203"],
                "mitre_ttp": ["T1071.001 — Application Layer Protocol: Web Protocols", "T1573 — Encrypted Channel", "T1095 — Non-Application Layer Protocol"],
                "description": "ThreatFade detected statistically anomalous outbound traffic from 3 internal hosts with z-score 7.01, consistent with Cobalt Strike HTTP/S beacon patterns. Traffic analysis reveals periodic callbacks at 60-second intervals to an external IP (203.0.113.47) with encrypted payload signatures matching known Cobalt Strike malleable C2 profiles.",
                "evidence": "ThreatFade detection log: z-score=7.01, entropy=0.87, drop_ratio=0.23. Packet capture confirmed 60-second beacon interval. MITRE TTP mapping: T1071.001, T1573.",
                "business_impact": "Active adversary presence. Risk of lateral movement, credential harvesting, data exfiltration, and ransomware deployment. NIS2 incident reporting obligation likely triggered.",
                "remediation": "1. Immediately isolate affected hosts (192.168.10.45, .67, 192.168.11.203). 2. Block outbound traffic to 203.0.113.47 at perimeter firewall. 3. Engage incident response team. 4. Submit NIS2 early warning notification to CSIRT within 24 hours. 5. Deploy ThreatFade endpoint agent across full fleet to identify additional compromised hosts.",
                "remediation_effort": "Immediate (0-24 hours)",
            },
            {
                "id": "TF-002",
                "title": "SQL Injection — Customer Portal Login Form",
                "severity": "CRITICAL",
                "cvss_score": 9.1,
                "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                "affected_systems": ["portal.acme-example.com — /login endpoint"],
                "mitre_ttp": ["T1190 — Exploit Public-Facing Application"],
                "description": "Unauthenticated SQL injection vulnerability in the customer portal login form allows extraction of the entire customer database including names, email addresses, hashed passwords, and account balances.",
                "evidence": "BugFlow confirmed via sqlmap — UNION-based injection on 'username' parameter. Successfully extracted 3 rows from 'customers' table in proof-of-concept (non-destructive test only).",
                "business_impact": "Full customer database exposure. GDPR Article 33 breach notification obligation. Reputational damage. Regulatory fines.",
                "remediation": "1. Apply parameterised queries / prepared statements immediately. 2. Deploy WAF rule blocking SQL metacharacters on login endpoint. 3. Rotate all customer credentials. 4. Notify DPA within 72 hours per GDPR Article 33.",
                "remediation_effort": "Short-term (1-7 days)",
            },
            {
                "id": "TF-003",
                "title": "IcedID Loader Pattern — Suspicious Download Activity",
                "severity": "CRITICAL",
                "cvss_score": 9.0,
                "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H",
                "affected_systems": ["192.168.12.88"],
                "mitre_ttp": ["T1566.001 — Phishing: Spearphishing Attachment", "T1059.001 — PowerShell"],
                "description": "ThreatFade detected traffic with z-score 3.89 consistent with IcedID loader download patterns on host 192.168.12.88. The host performed 14 DNS lookups to domains matching IcedID DGA patterns within a 10-minute window.",
                "evidence": "ThreatFade detection: z-score=3.89, entropy=2.1. DNS logs confirm 14 DGA-pattern lookups. Host has not been reimaged in 847 days.",
                "business_impact": "Potential banking trojan deployment risk. IcedID is commonly used as a precursor to ransomware. Possible credential theft from financial applications.",
                "remediation": "1. Isolate host 192.168.12.88 immediately. 2. Reimage from known-good baseline. 3. Review email logs for phishing delivery vector. 4. Block identified DGA domains at DNS level.",
                "remediation_effort": "Immediate (0-24 hours)",
            },
            {
                "id": "BF-001",
                "title": "Outdated Apache HTTP Server — CVE-2024-38476",
                "severity": "HIGH",
                "cvss_score": 8.1,
                "cvss_vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H",
                "affected_systems": ["api.acme-example.com (Apache/2.4.51)"],
                "mitre_ttp": ["T1190 — Exploit Public-Facing Application"],
                "description": "The API gateway runs Apache HTTP Server 2.4.51 which is vulnerable to CVE-2024-38476, a server-side request forgery and information disclosure vulnerability.",
                "evidence": "BugFlow Nuclei scan confirmed version 2.4.51. CVE-2024-38476 PoC available publicly.",
                "business_impact": "Potential access to internal services from external network. Information disclosure of internal network topology.",
                "remediation": "Upgrade Apache HTTP Server to 2.4.62 or later.",
                "remediation_effort": "Short-term (1-7 days)",
            },
            {
                "id": "BF-002",
                "title": "Weak Password Policy — Active Directory",
                "severity": "HIGH",
                "cvss_score": 7.5,
                "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                "affected_systems": ["Active Directory — ACME.LOCAL domain"],
                "mitre_ttp": ["T1110.001 — Brute Force: Password Guessing"],
                "description": "Active Directory password policy allows minimum 6-character passwords with no complexity requirements. 23% of sampled accounts (47 of 204) used passwords from the RockYou2024 wordlist.",
                "evidence": "BugFlow AD audit identified policy: MinPasswordLength=6, ComplexityEnabled=False. Hashcat cracked 47 NTLM hashes from DC sync in under 4 hours using RockYou2024.",
                "business_impact": "Credential compromise enables lateral movement, privilege escalation, and domain takeover.",
                "remediation": "1. Enforce minimum 12-character passwords with complexity. 2. Enable MFA for all accounts — mandatory per NIS2 Article 21(2)(j). 3. Force password reset for all 47 compromised accounts. 4. Deploy Azure AD Password Protection or equivalent.",
                "remediation_effort": "Short-term (1-7 days)",
            },
            {
                "id": "RO-001",
                "title": "Exposed Internal Hostnames in Public DNS Records",
                "severity": "MEDIUM",
                "cvss_score": 5.3,
                "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N",
                "affected_systems": ["DNS — public zone acme-example.com"],
                "mitre_ttp": ["T1590.002 — Gather Victim Network Information: DNS"],
                "description": "ReconOS OSINT scan identified 14 internal hostnames exposed in public DNS records, including dev.acme-example.com (pointing to 10.0.0.x internal IP) and staging-api.acme-example.com.",
                "evidence": "ReconOS AfricanContextEngine DNS enumeration: 14 internal PTR records exposed. Zone transfer partially successful from ns2.acme-example.com.",
                "business_impact": "Reconnaissance enablement. Exposes internal architecture to threat actors prior to attack.",
                "remediation": "1. Remove internal hostnames from public DNS zone. 2. Disable zone transfers on public nameservers. 3. Audit all DNS records for internal exposure.",
                "remediation_effort": "Medium-term (1-4 weeks)",
            },
            {
                "id": "TF-004",
                "title": "Missing Network Segmentation — Flat Network Architecture",
                "severity": "MEDIUM",
                "cvss_score": 6.5,
                "cvss_vector": "CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                "affected_systems": ["Network infrastructure — full /16 subnet"],
                "mitre_ttp": ["T1021 — Remote Services", "T1018 — Remote System Discovery"],
                "description": "The internal network operates as a single flat /16 subnet with no VLAN segmentation between workstations, servers, and critical systems. ThreatFade detected lateral movement traffic patterns across the network.",
                "evidence": "Network traffic analysis: workstation-to-workstation SMB traffic observed. No ACLs between workstation and server subnets. ThreatFade lateral movement alert triggered 7 times during assessment.",
                "business_impact": "Any compromised endpoint has unrestricted access to all other systems. Enables rapid ransomware spread.",
                "remediation": "1. Implement VLAN segmentation (workstations, servers, DMZ, management). 2. Deploy micro-segmentation for critical assets. 3. Implement network ACLs between zones.",
                "remediation_effort": "Medium-term (1-4 weeks)",
            },
            {
                "id": "BF-003",
                "title": "Unencrypted Internal API Traffic (HTTP)",
                "severity": "MEDIUM",
                "cvss_score": 5.9,
                "cvss_vector": "CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N",
                "affected_systems": ["Internal API service — 192.168.20.10:8080"],
                "mitre_ttp": ["T1040 — Network Sniffing"],
                "description": "Internal microservice API communicates over HTTP (unencrypted) on port 8080, transmitting session tokens and customer data in cleartext.",
                "evidence": "BugFlow network capture on flat network segment. Captured 3 valid session tokens and 2 customer records in cleartext during 10-minute passive capture.",
                "business_impact": "Session hijacking and customer data exposure risk. DORA ICT risk management gap.",
                "remediation": "Enforce TLS 1.2+ on all internal API communications. Implement mutual TLS for service-to-service authentication.",
                "remediation_effort": "Medium-term (1-4 weeks)",
            },
            {
                "id": "RO-002",
                "title": "Third-Party SaaS Credentials in Public GitHub Repository",
                "severity": "MEDIUM",
                "cvss_score": 6.8,
                "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N",
                "affected_systems": ["github.com/acme-corp — dev repository (public)"],
                "mitre_ttp": ["T1552.001 — Unsecured Credentials: Credentials in Files"],
                "description": "ReconOS OSINT scan identified a public GitHub repository containing hardcoded Paystack test API keys and an AWS access key ID in a committed .env file.",
                "evidence": "ReconOS Nigerian fintech detector (inherited from Tinlance open-source contributions) flagged Paystack key pattern. AWS key validated as active via sts:GetCallerIdentity.",
                "business_impact": "Paystack account compromise. AWS resource abuse and potential data access.",
                "remediation": "1. Immediately revoke and rotate exposed credentials. 2. Make repository private or remove sensitive files. 3. Implement git-secrets or TruffleHog pre-commit hooks. 4. Audit all repositories for credential exposure.",
                "remediation_effort": "Immediate (0-24 hours)",
            },
            {
                "id": "BF-004",
                "title": "Missing Security Headers on Customer Portal",
                "severity": "LOW",
                "cvss_score": 3.7,
                "cvss_vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:N",
                "affected_systems": ["portal.acme-example.com"],
                "mitre_ttp": ["T1185 — Browser Session Hijacking"],
                "description": "Customer portal missing: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, and Permissions-Policy headers.",
                "evidence": "BugFlow HTTP header scan confirmed absence of 5 security headers. Clickjacking PoC confirmed with X-Frame-Options missing.",
                "business_impact": "Clickjacking, MIME-type sniffing, and information leakage risks.",
                "remediation": "Add security headers to web server configuration. Use SecurityHeaders.com to validate.",
                "remediation_effort": "Short-term (1-7 days)",
            },
            {
                "id": "BF-005",
                "title": "Default SNMP Community String on Network Devices",
                "severity": "LOW",
                "cvss_score": 2.7,
                "cvss_vector": "CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:N",
                "affected_systems": ["192.168.1.1 — Core switch", "192.168.1.2 — Distribution switch"],
                "mitre_ttp": ["T1602 — Data from Configuration Repository"],
                "description": "Network switches using default SNMP community string 'public', enabling read access to network topology and device configuration.",
                "evidence": "BugFlow SNMP scan confirmed community string 'public' on 2 core switches. Successfully retrieved interface table and routing table.",
                "business_impact": "Network topology disclosure enabling more targeted attacks.",
                "remediation": "Change SNMP community strings to complex unique values. Implement SNMPv3 with authentication.",
                "remediation_effort": "Short-term (1-7 days)",
            },
            {
                "id": "RO-003",
                "title": "Informal Patch Management Process",
                "severity": "INFO",
                "cvss_score": 0.0,
                "cvss_vector": "N/A",
                "affected_systems": ["Organisational process — IT Operations"],
                "mitre_ttp": ["T1190 — Exploit Public-Facing Application (risk factor)"],
                "description": "No formal patch management policy or tooling identified. 23 systems show OS versions more than 6 months behind current release.",
                "evidence": "BugFlow asset inventory: 23 hosts with end-of-support or critically outdated OS versions. No WSUS or SCCM deployment confirmed.",
                "business_impact": "Increased attack surface from unpatched vulnerabilities over time. NIS2 risk management requirement gap.",
                "remediation": "Implement formal patch management policy with defined SLAs. Deploy automated patching tool (WSUS, Intune, or equivalent).",
                "remediation_effort": "Medium-term (1-4 weeks)",
            },
        ],
        "compliance": {
            "nis2_applicable": True,
            "dora_applicable": False,
            "nis2_gaps": [
                ("Risk management policies",            "Article 21(2)(a)", "PARTIAL", "Policy exists but not formally documented or board-approved"),
                ("Incident handling procedures",        "Article 21(2)(b)", "GAP",     "No formal IR plan. Active incident (TF-001) has no documented response procedure"),
                ("Business continuity & recovery",      "Article 21(2)(c)", "PARTIAL", "BCP exists for operational systems but not tested in 18 months"),
                ("Supply chain security",              "Article 21(2)(d)", "GAP",     "No vendor security assessment programme. RO-002 credentials from third-party integration"),
                ("Network & information system security","Article 21(2)(e)", "GAP",    "Flat network, no segmentation, active C2 beacon undetected prior to assessment"),
                ("Policies on cryptography",           "Article 21(2)(h)", "PARTIAL", "HTTPS on external systems. Internal API traffic unencrypted (BF-003)"),
                ("Human resources security",           "Article 21(2)(i)", "PARTIAL", "Basic onboarding but no security awareness programme"),
                ("Multi-factor authentication",        "Article 21(2)(j)", "GAP",     "MFA not enforced on AD or VPN. Mandatory under NIS2"),
                ("Incident reporting (24hr/72hr)",     "Article 23",       "GAP",     "TF-001 C2 incident may already require 24hr CSIRT notification"),
                ("Management accountability",          "Article 20",       "GAP",     "No designated CISO or security accountability at board level"),
            ],
            "dora_gaps": [],
            "compliance_summary": "Acme Financial Services has significant NIS2 compliance gaps. 6 of 10 assessed controls are non-compliant. The October 2026 compliance deadline is approaching. Immediate remediation of critical gaps is required to avoid fines of up to €10 million.",
        },
        "threatfade_detections": [
            {"timestamp": "2026-05-27 09:14:22", "host": "192.168.10.45", "threat": "Cobalt Strike C2 Beacon", "z_score": 7.01, "severity": "CRITICAL", "mitre": "T1071.001"},
            {"timestamp": "2026-05-27 09:14:23", "host": "192.168.10.67", "threat": "Cobalt Strike C2 Beacon", "z_score": 6.87, "severity": "CRITICAL", "mitre": "T1071.001"},
            {"timestamp": "2026-05-27 11:30:05", "host": "192.168.12.88", "threat": "IcedID Loader Pattern",   "z_score": 3.89, "severity": "CRITICAL", "mitre": "T1566.001"},
            {"timestamp": "2026-05-28 14:22:11", "host": "192.168.11.203","threat": "Cobalt Strike C2 Beacon", "z_score": 7.14, "severity": "CRITICAL", "mitre": "T1573"},
            {"timestamp": "2026-05-29 08:45:00", "host": "192.168.10.45", "threat": "Lateral Movement SMB",    "z_score": 4.21, "severity": "HIGH",     "mitre": "T1021"},
        ],
        "remediation_roadmap": [
            {"phase": "Immediate (0-24 hrs)",  "priority": 1, "actions": ["Isolate TF-001 hosts", "Block C2 IP at perimeter", "Notify CSIRT (NIS2)", "Revoke exposed credentials (RO-002)", "Begin IR process"]},
            {"phase": "Short-term (1-7 days)", "priority": 2, "actions": ["Patch SQLi (TF-002)", "Upgrade Apache (BF-001)", "Force AD password reset", "Add security headers (BF-004)", "Change SNMP strings (BF-005)"]},
            {"phase": "Medium-term (1-4 wks)", "priority": 3, "actions": ["Implement network segmentation", "Enforce internal TLS (BF-003)", "Clean up DNS (RO-001)", "Deploy MFA on AD + VPN", "Implement patch management"]},
            {"phase": "Long-term (1-3 months)","priority": 4, "actions": ["Deploy ThreatFade across full fleet", "Establish NIS2 compliance programme", "Board-level CISO appointment", "Security awareness training", "Vendor security assessment programme"]},
        ],
    }


# ══════════════════════════════════════════════════════════════════════════════
# PDF REPORT
# ══════════════════════════════════════════════════════════════════════════════

def severity_count(findings, sev):
    return sum(1 for f in findings if f["severity"] == sev)

def build_pdf(data: dict, out_path: str):
    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2*cm,
        title=f"Security Assessment Report — {data['meta']['client_name']}",
        author="Tinlance Limited",
        subject="FDSE Security Assessment",
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Helper styles ──────────────────────────────────────────────────────
    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    cover_title = S("CoverTitle", fontSize=28, textColor=TEAL, fontName="Helvetica-Bold",
                    leading=34, alignment=TA_LEFT, spaceAfter=8)
    cover_sub   = S("CoverSub",   fontSize=14, textColor=LIGHT, fontName="Helvetica",
                    leading=20, alignment=TA_LEFT, spaceAfter=6)
    cover_meta  = S("CoverMeta",  fontSize=10, textColor=MUTED, fontName="Helvetica",
                    leading=14, alignment=TA_LEFT)
    h1          = S("H1", fontSize=16, textColor=TEAL, fontName="Helvetica-Bold",
                    leading=22, spaceBefore=18, spaceAfter=8)
    h2          = S("H2", fontSize=13, textColor=LIGHT, fontName="Helvetica-Bold",
                    leading=18, spaceBefore=14, spaceAfter=6)
    body        = S("Body", fontSize=9.5, textColor=colors.HexColor("#c4cad6"), fontName="Helvetica",
                    leading=14, spaceAfter=6, alignment=TA_JUSTIFY)
    label       = S("Label", fontSize=8, textColor=TEAL, fontName="Helvetica-Bold",
                    leading=11, spaceAfter=2)
    bullet_s    = S("Bullet", fontSize=9.5, textColor=colors.HexColor("#c4cad6"), fontName="Helvetica",
                    leading=14, spaceAfter=4, leftIndent=14, bulletIndent=4)

    def HR():
        return HRFlowable(width="100%", thickness=0.5, color=TEAL_DARK, spaceAfter=8, spaceBefore=4)

    def SB(h=6):
        return Spacer(1, h)

    m = data["meta"]
    f = data["findings"]
    e = data["executive"]

    # ══ COVER PAGE ════════════════════════════════════════════════════════
    story.append(SB(40))
    story.append(Paragraph("TINLANCE", S("Brand", fontSize=11, textColor=TEAL,
                 fontName="Helvetica-Bold", leading=14)))
    story.append(SB(16))
    story.append(Paragraph("Security Assessment Report", cover_title))
    story.append(Paragraph(m["client_name"], cover_sub))
    story.append(HR())
    story.append(SB(8))

    meta_rows = [
        ["Engagement Type", m["engagement_type"]],
        ["Assessment Period", f"{m['start_date']} — {m['end_date']}"],
        ["Report Date",      m["report_date"]],
        ["Assessor",         m["assessor"]],
        ["Classification",   m["classification"]],
        ["Version",          m["version"]],
    ]
    mt = Table(meta_rows, colWidths=[4*cm, 13*cm])
    mt.setStyle(TableStyle([
        ("FONTNAME",   (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("FONTNAME",   (0,0), (0,-1),  "Helvetica-Bold"),
        ("TEXTCOLOR",  (0,0), (0,-1),  TEAL),
        ("TEXTCOLOR",  (1,0), (1,-1),  LIGHT),
        ("BACKGROUND", (0,0), (-1,-1), DARK2),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [DARK2, DARK3]),
        ("GRID",       (0,0), (-1,-1), 0.3, colors.HexColor("#1a1e2a")),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING", (0,0),(-1,-1), 10),
    ]))
    story.append(mt)
    story.append(SB(20))

    # Overall risk badge
    risk = e["overall_risk"]
    risk_col = SEVERITY_COLORS.get(risk, MEDIUM_C)
    risk_t = Table([[f"OVERALL RISK: {risk}  |  Score: {e['risk_score']}/10"]],
                   colWidths=[17*cm])
    risk_t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), risk_col),
        ("TEXTCOLOR",    (0,0),(-1,-1), DARK),
        ("FONTNAME",     (0,0),(-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0),(-1,-1), 13),
        ("ALIGN",        (0,0),(-1,-1), "CENTER"),
        ("TOPPADDING",   (0,0),(-1,-1), 10),
        ("BOTTOMPADDING",(0,0),(-1,-1), 10),
    ]))
    story.append(risk_t)

    # Severity summary bar
    story.append(SB(14))
    counts = {s: severity_count(f, s) for s in ["CRITICAL","HIGH","MEDIUM","LOW","INFO"]}
    sev_data = [["CRITICAL","HIGH","MEDIUM","LOW","INFO"],
                [str(counts["CRITICAL"]),str(counts["HIGH"]),str(counts["MEDIUM"]),
                 str(counts["LOW"]),str(counts["INFO"])]]
    st = Table(sev_data, colWidths=[3.4*cm]*5)
    st.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(0,0), CRITICAL_C),
        ("BACKGROUND",   (1,0),(1,0), HIGH_C),
        ("BACKGROUND",   (2,0),(2,0), MEDIUM_C),
        ("BACKGROUND",   (3,0),(3,0), LOW_C),
        ("BACKGROUND",   (4,0),(4,0), INFO_C),
        ("TEXTCOLOR",    (0,0),(-1,0), DARK),
        ("FONTNAME",     (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0),(-1,0), 9),
        ("BACKGROUND",   (0,1),(-1,1), DARK3),
        ("TEXTCOLOR",    (0,1),(0,1), CRITICAL_C),
        ("TEXTCOLOR",    (1,1),(1,1), HIGH_C),
        ("TEXTCOLOR",    (2,1),(2,1), MEDIUM_C),
        ("TEXTCOLOR",    (3,1),(3,1), LOW_C),
        ("TEXTCOLOR",    (4,1),(4,1), INFO_C),
        ("FONTNAME",     (0,1),(-1,1), "Helvetica-Bold"),
        ("FONTSIZE",     (0,1),(-1,1), 20),
        ("ALIGN",        (0,0),(-1,-1), "CENTER"),
        ("TOPPADDING",   (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("GRID",         (0,0),(-1,-1), 0.3, DARK),
    ]))
    story.append(st)
    story.append(PageBreak())

    # ══ EXECUTIVE SUMMARY ════════════════════════════════════════════════
    story.append(Paragraph("01 — Executive Summary", h1))
    story.append(HR())
    story.append(Paragraph(e["summary"], body))
    story.append(SB(10))
    story.append(Paragraph("Business Impact", h2))
    story.append(Paragraph(e["business_impact"], body))
    story.append(SB(10))
    story.append(Paragraph("Key Recommendations", h2))
    for rec in e["key_recommendations"]:
        story.append(Paragraph(f"• {rec}", bullet_s))
    story.append(PageBreak())

    # ══ SCOPE & METHODOLOGY ══════════════════════════════════════════════
    sc = data["scope"]
    story.append(Paragraph("02 — Scope & Methodology", h1))
    story.append(HR())
    story.append(Paragraph("In Scope", h2))
    for item in sc["in_scope"]:
        story.append(Paragraph(f"• {item}", bullet_s))
    story.append(SB(8))
    story.append(Paragraph("Out of Scope", h2))
    for item in sc["out_of_scope"]:
        story.append(Paragraph(f"• {item}", bullet_s))
    story.append(SB(8))
    story.append(Paragraph("Methodology", label))
    story.append(Paragraph(sc["methodology"], body))
    story.append(SB(6))
    story.append(Paragraph("Tools Used", label))
    story.append(Paragraph(" · ".join(sc["tools"]), body))
    story.append(PageBreak())

    # ══ TECHNICAL FINDINGS ═══════════════════════════════════════════════
    story.append(Paragraph("03 — Technical Findings", h1))
    story.append(HR())

    for idx, finding in enumerate(f):
        sev   = finding["severity"]
        sc_   = finding["cvss_score"]
        s_col = SEVERITY_COLORS.get(sev, MUTED)

        # Finding header row
        hdr = Table([[finding["id"], finding["title"], sev, f"CVSS {sc_}"]],
                    colWidths=[1.8*cm, 10*cm, 2.2*cm, 3*cm])
        hdr.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), s_col),
            ("TEXTCOLOR",    (0,0),(-1,-1), DARK),
            ("FONTNAME",     (0,0),(-1,-1), "Helvetica-Bold"),
            ("FONTSIZE",     (0,0),(-1,-1), 9),
            ("ALIGN",        (2,0),(-1,-1), "CENTER"),
            ("TOPPADDING",   (0,0),(-1,-1), 7),
            ("BOTTOMPADDING",(0,0),(-1,-1), 7),
            ("LEFTPADDING",  (0,0),(0,-1),  8),
        ]))
        story.append(KeepTogether([hdr]))

        # Finding details table
        rows = []
        for lbl, val in [
            ("CVSS Vector",       finding.get("cvss_vector","N/A")),
            ("Affected Systems",  "\n".join(finding.get("affected_systems",[]))),
            ("MITRE ATT&CK",     "\n".join(finding.get("mitre_ttp",[]))),
            ("Description",       finding["description"]),
            ("Evidence",          finding["evidence"]),
            ("Business Impact",   finding["business_impact"]),
            ("Remediation",       finding["remediation"]),
            ("Effort",            finding.get("remediation_effort","—")),
        ]:
            rows.append([
                Paragraph(lbl, S(f"FL{idx}", fontSize=8, textColor=TEAL,
                          fontName="Helvetica-Bold", leading=11)),
                Paragraph(val, S(f"FV{idx}", fontSize=8.5,
                          textColor=colors.HexColor("#c4cad6"),
                          fontName="Helvetica", leading=13)),
            ])

        dt = Table(rows, colWidths=[3*cm, 14*cm])
        dt.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(0,-1), DARK3),
            ("BACKGROUND",    (1,0),(1,-1), DARK2),
            ("ROWBACKGROUNDS",(1,0),(1,-1), [DARK2, DARK3]),
            ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#1a1e2a")),
            ("TOPPADDING",    (0,0),(-1,-1), 5),
            ("BOTTOMPADDING", (0,0),(-1,-1), 5),
            ("LEFTPADDING",   (0,0),(0,-1),  8),
            ("LEFTPADDING",   (1,0),(1,-1),  8),
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ]))
        story.append(dt)
        story.append(SB(12))

    story.append(PageBreak())

    # ══ THREATFADE DETECTIONS ═════════════════════════════════════════════
    story.append(Paragraph("04 — ThreatFade Live Detections", h1))
    story.append(HR())
    story.append(Paragraph(
        "The following threats were detected live by ThreatFade v0.2.0-beta during the "
        "assessment engagement. All detections are based on entropy analysis and z-score "
        "statistical modelling validated against known malware traffic signatures.", body))
    story.append(SB(8))

    tf_rows = [["Timestamp", "Host", "Threat", "Z-Score", "Severity", "MITRE TTP"]]
    for det in data["threatfade_detections"]:
        tf_rows.append([
            det["timestamp"], det["host"], det["threat"],
            str(det["z_score"]), det["severity"], det["mitre"]
        ])
    tft = Table(tf_rows, colWidths=[3.2*cm, 2.8*cm, 4.5*cm, 1.8*cm, 2*cm, 3*cm])
    tft.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,0), DARK),
        ("TEXTCOLOR",    (0,0),(-1,0), TEAL),
        ("FONTNAME",     (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0),(-1,-1), 8),
        ("FONTNAME",     (0,1),(-1,-1), "Helvetica"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[DARK2, DARK3]),
        ("TEXTCOLOR",    (0,1),(-1,-1), LIGHT),
        ("GRID",         (0,0),(-1,-1), 0.3, colors.HexColor("#1a1e2a")),
        ("TOPPADDING",   (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",  (0,0),(-1,-1), 6),
    ]))
    story.append(tft)
    story.append(PageBreak())

    # ══ COMPLIANCE MAPPING ═══════════════════════════════════════════════
    comp = data["compliance"]
    story.append(Paragraph("05 — NIS2 Compliance Gap Assessment", h1))
    story.append(HR())
    story.append(Paragraph(comp["compliance_summary"], body))
    story.append(SB(10))

    STATUS_COLORS = {
        "COMPLIANT": GREEN_C,
        "PARTIAL":   MEDIUM_C,
        "GAP":       CRITICAL_C,
        "N/A":       MUTED,
    }
    nis2_rows = [["NIS2 Control", "Reference", "Status", "Gap Details"]]
    for ctrl, ref, status, detail in comp["nis2_gaps"]:
        nis2_rows.append([ctrl, ref, status, detail])

    nt = Table(nis2_rows, colWidths=[4.5*cm, 2.5*cm, 2*cm, 8*cm])
    nt_style = [
        ("BACKGROUND",   (0,0),(-1,0), DARK),
        ("TEXTCOLOR",    (0,0),(-1,0), TEAL),
        ("FONTNAME",     (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0),(-1,-1), 8),
        ("FONTNAME",     (0,1),(-1,-1), "Helvetica"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[DARK2, DARK3]),
        ("TEXTCOLOR",    (0,1),(-1,-1), LIGHT),
        ("GRID",         (0,0),(-1,-1), 0.3, colors.HexColor("#1a1e2a")),
        ("TOPPADDING",   (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",  (0,0),(-1,-1), 6),
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
    ]
    for i, row in enumerate(nis2_rows[1:], start=1):
        status = row[2]
        col    = STATUS_COLORS.get(status, MUTED)
        nt_style.append(("TEXTCOLOR", (2,i), (2,i), col))
        nt_style.append(("FONTNAME",  (2,i), (2,i), "Helvetica-Bold"))
    nt.setStyle(TableStyle(nt_style))
    story.append(nt)
    story.append(PageBreak())

    # ══ REMEDIATION ROADMAP ═══════════════════════════════════════════════
    story.append(Paragraph("06 — Remediation Roadmap", h1))
    story.append(HR())
    story.append(Paragraph(
        "The following prioritised roadmap translates all findings into a time-phased "
        "action plan. Phase 1 addresses active threats requiring immediate containment. "
        "Subsequent phases address systemic security gaps.", body))
    story.append(SB(10))

    phase_colors = [CRITICAL_C, HIGH_C, MEDIUM_C, LOW_C]
    for i, phase in enumerate(data["remediation_roadmap"]):
        pc = phase_colors[i % len(phase_colors)]
        ph = Table([[f"Phase {phase['priority']} — {phase['phase']}"]],
                   colWidths=[17*cm])
        ph.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), pc),
            ("TEXTCOLOR",    (0,0),(-1,-1), DARK),
            ("FONTNAME",     (0,0),(-1,-1), "Helvetica-Bold"),
            ("FONTSIZE",     (0,0),(-1,-1), 10),
            ("TOPPADDING",   (0,0),(-1,-1), 7),
            ("BOTTOMPADDING",(0,0),(-1,-1), 7),
            ("LEFTPADDING",  (0,0),(-1,-1), 10),
        ]))
        story.append(ph)
        for action in phase["actions"]:
            story.append(Paragraph(f"→  {action}", bullet_s))
        story.append(SB(10))

    # ══ FOOTER ════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(SB(20))
    story.append(HR())
    story.append(Paragraph(
        f"This report was prepared by Tinlance Limited for {m['client_name']}. "
        "It is classified CONFIDENTIAL and intended solely for the named client. "
        "Unauthorised distribution is prohibited.",
        S("Footer", fontSize=8, textColor=MUTED, fontName="Helvetica",
          leading=12, alignment=TA_CENTER)))
    story.append(SB(4))
    story.append(Paragraph(
        "Tinlance Limited  ·  RC: 7962164  ·  tinlance.com  ·  "
        f"ThreatFade v0.2.0-beta  ·  {m['report_date']}",
        S("Footer2", fontSize=8, textColor=TEAL, fontName="Helvetica-Bold",
          leading=12, alignment=TA_CENTER)))

    doc.build(story)
    print(f"  ✓ PDF generated: {out_path}")


# ══════════════════════════════════════════════════════════════════════════════
# WORD (DOCX) REPORT
# ══════════════════════════════════════════════════════════════════════════════

def _set_cell_bg(cell, hex_color):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  hex_color.lstrip("#"))
    tcPr.append(shd)

def _add_run(para, text, bold=False, color=None, size=None, italic=False):
    run = para.add_run(text)
    run.bold   = bold
    run.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*tuple(int(color.lstrip("#")[i:i+2],16) for i in (0,2,4)))
    if size:
        run.font.size = Pt(size)
    return run

def build_docx(data: dict, out_path: str):
    doc = DocxDocument()

    # Page margins
    for section in doc.sections:
        section.left_margin   = Cm(2)
        section.right_margin  = Cm(2)
        section.top_margin    = Cm(2.5)
        section.bottom_margin = Cm(2)

    m = data["meta"]
    f = data["findings"]
    e = data["executive"]

    SEV_HEX = {"CRITICAL":"ff4d6d","HIGH":"ff8c42","MEDIUM":"f5c842","LOW":"4ecdc4","INFO":"6c8ebf"}
    STATUS_HEX = {"COMPLIANT":"2ecc71","PARTIAL":"f5c842","GAP":"ff4d6d","N/A":"8892a4"}

    def H(level, text, color="00e5c8"):
        p = doc.add_heading(text, level=level)
        for run in p.runs:
            run.font.color.rgb = RGBColor(*tuple(int(color[i:i+2],16) for i in (0,2,4)))
        return p

    def P(text, size=10, color="c4cad6", bold=False, italic=False):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.font.size  = Pt(size)
        r.font.color.rgb = RGBColor(*tuple(int(color[i:i+2],16) for i in (0,2,4)))
        r.bold   = bold
        r.italic = italic
        p.paragraph_format.space_after = Pt(4)
        return p

    def meta_table(rows):
        t = doc.add_table(rows=len(rows), cols=2)
        t.style = "Table Grid"
        for i, (lbl, val) in enumerate(rows):
            c0, c1 = t.rows[i].cells
            _set_cell_bg(c0, "0d1018")
            _set_cell_bg(c1, "12151e")
            p0 = c0.paragraphs[0]
            _add_run(p0, lbl, bold=True, color="00e5c8", size=9)
            p1 = c1.paragraphs[0]
            _add_run(p1, val, color="e8ecf4", size=9)
        return t

    # ── Cover ──────────────────────────────────────────────────────────────
    p = doc.add_paragraph()
    _add_run(p, "TINLANCE LIMITED", bold=True, color="00e5c8", size=11)

    p = doc.add_paragraph()
    _add_run(p, "Security Assessment Report", bold=True, color="00e5c8", size=24)

    p = doc.add_paragraph()
    _add_run(p, m["client_name"], bold=True, color="e8ecf4", size=16)

    doc.add_paragraph()
    meta_table([
        ("Engagement", m["engagement_type"]),
        ("Period",     f"{m['start_date']} — {m['end_date']}"),
        ("Date",       m["report_date"]),
        ("Assessor",   m["assessor"]),
        ("Classification", m["classification"]),
    ])
    doc.add_page_break()

    # ── Executive Summary ──────────────────────────────────────────────────
    H(1, "01 — Executive Summary")
    P(e["summary"])
    H(2, "Business Impact", color="ff4d6d")
    P(e["business_impact"])
    H(2, "Key Recommendations", color="00e5c8")
    for rec in e["key_recommendations"]:
        p = doc.add_paragraph(style="List Bullet")
        _add_run(p, rec, color="c4cad6", size=10)
    doc.add_page_break()

    # ── Scope ──────────────────────────────────────────────────────────────
    sc = data["scope"]
    H(1, "02 — Scope & Methodology")
    H(2, "In Scope")
    for item in sc["in_scope"]:
        p = doc.add_paragraph(style="List Bullet")
        _add_run(p, item, color="c4cad6", size=10)
    H(2, "Methodology")
    P(sc["methodology"])
    doc.add_page_break()

    # ── Findings ───────────────────────────────────────────────────────────
    H(1, "03 — Technical Findings")
    for finding in f:
        sev    = finding["severity"]
        shex   = SEV_HEX.get(sev, "8892a4")
        t      = doc.add_table(rows=1, cols=4)
        t.style = "Table Grid"
        for ci, (txt, w) in enumerate([(finding["id"],1),(finding["title"],5),(sev,1),(f"CVSS {finding['cvss_score']}",1)]):
            c = t.rows[0].cells[ci]
            _set_cell_bg(c, shex)
            _add_run(c.paragraphs[0], txt, bold=True, color="080a0f", size=9)
        doc.add_paragraph()
        detail_rows = [
            ("CVSS Vector",      finding.get("cvss_vector","N/A")),
            ("Affected Systems", "\n".join(finding.get("affected_systems",[]))),
            ("MITRE ATT&CK",    "\n".join(finding.get("mitre_ttp",[]))),
            ("Description",      finding["description"]),
            ("Evidence",         finding["evidence"]),
            ("Business Impact",  finding["business_impact"]),
            ("Remediation",      finding["remediation"]),
            ("Effort",           finding.get("remediation_effort","—")),
        ]
        dt = doc.add_table(rows=len(detail_rows), cols=2)
        dt.style = "Table Grid"
        for i, (lbl, val) in enumerate(detail_rows):
            c0, c1 = dt.rows[i].cells
            _set_cell_bg(c0, "0d1018")
            _set_cell_bg(c1, "12151e" if i%2==0 else "0d1018")
            _add_run(c0.paragraphs[0], lbl, bold=True, color="00e5c8", size=8)
            _add_run(c1.paragraphs[0], val, color="c4cad6", size=9)
        doc.add_paragraph()
    doc.add_page_break()

    # ── Compliance ─────────────────────────────────────────────────────────
    comp = data["compliance"]
    H(1, "04 — NIS2 Compliance Gap Assessment")
    P(comp["compliance_summary"])
    doc.add_paragraph()
    nis2_t = doc.add_table(rows=1+len(comp["nis2_gaps"]), cols=4)
    nis2_t.style = "Table Grid"
    for ci, hdr in enumerate(["NIS2 Control","Reference","Status","Gap Details"]):
        c = nis2_t.rows[0].cells[ci]
        _set_cell_bg(c, "080a0f")
        _add_run(c.paragraphs[0], hdr, bold=True, color="00e5c8", size=9)
    for i, (ctrl, ref, status, detail) in enumerate(comp["nis2_gaps"], start=1):
        shex2 = STATUS_HEX.get(status, "8892a4")
        cells = nis2_t.rows[i].cells
        for ci, txt in enumerate([ctrl, ref, status, detail]):
            _set_cell_bg(cells[ci], "0d1018" if i%2==0 else "12151e")
        _add_run(cells[0].paragraphs[0], ctrl,   color="c4cad6", size=9)
        _add_run(cells[1].paragraphs[0], ref,    color="c4cad6", size=9)
        _add_run(cells[2].paragraphs[0], status, bold=True, color=shex2, size=9)
        _add_run(cells[3].paragraphs[0], detail, color="c4cad6", size=9)
    doc.add_page_break()

    # ── Remediation Roadmap ────────────────────────────────────────────────
    H(1, "05 — Remediation Roadmap")
    phase_hex = ["ff4d6d","ff8c42","f5c842","4ecdc4"]
    for i, phase in enumerate(data["remediation_roadmap"]):
        ph = phase_hex[i % len(phase_hex)]
        t  = doc.add_table(rows=1, cols=1)
        t.style = "Table Grid"
        c  = t.rows[0].cells[0]
        _set_cell_bg(c, ph)
        _add_run(c.paragraphs[0], f"Phase {phase['priority']} — {phase['phase']}",
                 bold=True, color="080a0f", size=11)
        for action in phase["actions"]:
            p = doc.add_paragraph(style="List Bullet")
            _add_run(p, action, color="c4cad6", size=10)
        doc.add_paragraph()

    doc.save(out_path)
    print(f"  ✓ DOCX generated: {out_path}")


# ══════════════════════════════════════════════════════════════════════════════
# EXCEL REPORT
# ══════════════════════════════════════════════════════════════════════════════

def build_excel(data: dict, out_path: str):
    wb  = openpyxl.Workbook()
    m   = data["meta"]
    f   = data["findings"]
    e   = data["executive"]

    DARK_FILL   = PatternFill("solid", fgColor="080a0f")
    DARK2_FILL  = PatternFill("solid", fgColor="0d1018")
    DARK3_FILL  = PatternFill("solid", fgColor="12151e")
    TEAL_FILL   = PatternFill("solid", fgColor="00e5c8")
    CRIT_FILL   = PatternFill("solid", fgColor="ff4d6d")
    HIGH_FILL   = PatternFill("solid", fgColor="ff8c42")
    MED_FILL    = PatternFill("solid", fgColor="f5c842")
    LOW_FILL    = PatternFill("solid", fgColor="4ecdc4")
    INFO_FILL   = PatternFill("solid", fgColor="6c8ebf")
    GREEN_FILL  = PatternFill("solid", fgColor="2ecc71")

    SEV_FILLS   = {"CRITICAL":CRIT_FILL,"HIGH":HIGH_FILL,"MEDIUM":MED_FILL,"LOW":LOW_FILL,"INFO":INFO_FILL}
    STATUS_FILLS= {"COMPLIANT":GREEN_FILL,"PARTIAL":MED_FILL,"GAP":CRIT_FILL}

    TEAL_FONT   = Font(name="Arial", bold=True, color="00e5c8", size=10)
    WHITE_FONT  = Font(name="Arial", color="e8ecf4", size=10)
    DARK_FONT   = Font(name="Arial", bold=True, color="080a0f", size=10)
    MUTED_FONT  = Font(name="Arial", color="8892a4", size=9)
    BODY_FONT   = Font(name="Arial", color="c4cad6", size=9)
    BOLD_WHITE  = Font(name="Arial", bold=True, color="e8ecf4", size=10)

    thin = Side(style="thin", color="1a1e2a")
    thin_border = Border(left=thin, right=thin, top=thin, bottom=thin)

    def hdr_row(ws, row, values, fills=None):
        for ci, val in enumerate(values, 1):
            c = ws.cell(row=row, column=ci, value=val)
            c.font   = TEAL_FONT
            c.fill   = DARK_FILL
            c.border = thin_border
            c.alignment = Alignment(wrap_text=True, vertical="center")
            if fills and ci-1 < len(fills) and fills[ci-1]:
                c.fill = fills[ci-1]

    def data_row(ws, row, values, fill=None):
        f = fill or (DARK2_FILL if row % 2 == 0 else DARK3_FILL)
        for ci, val in enumerate(values, 1):
            c = ws.cell(row=row, column=ci, value=val)
            c.font      = BODY_FONT
            c.fill      = f
            c.border    = thin_border
            c.alignment = Alignment(wrap_text=True, vertical="top")

    # ── Sheet 1: Dashboard ────────────────────────────────────────────────
    ws1 = wb.active
    ws1.title = "Dashboard"
    ws1.sheet_properties.tabColor = "00e5c8"

    ws1["A1"] = "TINLANCE SECURITY ASSESSMENT REPORT"
    ws1["A1"].font = Font(name="Arial", bold=True, color="00e5c8", size=16)
    ws1["A2"] = m["client_name"]
    ws1["A2"].font = Font(name="Arial", bold=True, color="e8ecf4", size=12)
    ws1["A3"] = f"Report Date: {m['report_date']}  |  Classification: {m['classification']}"
    ws1["A3"].font = MUTED_FONT

    # Overall risk
    ws1["A5"] = "OVERALL RISK"
    ws1["A5"].font = TEAL_FONT
    ws1["B5"] = e["overall_risk"]
    ws1["B5"].font = Font(name="Arial", bold=True, color="ff4d6d", size=14)
    ws1["C5"] = f"Score: {e['risk_score']}/10"
    ws1["C5"].font = WHITE_FONT

    # Severity counts
    ws1["A7"] = "Severity"
    ws1["B7"] = "Count"
    ws1["A7"].font = TEAL_FONT
    ws1["B7"].font = TEAL_FONT
    for ri, (sev, fill) in enumerate([
        ("CRITICAL",CRIT_FILL),("HIGH",HIGH_FILL),
        ("MEDIUM",MED_FILL),("LOW",LOW_FILL),("INFO",INFO_FILL)
    ], start=8):
        cnt = sum(1 for x in f if x["severity"]==sev)
        ws1.cell(ri,1,sev).font   = Font(name="Arial", bold=True, color="080a0f", size=10)
        ws1.cell(ri,1).fill       = fill
        ws1.cell(ri,2,cnt).font   = WHITE_FONT
        ws1.cell(ri,2).fill       = DARK2_FILL
        ws1.cell(ri,2).alignment  = Alignment(horizontal="center")

    # Bar chart
    chart    = BarChart()
    chart.type = "col"
    chart.title= "Findings by Severity"
    chart.y_axis.title = "Count"
    chart.x_axis.title = "Severity"
    chart.style = 10
    chart.width  = 14
    chart.height = 10
    data_ref   = Reference(ws1, min_col=2, min_row=7, max_row=12)
    cats_ref   = Reference(ws1, min_col=1, min_row=8, max_row=12)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats_ref)
    ws1.add_chart(chart, "D7")

    ws1.column_dimensions["A"].width = 18
    ws1.column_dimensions["B"].width = 10
    ws1.column_dimensions["C"].width = 20
    ws1.sheet_view.showGridLines = False

    # ── Sheet 2: Findings ─────────────────────────────────────────────────
    ws2 = wb.create_sheet("Findings")
    ws2.sheet_properties.tabColor = "ff4d6d"
    hdr_row(ws2, 1, ["ID","Title","Severity","CVSS","Affected Systems","MITRE TTP","Business Impact","Remediation","Effort"])
    for ri, finding in enumerate(f, start=2):
        sev_fill = SEV_FILLS.get(finding["severity"], INFO_FILL)
        row_fill  = DARK2_FILL if ri%2==0 else DARK3_FILL
        values    = [
            finding["id"], finding["title"], finding["severity"],
            finding["cvss_score"],
            "\n".join(finding.get("affected_systems",[])),
            "\n".join(finding.get("mitre_ttp",[])),
            finding["business_impact"], finding["remediation"],
            finding.get("remediation_effort","—"),
        ]
        data_row(ws2, ri, values, fill=row_fill)
        ws2.cell(ri,3).fill = sev_fill
        ws2.cell(ri,3).font = Font(name="Arial", bold=True, color="080a0f", size=9)

    for ci, width in zip(range(1,10),[8,30,10,8,20,20,30,30,15]):
        ws2.column_dimensions[get_column_letter(ci)].width = width
    ws2.row_dimensions[1].height = 20
    ws2.sheet_view.showGridLines  = False

    # ── Sheet 3: ThreatFade Detections ─────────────────────────────────────
    ws3 = wb.create_sheet("ThreatFade Detections")
    ws3.sheet_properties.tabColor = "00b8a0"
    hdr_row(ws3, 1, ["Timestamp","Host","Threat","Z-Score","Severity","MITRE TTP"])
    for ri, det in enumerate(data["threatfade_detections"], start=2):
        sev_fill = SEV_FILLS.get(det["severity"], INFO_FILL)
        values   = [det["timestamp"], det["host"], det["threat"],
                    det["z_score"], det["severity"], det["mitre"]]
        data_row(ws3, ri, values)
        ws3.cell(ri,5).fill = sev_fill
        ws3.cell(ri,5).font = Font(name="Arial", bold=True, color="080a0f", size=9)
    for ci, w in zip(range(1,7),[22,18,28,10,12,20]):
        ws3.column_dimensions[get_column_letter(ci)].width = w
    ws3.sheet_view.showGridLines = False

    # ── Sheet 4: NIS2 Compliance ───────────────────────────────────────────
    ws4 = wb.create_sheet("NIS2 Compliance")
    ws4.sheet_properties.tabColor = "f5c842"
    hdr_row(ws4, 1, ["NIS2 Control","Reference","Status","Gap Details"])
    for ri, (ctrl, ref, status, detail) in enumerate(data["compliance"]["nis2_gaps"], start=2):
        row_fill = DARK2_FILL if ri%2==0 else DARK3_FILL
        data_row(ws4, ri, [ctrl, ref, status, detail], fill=row_fill)
        sfill = STATUS_FILLS.get(status, INFO_FILL)
        ws4.cell(ri,3).fill = sfill
        ws4.cell(ri,3).font = Font(name="Arial", bold=True, color="080a0f", size=9)
    for ci, w in zip(range(1,5),[30,15,12,50]):
        ws4.column_dimensions[get_column_letter(ci)].width = w
    ws4.sheet_view.showGridLines = False

    # ── Sheet 5: Remediation Roadmap ──────────────────────────────────────
    ws5 = wb.create_sheet("Remediation Roadmap")
    ws5.sheet_properties.tabColor = "ff8c42"
    hdr_row(ws5, 1, ["Phase","Priority","Action","Category"])
    phase_fills = [CRIT_FILL, HIGH_FILL, MED_FILL, LOW_FILL]
    ri = 2
    for i, phase in enumerate(data["remediation_roadmap"]):
        pf = phase_fills[i % len(phase_fills)]
        for action in phase["actions"]:
            ws5.cell(ri,1,phase["phase"]).fill  = pf
            ws5.cell(ri,1).font                 = Font(name="Arial", bold=True, color="080a0f", size=9)
            ws5.cell(ri,2,phase["priority"]).fill= pf
            ws5.cell(ri,2).font                 = Font(name="Arial", bold=True, color="080a0f", size=9)
            ws5.cell(ri,2).alignment            = Alignment(horizontal="center")
            ws5.cell(ri,3,action).font          = BODY_FONT
            ws5.cell(ri,3).fill                 = DARK2_FILL if ri%2==0 else DARK3_FILL
            ws5.cell(ri,4,"Security").font      = MUTED_FONT
            ws5.cell(ri,4).fill                 = DARK2_FILL if ri%2==0 else DARK3_FILL
            ri += 1
    for ci, w in zip(range(1,5),[22,10,45,15]):
        ws5.column_dimensions[get_column_letter(ci)].width = w
    ws5.sheet_view.showGridLines = False

    wb.save(out_path)
    print(f"  ✓ Excel generated: {out_path}")


# ══════════════════════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Tinlance FDSE Report Generator")
    parser.add_argument("--input",   help="Path to JSON input file")
    parser.add_argument("--format",  default="all", choices=["pdf","docx","excel","all"])
    parser.add_argument("--client",  default="Client", help="Client name (used in filenames)")
    parser.add_argument("--out",     default=".", help="Output directory")
    parser.add_argument("--demo",    action="store_true", help="Generate demo report")
    args = parser.parse_args()

    if args.demo:
        data = build_demo_data()
    elif args.input:
        data = load_input(args.input)
    else:
        print("Error: provide --input <file.json> or --demo")
        sys.exit(1)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    slug = data["meta"]["client_name"].replace(" ","_").replace("/","_")[:30]
    date = datetime.now().strftime("%Y%m%d")

    print(f"\n🔐 Tinlance FDSE Report Generator")
    print(f"   Client : {data['meta']['client_name']}")
    print(f"   Findings: {len(data['findings'])}")
    print(f"   Output : {out}\n")

    if args.format in ("pdf",  "all"):
        build_pdf(data,   str(out / f"TinlanceReport_{slug}_{date}.pdf"))
    if args.format in ("docx", "all"):
        build_docx(data,  str(out / f"TinlanceReport_{slug}_{date}.docx"))
    if args.format in ("excel","all"):
        build_excel(data, str(out / f"TinlanceReport_{slug}_{date}.xlsx"))

    print(f"\n✅ All reports generated in: {out}")

if __name__ == "__main__":
    main()
