"""Generic JSON finding adapter with strict evidence references."""
from __future__ import annotations

import hashlib
from typing import Any

from ..contracts import validate_document
from .base import AdapterContext, AdapterError, _confidence, _severity


def normalize_findings(payload: dict[str, Any], context: AdapterContext) -> list[dict[str, Any]]:
    raw = payload.get("findings")
    if not isinstance(raw, list):
        raise AdapterError("generic JSON adapter requires a findings array")
    results: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            raise AdapterError("finding entries must be objects")
        title = str(item.get("title") or item.get("name") or "Untitled finding").strip()
        if not title:
            raise AdapterError("finding title cannot be empty")
        evidence_ids = item.get("evidence_ids") or [context.evidence_id]
        if not isinstance(evidence_ids, list) or not evidence_ids:
            raise AdapterError("finding must reference evidence")
        fingerprint = hashlib.sha256((context.source + "\0" + title + "\0" + json_safe(item)).encode()).hexdigest()[:20].upper()
        finding = {
            "schema_version": "1.0.0",
            "finding_id": "FND-" + fingerprint,
            "title": title,
            "description": str(item.get("description") or item.get("message") or ""),
            "severity": _severity(item.get("severity") or item.get("level")),
            "status": str(item.get("status") or "OPEN").upper(),
            "confidence": _confidence(item.get("confidence")),
            "evidence_ids": evidence_ids,
            "asset_ids": item.get("asset_ids") or [],
            "source": context.source,
            "mitre_techniques": [x for x in (item.get("mitre_techniques") or []) if isinstance(x, str)],
        }
        if "cvss" in item and isinstance(item["cvss"], (int, float)):
            finding["cvss"] = float(item["cvss"])
        if context.source_version:
            finding["notes"] = f"source_version={context.source_version}"
        validate_document("finding", finding)
        results.append(finding)
    return results


def json_safe(value: Any) -> str:
    import json
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
