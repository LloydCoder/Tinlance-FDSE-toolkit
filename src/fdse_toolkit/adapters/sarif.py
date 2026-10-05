"""Minimal SARIF 2.x result adapter; raw SARIF remains the evidence artifact."""
from __future__ import annotations

from typing import Any

from .base import AdapterContext, AdapterError, _severity
from .generic_json import normalize_findings


def normalize_sarif(payload: dict[str, Any], context: AdapterContext) -> list[dict[str, Any]]:
    runs = payload.get("runs")
    if not isinstance(runs, list):
        raise AdapterError("SARIF payload requires runs")
    findings = []
    for run in runs:
        if not isinstance(run, dict):
            continue
        tool = run.get("tool", {})
        driver = tool.get("driver", {}) if isinstance(tool, dict) else {}
        source = str(driver.get("name") or context.source)
        for result in run.get("results", []) or []:
            if not isinstance(result, dict):
                continue
            rule_id = result.get("ruleId")
            message = result.get("message", {})
            text = message.get("text") if isinstance(message, dict) else str(message)
            item = {
                "title": f"{rule_id}: {text}" if rule_id else str(text),
                "description": str(text),
                "level": result.get("level", "note"),
                "evidence_ids": [context.evidence_id],
            }
            locations = result.get("locations") or []
            if locations:
                uri = (((locations[0] or {}).get("physicalLocation") or {}).get("artifactLocation") or {}).get("uri")
                if uri:
                    item["description"] += f" Location: {uri}"
            findings.extend(normalize_findings({"findings": [item]}, AdapterContext(context.evidence_id, source, context.source_version)))
    return findings
