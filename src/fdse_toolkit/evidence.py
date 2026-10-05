"""Evidence acquisition, integrity, and tamper-evident chain-of-custody support."""

from __future__ import annotations

import getpass
import hashlib
import json
import os
import shutil
import tempfile
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from .contracts import validate_document


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


@contextmanager
def _exclusive_lock(lock_path: Path, timeout: float = 10.0) -> Iterator[None]:
    deadline = time.monotonic() + timeout
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"timed out waiting for evidence lock: {lock_path}")
            time.sleep(0.05)
    try:
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


class EvidenceStore:
    """Content-addressed evidence store with a tamper-evident event chain."""

    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.objects = self.root / "objects"
        self.chain = self.root / "chain"
        self.manifest_path = self.root / "manifest.json"
        self.lock_path = self.root / ".lock"
        self.root.mkdir(parents=True, exist_ok=True)
        self.objects.mkdir(exist_ok=True)
        self.chain.mkdir(exist_ok=True)
        if not self.manifest_path.exists():
            _atomic_write(self.manifest_path, canonical_json({"schema_version": "1.0.0", "evidence": []}) + b"\n")

    def _load_manifest(self) -> dict:
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def _append_event(self, event_type: str, evidence_id: str, details: dict, actor: str) -> dict:
        events = sorted(self.chain.glob("*.json"))
        sequence = len(events) + 1
        previous_hash = "" if not events else json.loads(events[-1].read_text(encoding="utf-8"))["event_sha256"]
        event = {
            "sequence": sequence,
            "event_id": "EVT-" + uuid.uuid4().hex.upper(),
            "event_type": event_type,
            "evidence_id": evidence_id,
            "actor": actor,
            "timestamp": utc_now(),
            "details": details,
            "previous_event_sha256": previous_hash,
        }
        event["event_sha256"] = hashlib.sha256(canonical_json(event)).hexdigest()
        _atomic_write(self.chain / f"{sequence:08d}.json", canonical_json(event) + b"\n")
        return event

    def add_file(
        self,
        source: Path,
        *,
        kind: str = "other",
        source_name: str = "FDSE operator",
        source_version: str | None = None,
        asset_id: str | None = None,
        classification: str = "CONFIDENTIAL",
        actor: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        source = Path(source).resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        if kind not in {"pcap", "log", "json", "screenshot", "document", "repository_artifact", "scan_output", "binary", "other"}:
            raise ValueError("unsupported evidence kind")
        if classification not in {"PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"}:
            raise ValueError("invalid classification")
        digest, size = sha256_file(source)
        evidence_id = "EVD-" + uuid.uuid4().hex[:20].upper()
        record = {
            "schema_version": "1.0.0",
            "evidence_id": evidence_id,
            "kind": kind,
            "sha256": digest,
            "collected_at": utc_now(),
            "source": source_name,
            "source_version": source_version,
            "asset_id": asset_id,
            "path": source.name,
            "size_bytes": size,
            "classification": classification,
            "provenance": {
                "collector": "tinlance-fdse-toolkit",
                "collector_version": "0.1.0.dev0",
                "metadata": metadata or {},
            },
        }
        record = {k: v for k, v in record.items() if v is not None}
        validate_document("evidence", record)
        actor = actor or getpass.getuser()
        with _exclusive_lock(self.lock_path):
            object_path = self.objects / digest
            if not object_path.exists():
                fd, temp_name = tempfile.mkstemp(prefix=".object-", dir=self.objects)
                try:
                    with os.fdopen(fd, "wb") as destination, source.open("rb") as source_handle:
                        shutil.copyfileobj(source_handle, destination, length=1024 * 1024)
                        destination.flush()
                        os.fsync(destination.fileno())
                    os.chmod(temp_name, 0o600)
                    os.replace(temp_name, object_path)
                except BaseException:
                    try:
                        os.unlink(temp_name)
                    except FileNotFoundError:
                        pass
                    raise
            manifest = self._load_manifest()
            manifest["evidence"].append(record)
            _atomic_write(self.manifest_path, canonical_json(manifest) + b"\n")
            record_hash = hashlib.sha256(canonical_json(record)).hexdigest()
            self._append_event("COLLECTED", evidence_id, {"record_sha256": record_hash, "object_sha256": digest}, actor)
        return record

    def verify(self) -> dict:
        manifest = self._load_manifest()
        records = manifest.get("evidence", [])
        previous = ""
        verified_records = 0
        for record in records:
            validate_document("evidence", record)
            object_path = self.objects / record["sha256"]
            if not object_path.is_file():
                raise ValueError(f"missing evidence object: {record['evidence_id']}")
            digest, size = sha256_file(object_path)
            if digest != record["sha256"] or size != record["size_bytes"]:
                raise ValueError(f"evidence integrity failure: {record['evidence_id']}")
            verified_records += 1
        for expected_sequence, event_path in enumerate(sorted(self.chain.glob("*.json")), start=1):
            event = json.loads(event_path.read_text(encoding="utf-8"))
            if event["sequence"] != expected_sequence or event["previous_event_sha256"] != previous:
                raise ValueError(f"chain sequence failure: {event_path.name}")
            claimed = event.pop("event_sha256")
            calculated = hashlib.sha256(canonical_json(event)).hexdigest()
            if claimed != calculated:
                raise ValueError(f"chain integrity failure: {event_path.name}")
            previous = claimed
        return {"records": verified_records, "events": len(list(self.chain.glob("*.json"))), "head_sha256": previous}
