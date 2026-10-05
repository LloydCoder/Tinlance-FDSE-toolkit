from pathlib import Path
import json
import zipfile

import pytest

from fdse_toolkit.airgap import verify_airgap_bundle


def test_airgap_rejects_duplicate_archive_names(tmp_path: Path):
    bundle = tmp_path / "dup.zip"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("AIRGAP-MANIFEST.json", json.dumps({"artifacts": []}))
        archive.writestr("same.txt", "a")
        archive.writestr("same.txt", "b")
    with pytest.raises(ValueError, match="duplicate archive names"):
        verify_airgap_bundle(bundle)


def test_airgap_rejects_manifest_size_mismatch(tmp_path: Path):
    bundle = tmp_path / "bad-size.zip"
    data = b"fixture"
    manifest = {"schema_version": "1.0.0", "offline_only": True, "artifacts": [{"path": "x.txt", "sha256": __import__("hashlib").sha256(data).hexdigest(), "size_bytes": 999}]}
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("AIRGAP-MANIFEST.json", json.dumps(manifest))
        archive.writestr("x.txt", data)
    with pytest.raises(ValueError, match="size mismatch"):
        verify_airgap_bundle(bundle)
