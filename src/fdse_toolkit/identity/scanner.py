"""Safe, offline-first identity/secret exposure scanner."""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any

from .patterns import PATTERNS, SecretPattern

_MAX_FILE_BYTES = 10 * 1024 * 1024


def _entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = {char: value.count(char) for char in set(value)}
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def _confidence(pattern: SecretPattern, value: str) -> float:
    score = pattern.base_confidence
    if len(value) >= 20 and _entropy(value) >= 3.0:
        score += 0.03
    return round(min(score, 0.99), 2)


class IdentityScanner:
    """Deterministic secret detector. It never stores matched secret values."""

    def __init__(self, *, max_file_bytes: int = _MAX_FILE_BYTES):
        if max_file_bytes <= 0:
            raise ValueError("max_file_bytes must be positive")
        self.max_file_bytes = max_file_bytes

    def scan_text(self, text: str, *, source: str = "text") -> list[dict[str, Any]]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        findings: list[dict[str, Any]] = []
        for pattern in PATTERNS:
            for match in pattern.regex.finditer(text):
                value = match.group(1) if match.lastindex else match.group(0)
                line = text.count("\n", 0, match.start()) + 1
                line_start = text.rfind("\n", 0, match.start()) + 1
                column = match.start() - line_start + 1
                findings.append({
                    "type": pattern.name,
                    "severity": pattern.severity,
                    "confidence": _confidence(pattern, value),
                    "description": pattern.description,
                    "source": source,
                    "location": {"line": line, "column": column},
                    "match_sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
                    "redaction": "[REDACTED]",
                    "match_length": len(value),
                    "remediation": "Revoke/rotate the credential, audit use, remove it from source history, and move secrets to an approved secret-management mechanism.",
                })
        return self._deduplicate(findings)

    def scan_file(self, path: Path, *, source: str | None = None) -> list[dict[str, Any]]:
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(path)
        size = path.stat().st_size
        if size > self.max_file_bytes:
            raise ValueError(f"input exceeds max_file_bytes ({self.max_file_bytes})")
        text = path.read_text(encoding="utf-8", errors="replace")
        return self.scan_text(text, source=source or path.name)

    @staticmethod
    def _deduplicate(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[tuple[str, str, str]] = set()
        output = []
        for finding in findings:
            key = (finding["type"], finding["match_sha256"], finding["source"])
            if key not in seen:
                seen.add(key)
                output.append(finding)
        return output
