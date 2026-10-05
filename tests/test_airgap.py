from pathlib import Path

import pytest

from fdse_toolkit.airgap import build_airgap_bundle, verify_airgap_bundle


def test_airgap_bundle_is_offline_and_verifiable(tmp_path: Path):
    src = tmp_path / "bundle"
    src.mkdir()
    (src / "README.txt").write_text("offline fixture", encoding="utf-8")
    out = tmp_path / "airgap.zip"
    manifest = build_airgap_bundle(src, out)
    assert manifest["offline_only"] is True
    verified = verify_airgap_bundle(out)
    assert verified["artifacts"][0]["path"] == "README.txt"


def test_airgap_bundle_rejects_empty_source(tmp_path: Path):
    with pytest.raises(ValueError):
        build_airgap_bundle(tmp_path, tmp_path / "empty.zip")
