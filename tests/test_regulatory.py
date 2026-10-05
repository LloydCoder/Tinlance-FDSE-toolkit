import pytest

from fdse_toolkit.regulatory import build_assessment, official_reference


def test_nis2_reference_is_official_and_source_backed():
    ref = official_reference("NIS2")
    assert ref["url"].startswith("https://eur-lex.europa.eu/")
    assessment = build_assessment(
        assessment_id="REG-NIS2-001",
        regime="NIS2",
        jurisdiction="EU",
        statement_type="LEGAL_REQUIREMENT",
        applicability_status="REQUIRES_LEGAL_REVIEW",
    )
    assert assessment["source_url"] == ref["url"]
    assert "deadline" not in assessment


def test_unknown_regime_fails_closed():
    with pytest.raises(ValueError):
        official_reference("UNKNOWN-REGIME")
