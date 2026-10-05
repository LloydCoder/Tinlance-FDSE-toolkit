from fdse_toolkit.supply_chain import generate_sbom


def test_sbom_is_cyclonedx_and_contains_project():
    bom = generate_sbom()
    assert bom["bomFormat"] == "CycloneDX"
    assert bom["specVersion"] == "1.5"
    assert any(c["name"].lower() == "jsonschema" for c in bom["components"])
    assert bom["metadata"]["component"]["name"] == "tinlance-fdse-toolkit"
