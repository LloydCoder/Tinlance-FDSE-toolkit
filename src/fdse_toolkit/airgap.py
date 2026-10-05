"""Offline/air-gapped FDSE bundle builder and verifier."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

MAX_BUNDLE_FILES = 10000
MAX_BUNDLE_UNCOMPRESSED_BYTES = 2 * 1024 * 1024 * 1024


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
        if len(names) > MAX_BUNDLE_FILES + 1:
            raise ValueError("air-gap bundle contains too many archive entries")
        if len(names) != len(set(names)):
            raise ValueError("air-gap bundle contains duplicate archive names")
        if "AIRGAP-MANIFEST.json" not in names:
            raise ValueError("missing AIRGAP-MANIFEST.json")
        manifest = json.loads(archive.read("AIRGAP-MANIFEST.json"))
        artifacts = manifest.get("artifacts", [])
        if not isinstance(artifacts, list) or len(artifacts) > MAX_BUNDLE_FILES:
            raise ValueError("invalid air-gap artifact count")
        total_size = 0
        seen: set[str] = set()
        for item in artifacts:
            name = item["path"]
            if name in seen:
                raise ValueError(f"duplicate manifest artifact: {name}")
            seen.add(name)
            if name not in names:
                raise ValueError(f"missing bundle artifact: {name}")
            if Path(name).is_absolute() or ".." in Path(name).parts:
                raise ValueError(f"unsafe bundle path: {name}")
            info = archive.getinfo(name)
            declared_size = item.get("size_bytes")
            if not isinstance(declared_size, int) or declared_size < 0 or declared_size != info.file_size:
                raise ValueError(f"size mismatch: {name}")
            total_size += info.file_size
            if total_size > MAX_BUNDLE_UNCOMPRESSED_BYTES:
                raise ValueError("air-gap bundle exceeds uncompressed size limit")
            data = archive.read(name)
            if hashlib.sha256(data).hexdigest() != item["sha256"]:

                raise ValueError(f"integrity failure: {name}")
    return manifest
