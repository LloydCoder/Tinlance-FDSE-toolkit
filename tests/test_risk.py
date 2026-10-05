from fdse_toolkit.risk import correlate_findings, prioritization_score


def finding(fid, title, evidence, source, severity="HIGH", confidence=0.8, assets=None):
    return {
        "schema_version": "1.0.0", "finding_id": fid, "title": title,
        "description": "synthetic", "severity": severity, "status": "OPEN",
        "confidence": confidence, "evidence_ids": evidence, "asset_ids": assets or [],
        "source": source,
    }


def test_correlator_merges_same_title_and_asset_across_sources():
    out = correlate_findings([
        finding("FND-A", "Exposed credential", ["EVD-A"], "ReconOS", assets=["AST-1"]),
        finding("FND-B", "Exposed credential", ["EVD-B"], "IdentityScanner", severity="CRITICAL", confidence=0.95, assets=["AST-1"]),
    ], asset_criticalities={"AST-1": "CRITICAL"})
    assert len(out) == 1
    assert out[0]["evidence_ids"] == ["EVD-A", "EVD-B"]
    assert out[0]["correlated_sources"] == ["IdentityScanner", "ReconOS"]
    assert out[0]["severity"] == "CRITICAL"
    assert out[0]["risk_score"] == 100.0


def test_prioritization_score_is_bounded_and_deterministic():
    item = finding("FND-X", "Risk", ["EVD-X"], "test", severity="MEDIUM", confidence=0.5, assets=["AST-X"])
    assert prioritization_score(item, {"AST-X": "HIGH"}) == 25.0
