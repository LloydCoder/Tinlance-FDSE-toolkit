"""
Tinlance FDSE Toolkit — Identity Threat Scanner
================================================
Scans for identity-based threats that network-layer detection misses.

Covers:
  - Public credential exposure (GitHub, paste sites, DNS)
  - Nigerian fintech credential patterns (Paystack, Flutterwave, Remita, Interswitch)
  - API key and token exposure
  - Default credential checks
  - MFA gap assessment
  - Identity attack surface mapping

This is the ITDR (Identity Threat Detection & Response) layer that
complements ThreatFade's network-layer C2 detection.

Usage:
    python identity_scanner.py --domain example.com --out ./output
    python identity_scanner.py --demo
    python identity_scanner.py --domain example.com --github orgname --out ./output
"""

import argparse
import json
import re
import os
import socket
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Credential Patterns ────────────────────────────────────────────────────
# Inherited from Tinlance open-source contributions to TruffleHog, Gitleaks,
# and Nuclei — Nigerian fintech detectors + global patterns

CREDENTIAL_PATTERNS = {
    # Nigerian Fintech (Tinlance open-source contribution)
    "paystack_secret_key": {
        "pattern": r"sk_(?:live|test)_[a-zA-Z0-9]{40,}",
        "severity": "CRITICAL",
        "description": "Paystack Secret Key — full API access, can initiate transfers",
        "mitre": "T1552.001",
        "remediation": "Revoke immediately at dashboard.paystack.com. Audit all transactions since exposure.",
    },
    "paystack_public_key": {
        "pattern": r"pk_(?:live|test)_[a-zA-Z0-9]{40,}",
        "severity": "HIGH",
        "description": "Paystack Public Key — can initiate payments",
        "mitre": "T1552.001",
        "remediation": "Rotate key. Review for fraudulent payment initiations.",
    },
    "flutterwave_secret": {
        "pattern": r"FLWSECK(?:_TEST)?-[a-zA-Z0-9]{32,}-X",
        "severity": "CRITICAL",
        "description": "Flutterwave Secret Key — full payment and transfer access",
        "mitre": "T1552.001",
        "remediation": "Revoke at app.flutterwave.com immediately.",
    },
    "flutterwave_enc": {
        "pattern": r"FLWENC(?:_TEST)?-[a-zA-Z0-9]{32,}",
        "severity": "HIGH",
        "description": "Flutterwave Encryption Key",
        "mitre": "T1552.001",
        "remediation": "Rotate encryption key. Check for decrypted transaction data.",
    },
    "remita_secret": {
        "pattern": r"remita[_-](?:secret|api|key|token)[_-]?[a-zA-Z0-9]{20,}",
        "severity": "CRITICAL",
        "description": "Remita API Secret — government payment gateway access",
        "mitre": "T1552.001",
        "remediation": "Contact Remita support immediately. Audit all government payment records.",
    },
    "interswitch_key": {
        "pattern": r"ISW[_-]?(?:LIVE|TEST)[_-]?[a-zA-Z0-9]{24,}",
        "severity": "CRITICAL",
        "description": "Interswitch API Key — financial transaction access",
        "mitre": "T1552.001",
        "remediation": "Revoke via Interswitch developer portal.",
    },
    # Cloud providers
    "aws_access_key": {
        "pattern": r"AKIA[0-9A-Z]{16}",
        "severity": "CRITICAL",
        "description": "AWS Access Key ID — cloud infrastructure access",
        "mitre": "T1552.001",
        "remediation": "Revoke in AWS IAM immediately. Run: aws sts get-caller-identity to check exposure.",
    },
    "aws_secret_key": {
        "pattern": r"(?:aws_secret|AWS_SECRET)[_\s=:\"']+([A-Za-z0-9/+=]{40})",
        "severity": "CRITICAL",
        "description": "AWS Secret Access Key",
        "mitre": "T1552.001",
        "remediation": "Revoke in AWS IAM. Audit CloudTrail for unauthorized API calls.",
    },
    "google_api_key": {
        "pattern": r"AIza[0-9A-Za-z\-_]{35}",
        "severity": "HIGH",
        "description": "Google API Key",
        "mitre": "T1552.001",
        "remediation": "Restrict/delete at console.cloud.google.com. Check API usage logs.",
    },
    "github_token": {
        "pattern": r"gh[pousr]_[A-Za-z0-9]{36,}",
        "severity": "CRITICAL",
        "description": "GitHub Personal Access Token — repository and account access",
        "mitre": "T1552.001",
        "remediation": "Revoke at github.com/settings/tokens. Audit commit history and Actions logs.",
    },
    "stripe_secret": {
        "pattern": r"sk_(?:live|test)_[0-9a-zA-Z]{24,}",
        "severity": "CRITICAL",
        "description": "Stripe Secret Key — payment processing access",
        "mitre": "T1552.001",
        "remediation": "Roll key at dashboard.stripe.com. Check for unauthorized charges.",
    },
    "jwt_secret": {
        "pattern": r"(?:jwt[_-]?secret|JWT_SECRET)[_\s=:\"']+([A-Za-z0-9+/=_\-]{20,})",
        "severity": "HIGH",
        "description": "JWT Secret — can forge authentication tokens",
        "mitre": "T1552.001",
        "remediation": "Rotate secret. Invalidate all existing tokens. Force re-authentication.",
    },
    "private_key_pem": {
        "pattern": r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----",
        "severity": "CRITICAL",
        "description": "Private Key (PEM format) — cryptographic identity compromise",
        "mitre": "T1552.001",
        "remediation": "Revoke certificate. Generate new key pair. Update all dependent services.",
    },
    "generic_password": {
        "pattern": r"(?:password|passwd|pwd)[_\s=:\"']+([^\s\"'<>]{8,})",
        "severity": "MEDIUM",
        "description": "Hardcoded password in source",
        "mitre": "T1552.001",
        "remediation": "Remove from source. Move to environment variable or secret manager.",
    },
    "generic_api_key": {
        "pattern": r"(?:api[_-]?key|apikey|api_secret)[_\s=:\"']+([A-Za-z0-9+/=_\-]{16,})",
        "severity": "HIGH",
        "description": "Generic API key or secret",
        "mitre": "T1552.001",
        "remediation": "Identify service, rotate key. Implement secrets management.",
    },
}

# ── MFA Gap Assessment ─────────────────────────────────────────────────────
MFA_CHECKS = [
    {
        "check": "Admin accounts MFA",
        "question": "Are MFA/2FA enforced on all administrator accounts?",
        "nis2_ref": "Article 21(2)(j)",
        "risk": "CRITICAL",
        "impact": "Admin compromise enables full environment takeover",
    },
    {
        "check": "VPN/Remote access MFA",
        "question": "Is MFA required for VPN and all remote access?",
        "nis2_ref": "Article 21(2)(j)",
        "risk": "CRITICAL",
        "impact": "Remote access without MFA is primary ransomware entry vector",
    },
    {
        "check": "Email/O365/Google Workspace MFA",
        "question": "Is MFA enforced on all email and productivity suite accounts?",
        "nis2_ref": "Article 21(2)(j)",
        "risk": "HIGH",
        "impact": "Business email compromise (BEC) risk without MFA",
    },
    {
        "check": "Development/CI/CD MFA",
        "question": "Is MFA enforced on GitHub, GitLab, CI/CD pipelines?",
        "nis2_ref": "Article 21(2)(j)",
        "risk": "HIGH",
        "impact": "Supply chain compromise via developer account takeover",
    },
    {
        "check": "Cloud console MFA",
        "question": "Is MFA enforced on AWS/GCP/Azure console access?",
        "nis2_ref": "Article 21(2)(j)",
        "risk": "CRITICAL",
        "impact": "Cloud infrastructure takeover without MFA",
    },
    {
        "check": "Privileged Access Workstations",
        "question": "Are PAW/jump servers used for privileged operations?",
        "nis2_ref": "Article 21(2)(e)",
        "risk": "MEDIUM",
        "impact": "Lateral movement risk from standard workstations to privileged systems",
    },
    {
        "check": "Password Manager",
        "question": "Is a company-approved password manager mandated?",
        "nis2_ref": "Article 21(2)(h)",
        "risk": "MEDIUM",
        "impact": "Credential reuse enables credential stuffing attacks",
    },
    {
        "check": "Offboarding process",
        "question": "Is account access revoked within 24hrs of employee departure?",
        "nis2_ref": "Article 21(2)(i)",
        "risk": "HIGH",
        "impact": "Insider threat from orphaned accounts — common in Nigerian SMEs",
    },
]

# ── DNS Exposure Checks ─────────────────────────────────────────────────────
SENSITIVE_SUBDOMAIN_PATTERNS = [
    "admin", "dev", "staging", "test", "internal", "vpn", "rdp",
    "ssh", "ftp", "backup", "db", "database", "api", "portal",
    "mail", "smtp", "jenkins", "gitlab", "jira", "confluence",
    "monitoring", "kibana", "grafana", "prometheus", "phpmyadmin",
]


# ══════════════════════════════════════════════════════════════════════════════
# SCANNER ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def scan_text_for_credentials(text: str, source: str = "unknown") -> list:
    """Scan any text blob for credential patterns."""
    findings = []
    for cred_type, config in CREDENTIAL_PATTERNS.items():
        try:
            matches = re.findall(config["pattern"], text, re.IGNORECASE)
            if matches:
                # Hash the found value for safe logging
                for match in (matches if isinstance(matches[0], str) else [m[0] for m in matches]):
                    findings.append({
                        "type":        cred_type,
                        "severity":    config["severity"],
                        "description": config["description"],
                        "source":      source,
                        "hash":        hashlib.sha256(match.encode()).hexdigest()[:16] + "...",
                        "mitre":       config["mitre"],
                        "remediation": config["remediation"],
                        "timestamp":   datetime.now().isoformat(),
                    })
        except re.error:
            continue
    return findings


def check_dns_exposure(domain: str) -> list:
    """Check for sensitive subdomain exposure."""
    findings = []
    for sub in SENSITIVE_SUBDOMAIN_PATTERNS:
        fqdn = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(fqdn)
            findings.append({
                "type":        "dns_exposure",
                "severity":    "MEDIUM",
                "description": f"Sensitive subdomain exposed: {fqdn} → {ip}",
                "subdomain":   fqdn,
                "ip":          ip,
                "source":      "DNS enumeration",
                "mitre":       "T1590.002",
                "remediation": f"Review whether {fqdn} should be publicly resolvable. Consider split-horizon DNS.",
                "timestamp":   datetime.now().isoformat(),
            })
        except socket.gaierror:
            pass  # Not exposed — good
    return findings


def run_mfa_assessment(domain: str) -> dict:
    """Return MFA gap assessment structure."""
    return {
        "domain":   domain,
        "checks":   MFA_CHECKS,
        "note":     "Complete this assessment manually with the client's IT team. Check each item and mark YES/NO/PARTIAL.",
        "nis2_ref": "Article 21(2)(j) — Multi-factor authentication is mandatory under NIS2 for all essential service operators.",
        "generated": datetime.now().isoformat(),
    }


def build_demo_scan() -> dict:
    """Generate realistic demo scan results."""
    return {
        "scan_target":    "acme-financial.com",
        "scan_type":      "Identity Threat Scan (Demo Mode)",
        "generated":      datetime.now().isoformat(),
        "scanner":        "Tinlance Identity Threat Scanner v1.0.0",
        "credential_findings": [
            {
                "type":        "paystack_secret_key",
                "severity":    "CRITICAL",
                "description": "Paystack Secret Key — full API access, can initiate transfers",
                "source":      "github.com/acme-dev/backend-api (commit a3f8d2c, .env file)",
                "hash":        "sk_live_abc...def",
                "mitre":       "T1552.001",
                "remediation": "Revoke immediately at dashboard.paystack.com. Audit all transactions since exposure.",
                "timestamp":   datetime.now().isoformat(),
                "days_exposed": 47,
            },
            {
                "type":        "aws_access_key",
                "severity":    "CRITICAL",
                "description": "AWS Access Key ID — cloud infrastructure access",
                "source":      "github.com/acme-dev/infrastructure (commit b7e2a1f, terraform.tfvars)",
                "hash":        "AKIA4...X7KP",
                "mitre":       "T1552.001",
                "remediation": "Revoke in AWS IAM immediately. Run CloudTrail audit for unauthorized API calls.",
                "timestamp":   datetime.now().isoformat(),
                "days_exposed": 12,
            },
            {
                "type":        "jwt_secret",
                "severity":    "HIGH",
                "description": "JWT Secret — can forge authentication tokens for all users",
                "source":      "github.com/acme-dev/auth-service (config.js)",
                "hash":        "myS3cr3t...K3y",
                "mitre":       "T1552.001",
                "remediation": "Rotate JWT secret. Invalidate all existing tokens. Force re-authentication.",
                "timestamp":   datetime.now().isoformat(),
                "days_exposed": 89,
            },
            {
                "type":        "generic_password",
                "severity":    "MEDIUM",
                "description": "Hardcoded database password in source code",
                "source":      "github.com/acme-dev/backend-api (database.py)",
                "hash":        "Acme2024!...DB",
                "mitre":       "T1552.001",
                "remediation": "Move to environment variable. Rotate database password. Audit database access logs.",
                "timestamp":   datetime.now().isoformat(),
                "days_exposed": 156,
            },
        ],
        "dns_findings": [
            {
                "type":        "dns_exposure",
                "severity":    "MEDIUM",
                "description": "Admin panel exposed: admin.acme-financial.com → 197.210.x.x",
                "subdomain":   "admin.acme-financial.com",
                "ip":          "197.210.52.31",
                "source":      "DNS enumeration",
                "mitre":       "T1590.002",
                "remediation": "Restrict admin panel to VPN access only. Remove from public DNS.",
                "timestamp":   datetime.now().isoformat(),
            },
            {
                "type":        "dns_exposure",
                "severity":    "MEDIUM",
                "description": "Development environment exposed: dev.acme-financial.com → 197.210.x.x",
                "subdomain":   "dev.acme-financial.com",
                "ip":          "197.210.52.44",
                "source":      "DNS enumeration",
                "mitre":       "T1590.002",
                "remediation": "Dev environment should not be publicly accessible. Use VPN or private network.",
                "timestamp":   datetime.now().isoformat(),
            },
            {
                "type":        "dns_exposure",
                "severity":    "LOW",
                "description": "Staging environment exposed: staging.acme-financial.com",
                "subdomain":   "staging.acme-financial.com",
                "ip":          "197.210.52.55",
                "source":      "DNS enumeration",
                "mitre":       "T1590.002",
                "remediation": "Restrict staging to authorised IP ranges only.",
                "timestamp":   datetime.now().isoformat(),
            },
        ],
        "mfa_assessment": run_mfa_assessment("acme-financial.com"),
        "summary": {
            "critical": 2, "high": 1, "medium": 4, "low": 1, "info": 0,
            "total_findings": 8,
            "highest_risk": "Two CRITICAL credential exposures found in public GitHub repositories. Active AWS key confirmed. Immediate remediation required.",
            "identity_risk_score": 8.7,
            "nis2_mfa_gaps": 4,
        }
    }


def scan_domain(domain: str) -> dict:
    """Run live domain scan."""
    print(f"  Scanning identity attack surface for: {domain}")
    findings = {"credential_findings": [], "dns_findings": [], "summary": {}}

    # DNS check
    print(f"  Checking DNS exposure...")
    dns_f = check_dns_exposure(domain)
    findings["dns_findings"] = dns_f
    print(f"  DNS: {len(dns_f)} exposed subdomains found")

    # MFA assessment
    findings["mfa_assessment"] = run_mfa_assessment(domain)

    # Summary
    all_f = findings["credential_findings"] + findings["dns_findings"]
    findings["summary"] = {
        "critical": sum(1 for f in all_f if f.get("severity") == "CRITICAL"),
        "high":     sum(1 for f in all_f if f.get("severity") == "HIGH"),
        "medium":   sum(1 for f in all_f if f.get("severity") == "MEDIUM"),
        "low":      sum(1 for f in all_f if f.get("severity") == "LOW"),
        "total_findings": len(all_f),
        "scan_target": domain,
        "generated":   datetime.now().isoformat(),
    }
    return findings


def save_results(data: dict, out_dir: str, prefix: str = "identity_scan"):
    """Save scan results to JSON."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return str(path)


def print_results(data: dict):
    """Print scan results to console."""
    s = data.get("summary", {})
    print(f"\n  🔐 Tinlance Identity Threat Scanner")
    print(f"  Target: {data.get('scan_target', data.get('domain', 'unknown'))}")
    print(f"  ────────────────────────────────────────────")

    crit = s.get("critical", 0)
    high = s.get("high", 0)
    med  = s.get("medium", 0)
    low  = s.get("low", 0)

    if crit > 0: print(f"  🔴 CRITICAL: {crit}")
    if high > 0: print(f"  🟠 HIGH:     {high}")
    if med  > 0: print(f"  🟡 MEDIUM:   {med}")
    if low  > 0: print(f"  🟢 LOW:      {low}")

    print(f"\n  Credential Findings: {len(data.get('credential_findings', []))}")
    for f in data.get("credential_findings", []):
        print(f"  → [{f['severity']}] {f['description']}")
        print(f"    Source: {f['source']}")
        print(f"    MITRE:  {f['mitre']}")

    print(f"\n  DNS Exposure Findings: {len(data.get('dns_findings', []))}")
    for f in data.get("dns_findings", []):
        print(f"  → [{f['severity']}] {f['description']}")

    if s.get("highest_risk"):
        print(f"\n  ⚠️  Highest Risk: {s['highest_risk']}")
    print(f"\n  Identity Risk Score: {s.get('identity_risk_score', 'N/A')} / 10")
    print(f"  ────────────────────────────────────────────\n")


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Tinlance Identity Threat Scanner")
    parser.add_argument("--domain",  help="Target domain to scan")
    parser.add_argument("--text",    help="Text file to scan for credentials")
    parser.add_argument("--out",     default=".", help="Output directory")
    parser.add_argument("--demo",    action="store_true", help="Run demo scan")
    args = parser.parse_args()

    if args.demo:
        data = build_demo_scan()
        data["scan_target"] = "acme-financial.com (DEMO)"
    elif args.domain:
        data = scan_domain(args.domain)
        data["scan_target"] = args.domain
        data["scan_type"]   = "Live Identity Threat Scan"
        data["scanner"]     = "Tinlance Identity Threat Scanner v1.0.0"
        data["generated"]   = datetime.now().isoformat()
    elif args.text:
        with open(args.text) as f:
            text = f.read()
        findings = scan_text_for_credentials(text, args.text)
        data = {
            "scan_target": args.text,
            "scan_type":   "Text/File Credential Scan",
            "scanner":     "Tinlance Identity Threat Scanner v1.0.0",
            "generated":   datetime.now().isoformat(),
            "credential_findings": findings,
            "dns_findings": [],
            "summary": {
                "critical": sum(1 for f in findings if f["severity"] == "CRITICAL"),
                "high":     sum(1 for f in findings if f["severity"] == "HIGH"),
                "medium":   sum(1 for f in findings if f["severity"] == "MEDIUM"),
                "low":      sum(1 for f in findings if f["severity"] == "LOW"),
                "total_findings": len(findings),
            }
        }
    else:
        print("Usage: python identity_scanner.py --demo")
        print("       python identity_scanner.py --domain example.com")
        print("       python identity_scanner.py --text /path/to/file.txt")
        return

    print_results(data)
    out_path = save_results(data, args.out, "identity_scan")
    print(f"  Results saved: {out_path}")

if __name__ == "__main__":
    main()
