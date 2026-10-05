"""Authenticated FDSE delivery package encryption."""
from __future__ import annotations

import hashlib
import json
import os
import struct
import tempfile
import zipfile
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"FDSEENC1\n"
SALT_BYTES = 16
NONCE_BYTES = 12
SCRYPT_N = 2**15
SCRYPT_R = 8
SCRYPT_P = 1
MAX_PASSWORD_BYTES = 1024
MAX_DELIVERY_ZIP_BYTES = 1024 * 1024 * 1024


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _derive(password: str, salt: bytes) -> bytes:
    if not isinstance(password, str) or len(password) < 16:
        raise ValueError("delivery password must be at least 16 characters")
    raw = password.encode("utf-8")
    if len(raw) > MAX_PASSWORD_BYTES:
        raise ValueError("delivery password is too long")
    return hashlib.scrypt(raw, salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P, maxmem=64 * 1024 * 1024, dklen=32)


def build_delivery_zip(artifacts: dict[str, Path], output_zip: Path) -> dict:
    if not artifacts:
        raise ValueError("at least one artifact is required")
    output_zip = Path(output_zip)
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    manifest = []
    seen_names: set[str] = set()
    for name, path in artifacts.items():
        path = Path(path)
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"artifact must be a regular file: {path}")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("delivery name must be a non-empty string")
        safe_name = Path(name)
        if safe_name.is_absolute() or ".." in safe_name.parts or str(safe_name) in ("", ".") or str(safe_name) in seen_names:
            raise ValueError(f"unsafe or duplicate delivery name: {name}")
        seen_names.add(str(safe_name))
        manifest.append({"name": str(safe_name), "sha256": _sha256(path), "size_bytes": path.stat().st_size})
    manifest.sort(key=lambda item: item["name"])
    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("delivery-manifest.json", json.dumps({"algorithm": "SHA-256", "artifacts": manifest}, indent=2, sort_keys=True))
        for name, path in sorted(artifacts.items(), key=lambda item: item[0]):
            archive.write(Path(path), arcname=name)
    return {"algorithm": "SHA-256", "artifacts": manifest, "zip_sha256": _sha256(output_zip)}


def encrypt_delivery(zip_path: Path, encrypted_path: Path, password: str) -> dict:
    zip_path = Path(zip_path)
    if zip_path.stat().st_size > MAX_DELIVERY_ZIP_BYTES:
        raise ValueError("delivery package exceeds maximum supported size")
    plaintext = zip_path.read_bytes()
    salt = os.urandom(SALT_BYTES)
    nonce = os.urandom(NONCE_BYTES)
    metadata = {
        "version": 1,
        "kdf": "scrypt",
        "scrypt": {"n": SCRYPT_N, "r": SCRYPT_R, "p": SCRYPT_P, "dklen": 32},
        "cipher": "AES-256-GCM",
        "salt": salt.hex(),
        "nonce": nonce.hex(),
    }
    header = json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode("utf-8")
    aad = MAGIC + struct.pack(">I", len(header)) + header
    key = _derive(password, salt)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, aad)
    encrypted_path = Path(encrypted_path)
    encrypted_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".fdse-delivery-", dir=encrypted_path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(aad)
            handle.write(ciphertext)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_name, 0o600)
        os.replace(temp_name, encrypted_path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise
    return {"cipher": "AES-256-GCM", "kdf": "scrypt", "sha256": _sha256(encrypted_path), "size_bytes": encrypted_path.stat().st_size}


def decrypt_delivery(encrypted_path: Path, output_zip: Path, password: str) -> Path:
    data = Path(encrypted_path).read_bytes()
    if not data.startswith(MAGIC):
        raise ValueError("invalid FDSE encrypted package")
    offset = len(MAGIC)
    if len(data) < offset + 4:
        raise ValueError("truncated FDSE encrypted package")
    header_len = struct.unpack(">I", data[offset:offset + 4])[0]
    offset += 4
    header = data[offset:offset + header_len]
    offset += header_len
    metadata = json.loads(header)
    if metadata.get("version") != 1 or metadata.get("cipher") != "AES-256-GCM" or metadata.get("kdf") != "scrypt":
        raise ValueError("unsupported encryption profile")
    salt = bytes.fromhex(metadata["salt"])
    nonce = bytes.fromhex(metadata["nonce"])
    key = _derive(password, salt)
    aad = MAGIC + struct.pack(">I", header_len) + header
    plaintext = AESGCM(key).decrypt(nonce, data[offset:], aad)
    output_zip = Path(output_zip)
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    output_zip.write_bytes(plaintext)
    return output_zip
