from pathlib import Path

import pytest

from fdse_toolkit.delivery import build_delivery_zip, decrypt_delivery, encrypt_delivery


def test_delivery_package_encrypts_and_round_trips(tmp_path: Path):
    source = tmp_path / "report.txt"
    source.write_text("synthetic report", encoding="utf-8")
    zip_path = tmp_path / "delivery.zip"
    encrypted = tmp_path / "delivery.fdse"
    restored = tmp_path / "restored.zip"
    manifest = build_delivery_zip({"report.txt": source}, zip_path)
    assert manifest["artifacts"][0]["name"] == "report.txt"
    result = encrypt_delivery(zip_path, encrypted, "correct horse battery staple 123")
    assert result["cipher"] == "AES-256-GCM"
    decrypt_delivery(encrypted, restored, "correct horse battery staple 123")
    assert restored.read_bytes() == zip_path.read_bytes()


def test_delivery_wrong_password_and_traversal_fail(tmp_path: Path):
    source = tmp_path / "report.txt"
    source.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        build_delivery_zip({"../report.txt": source}, tmp_path / "x.zip")
    zip_path = tmp_path / "delivery.zip"
    build_delivery_zip({"report.txt": source}, zip_path)
    encrypted = tmp_path / "delivery.fdse"
    encrypt_delivery(zip_path, encrypted, "correct horse battery staple 123")
    with pytest.raises(Exception):
        decrypt_delivery(encrypted, tmp_path / "bad.zip", "wrong password completely")
