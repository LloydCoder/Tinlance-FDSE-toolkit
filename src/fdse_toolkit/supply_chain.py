"""CycloneDX-style SBOM generation from the active Python environment."""
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from importlib.metadata import distributions


def _purl(name: str, version: str) -> str:
    normalized = name.lower().replace("_", "-")
    return f"pkg:pypi/{normalized}@{version}"


def generate_sbom(*, project_name: str = "tinlance-fdse-toolkit", project_version: str = "0.1.0.dev0") -> dict:
    components = []
    for dist in sorted(distributions(), key=lambda d: (d.metadata.get("Name") or "").lower()):
        name = dist.metadata.get("Name")
        version = dist.version
        if not name or not version:
            continue
        components.append({
            "type": "library",
            "name": name,
            "version": version,
            "purl": _purl(name, version),
        })
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "component": {
                "type": "application",
                "name": project_name,
                "version": project_version,
                "purl": _purl(project_name, project_version),
            },
            "tools": [{"vendor": "Python", "name": "importlib.metadata", "version": ".".join(map(str, sys.version_info[:3]))}],
        },
        "components": components,
    }


def write_sbom(output_path, *, project_name: str = "tinlance-fdse-toolkit", project_version: str = "0.1.0.dev0"):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(generate_sbom(project_name=project_name, project_version=project_version), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path
