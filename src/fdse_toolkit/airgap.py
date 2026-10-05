"""Offline/air-gapped FDSE bundle builder and verifier."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def build_airgap_bundle(source_dir: Path, output_zip: Path) -> dict:
    source_dir = Path(source_dir).resolve()
    if not source_dir.is_dir():
        raise NotADirectoryError(source_dir)
    files = []
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(source_dir)
        if ".." in relative.parts:
            raise ValueError("path traversal detected")
        files.append({"path": relative.as_posix(), "sha256": _sha256(path), "size_bytes": path.stat().st_size})
    if not files:
        raise ValueError("air-gap bundle cannot be empty")
    manifest = {"schema_version": "1.0.0", "offline_only": True, "artifacts": files}
    output_zip = Path(output_zip)
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("AIRGAP-MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True))
        for item in files:
            archive.write(source_dir / item["path"], arcname=item["path"])
    return manifest


def verify_airgap_bundle(bundle_zip: Path) -> dict:
    bundle_zip = Path(bundle_zip)
    with zipfile.ZipFile(bundle_zip) as archive:
        names = archive.namelist()
        if "AIRGAP-MANIFEST.json" not in names:
            raise ValueError("missing AIRGAP-MANIFEST.json")
        manifest = json.loads(archive.read("AIRGAP-MANIFEST.json"))
        for item in manifest.get("artifacts", []):
            name = item["path"]
            if name not in names:
                raise ValueError(f"missing bundle artifact: {name}")
            if Path(name).is_absolute() or ".." in Path(name).parts:
                raise ValueError(f"unsafe bundle path: {name}")
            data = archive.read(name)
            if hashlib.sha256(data).hexdigest() != item["sha256"]:
                raise ValueError(f"integrity failure: {name}")
    return manifest
