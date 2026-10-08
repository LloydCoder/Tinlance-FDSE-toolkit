#!/usr/bin/env python3
"""Fail-closed FDSE Toolkit verification against the canonical TSIC delivery-evidence adapter."""

from __future__ import annotations

import base64
import json
from urllib.request import Request, urlopen

TSIC_REVISION = "9bb4f6dd3d70f6fe1487c2dd14644026b6f4ee3f"
REQUIRED = {
    "identity-context",
    "event-envelope",
    "delivery-semantics",
    "trace-context",
    "economic-attribution",
}


def fetch_json(path: str) -> dict:
    url = f"https://api.github.com/repos/LloydCoder/tinlance-system-integration/contents/{path}?ref={TSIC_REVISION}"
    request = Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "tinlance-fdse-toolkit-tsic"},
    )
    with urlopen(request, timeout=20) as response:
        if response.status != 200:
            raise RuntimeError(f"TSIC contents API returned HTTP {response.status}: {url}")
        payload = json.load(response)
    return json.loads(base64.b64decode(payload["content"].replace("\n", "")).decode("utf-8"))


def main() -> None:
    manifest = fetch_json("manifests/ecosystem.json")
    adapter = fetch_json("integrations/fdse-toolkit/adapter.json")
    registry = fetch_json("catalog/contracts/registry.json")

    system = next(item for item in manifest["systems"] if item["id"] == "fdse-toolkit")
    assert system["repository"] == "LloydCoder/Tinlance-FDSE-toolkit"
    assert system["governance_role"] == "delivery_reporting_authority"

    assert adapter["source_system"] == "tsic"
    assert adapter["target_system"] == "fdse-toolkit"
    assert adapter["status"] == "reference-contract"
    assert {item["tsic_contract"] for item in adapter["contract_bindings"]} == REQUIRED
    assert {item["id"] for item in registry["contracts"]} >= REQUIRED

    assert adapter["authority"]["integration_contracts"] == "tsic"
    assert adapter["authority"]["delivery_reporting"] == "fdse-toolkit"
    assert adapter["authority"]["execution_authority"] == "agent-platform"

    required_invariants = {
        "reports_are_derived_from_provenance_preserving_evidence",
        "engineering_and_transformation_routes_remain_distinct",
        "economic_attribution_retains_delivery_route",
        "toolkit_does_not_grant_execution_authority",
        "toolkit_does_not_become_detection_or_policy_authority",
        "tsic_remains_integration_authority",
        "agent-platform-remains-execution-authority",
    }
    assert set(adapter["invariants"]) == required_invariants

    print(f"PASS TSIC-29 FDSE Toolkit conformance: revision={TSIC_REVISION}")


if __name__ == "__main__":
    main()
