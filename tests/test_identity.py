import json
from pathlib import Path

import pytest

from fdse_toolkit.identity import IdentityScanner


def test_scanner_detects_and_redacts_synthetic_provider_secret():
    secret = "sk_" + "live_" + "SYNTHETICNOTREAL1234567890"
    text = f'paystack_secret_key = "{secret}"\n'
    findings = IdentityScanner().scan_text(text, source="fixture.py")
    assert findings
    assert any(item["type"] == "paystack_secret_key" for item in findings)
    serialized = json.dumps(findings)
    assert secret not in serialized
    assert all(item["redaction"] == "[REDACTED]" for item in findings)
    assert all(len(item["match_sha256"]) == 64 for item in findings)


def test_scanner_does_not_label_generic_stripe_like_key_as_paystack():
    secret = "sk_" + "live_" + "SYNTHETIC_123456789012345678"
    findings = IdentityScanner().scan_text(f'key = "{secret}"', source="fixture.py")
    assert not any(item["type"] == "paystack_secret_key" for item in findings)


def test_scanner_rejects_oversized_files(tmp_path: Path):
    path = tmp_path / "large.txt"
    path.write_bytes(b"x" * 1025)
    with pytest.raises(ValueError):
        IdentityScanner(max_file_bytes=1024).scan_file(path)
