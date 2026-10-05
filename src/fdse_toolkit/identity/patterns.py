"""Curated deterministic secret patterns.

Provider formats change. These patterns are detection hints, not proof of validity.
Validity checks are intentionally disabled in the base scanner to avoid outbound
calls with customer-derived credentials.
"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SecretPattern:
    name: str
    regex: re.Pattern[str]
    severity: str
    base_confidence: float
    description: str


def _p(name: str, pattern: str, severity: str, confidence: float, description: str) -> SecretPattern:
    return SecretPattern(name, re.compile(pattern, re.IGNORECASE), severity, confidence, description)


PATTERNS = (
    _p("aws_access_key_id", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b", "CRITICAL", .97, "AWS access key identifier"),
    _p("aws_secret_access_key", r"(?i)(?:aws[_-]?secret(?:[_-]?access)?[_-]?key|secret[_-]?access[_-]?key)\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{40})", "CRITICAL", .92, "AWS secret access key assignment"),
    _p("github_personal_access_token", r"\bgh[pousr]_[A-Za-z0-9]{20,255}\b", "CRITICAL", .98, "GitHub token"),
    _p("stripe_secret_key", r"\bsk_(?:live|test)_[A-Za-z0-9]{16,}\b", "CRITICAL", .96, "Stripe secret API key"),
    _p("paystack_secret_key", r"(?i)\bpaystack(?:_secret)?(?:_key)?\b\s*[:=]\s*['\"](sk_(?:live|test)_[A-Za-z0-9]{10,})['\"]", "CRITICAL", .96, "Paystack secret API key in explicit provider context"),
    _p("flutterwave_secret_key", r"\bFLWSECK[-_][A-Za-z0-9_-]{10,}\b", "CRITICAL", .93, "Flutterwave secret key"),
    _p("twilio_account_sid", r"\bAC[a-f0-9]{32}\b", "HIGH", .90, "Twilio account SID"),
    _p("sendgrid_api_key", r"\bSG\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}\b", "CRITICAL", .96, "SendGrid API key"),
    _p("google_api_key", r"\bAIza[0-9A-Za-z_-]{35}\b", "HIGH", .94, "Google API key"),
    _p("jwt", r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b", "HIGH", .90, "JWT bearer token"),
    _p("private_key", r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----", "CRITICAL", .99, "Private cryptographic key header"),
    _p("bearer_token", r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{20,}\b", "HIGH", .72, "HTTP bearer credential"),
    _p("basic_auth", r"(?i)\bBasic\s+[A-Za-z0-9+/]{20,}={0,2}\b", "HIGH", .72, "HTTP Basic authentication credential"),
    _p("postgres_connection_string", r"(?i)postgres(?:ql)?://[^\s:@]+:[^\s@]+@[^\s/]+(?:/[^\s]*)?", "CRITICAL", .95, "PostgreSQL credential-bearing connection string"),
    _p("mysql_connection_string", r"(?i)mysql://[^\s:@]+:[^\s@]+@[^\s/]+(?:/[^\s]*)?", "CRITICAL", .95, "MySQL credential-bearing connection string"),
    _p("generic_api_key", r"(?i)\b(?:api[_-]?key|apikey)\s*[:=]\s*['\"]([A-Za-z0-9._~+/=-]{20,})['\"]", "HIGH", .62, "Generic API key assignment"),
    _p("generic_password", r"(?i)\b(?:password|passwd|pwd)\s*[:=]\s*['\"]([^'\"\r\n]{8,})['\"]", "HIGH", .58, "Generic password assignment"),
    _p("generic_secret_assignment", r"(?i)\b(?:secret|client_secret|token)\s*[:=]\s*['\"]([^'\"\r\n]{12,})['\"]", "HIGH", .58, "Generic secret/token assignment"),
)
