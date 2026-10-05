"""Source-backed regulatory assessment helpers; not legal advice."""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from .contracts import validate_document

OFFICIAL_REFERENCES = {
    "NIS2": {
        "title": "Directive (EU) 2022/2555 on measures for a high common level of cybersecurity across the Union",
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022L2555",
        "effective_date": "2024-10-18",
        "topic": "Article 23 incident reporting and related cybersecurity risk-management obligations",
    },
    "DORA": {
        "title": "Regulation (EU) 2022/2554 on digital operational resilience for the financial sector",
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554",
        "effective_date": "2025-01-17",
        "topic": "ICT-related incident management and reporting",
    },
}


@dataclass(frozen=True)
class RegulatoryAssessment:
    assessment_id: str
    regime: str
    jurisdiction: str
    statement_type: str
    source_url: str
    source_title: str
    effective_date: str
    applicability_status: str
    requirement_topic: str
    deadline: str | None = None
    competent_authority: str | None = None
    notes: str | None = None

    def as_dict(self) -> dict:
        value = {"schema_version": "1.0.0", **{k: v for k, v in self.__dict__.items() if v is not None}}
        validate_document("regulatory-assessment", value)
        return value


def official_reference(regime: str) -> dict:
    try:
        return dict(OFFICIAL_REFERENCES[regime.upper()])
    except KeyError as exc:
        raise ValueError(f"no maintained official reference for regime: {regime}") from exc


def build_assessment(
    *,
    assessment_id: str,
    regime: str,
    jurisdiction: str,
    statement_type: str,
    applicability_status: str,
    deadline: str | None = None,
    competent_authority: str | None = None,
    notes: str | None = None,
) -> dict:
    ref = official_reference(regime)
    parsed = urlparse(ref["url"])
    if parsed.scheme != "https" or parsed.netloc != "eur-lex.europa.eu":
        raise ValueError("regulatory source must be the maintained EU official source")
    assessment = RegulatoryAssessment(
        assessment_id=assessment_id,
        regime=regime.upper(),
        jurisdiction=jurisdiction,
        statement_type=statement_type,
        source_url=ref["url"],
        source_title=ref["title"],
        effective_date=ref["effective_date"],
        applicability_status=applicability_status,
        requirement_topic=ref["topic"],
        deadline=deadline,
        competent_authority=competent_authority,
        notes=notes,
    )
    return assessment.as_dict()
