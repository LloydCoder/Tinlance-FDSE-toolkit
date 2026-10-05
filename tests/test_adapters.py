from fdse_toolkit.adapters import AdapterContext, normalize_findings, normalize_sarif


def test_generic_adapter_normalizes_to_canonical_finding():
    findings = normalize_findings(
        {"findings": [{"title": "Credential exposure", "severity": "critical", "confidence": 0.91}]},
        AdapterContext("EVD-ABC", "ThreatFade", "1.0"),
    )
    assert findings[0]["evidence_ids"] == ["EVD-ABC"]
    assert findings[0]["severity"] == "CRITICAL"
    assert findings[0]["confidence"] == 0.91


def test_sarif_adapter_keeps_raw_evidence_reference():
    findings = normalize_sarif(
        {"version": "2.1.0", "runs": [{"tool": {"driver": {"name": "Semgrep"}}, "results": [{"ruleId": "SEC001", "level": "error", "message": {"text": "unsafe sink"}}]}]},
        AdapterContext("EVD-SARIF", "import", "2.1.0"),
    )
    assert len(findings) == 1
    assert findings[0]["source"] == "Semgrep"
    assert findings[0]["evidence_ids"] == ["EVD-SARIF"]
