"""Deterministic finding correlation and FDSE prioritization scoring."""
 
from __future__ import annotations
 
import hashlib
import re
from collections import defaultdict
from typing import Any
 
from .contracts import validate_document
 
_SEVERITY = {"INFO": 5, "LOW": 20, "MEDIUM": 40, "HIGH": 70, "CRITICAL": 90}
_CRITICALITY = {"UNKNOWN": 0.5, "LOW": 0.75, "MEDIUM": 1.0, "HIGH": 1.25, "CRITICAL": 1.5}
_STATUS_RANK = {"OPEN": 5, "RETEST_REQUIRED": 4, "MITIGATED": 3, "ACCEPTED": 2, "CLOSED": 1, "UNKNOWN": 0}
 
 
def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
 
 
def correlation_key(finding: dict[str, Any]) -> str:
    title = _normalize(str(finding.get("title", "")))
    assets = ",".join(sorted(str(x) for x in finding.get("asset_ids", [])))
    return hashlib.sha256(f"{title}\0{assets}".encode("utf-8")).hexdigest()
 
 
def prioritization_score(finding: dict[str, Any], asset_criticalities: dict[str, str] | None = None) -> float:
    severity = _SEVERITY.get(str(finding.get("severity", "INFO")).upper(), 5)
    confidence = max(0.0, min(1.0, float(finding.get("confidence", 0.0))))
    criticalities = asset_criticalities or {}
    factors = [_CRITICALITY.get(criticalities.get(asset, "UNKNOWN"), 0.5) for asset in finding.get("asset_ids", [])]
    asset_factor = max(factors, default=0.5)
    return round(min(100.0, severity * confidence * asset_factor), 2)
 
 
def correlate_findings(
    findings: list[dict[str, Any]],
    *,
    asset_criticalities: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for finding in findings:
        validate_document("finding", finding)
        groups[correlation_key(finding)].append(finding)
 
    output: list[dict[str, Any]] = []
    for key, group in sorted(groups.items()):
        first = dict(group[0])
        evidence = sorted({eid for item in group for eid in item.get("evidence_ids", [])})
        assets = sorted({aid for item in group for aid in item.get("asset_ids", [])})
        sources = sorted({str(item.get("source")) for item in group if item.get("source")})
        severities = sorted(group, key=lambda item: _SEVERITY.get(item.get("severity", "INFO"), 5), reverse=True)
        statuses = sorted(group, key=lambda item: _STATUS_RANK.get(item.get("status", "UNKNOWN"), 0), reverse=True)
        first["finding_id"] = "FND-" + key[:20].upper()
        first["correlation_key"] = key
        first["evidence_ids"] = evidence
        first["asset_ids"] = assets
        first["correlated_sources"] = sources
        first["severity"] = severities[0].get("severity", "INFO")
        first["status"] = statuses[0].get("status", "UNKNOWN")
        first["confidence"] = round(max(float(item.get("confidence", 0.0)) for item in group), 4)
        first["risk_score"] = prioritization_score(first, asset_criticalities)
        validate_document("finding", first)
        output.append(first)
    return output
