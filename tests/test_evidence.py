from pathlib import Path

import pytest

from fdse_toolkit.evidence import EvidenceStore, sha256_file


def test_evidence_store_is_content_addressed_and_verifiable(tmp_path: Path):
    source = tmp_path / "result.json"
    source.write_text('{"result":"synthetic"}\n', encoding="utf-8")
    store = EvidenceStore(tmp_path / "engagement" / "evidence")
    record = store.add_file(source, kind="json", source_name="synthetic-fixture")

    assert record["sha256"] == sha256_file(source)[0]
    assert (store.objects / record["sha256"]).is_file()
    result = store.verify()
    assert result["records"] == 1
    assert result["events"] == 1


def test_evidence_tampering_is_detected(tmp_path: Path):
    source = tmp_path / "result.json"
    source.write_text("original", encoding="utf-8")
    store = EvidenceStore(tmp_path / "evidence")
    record = store.add_file(source, kind="json")
    object_path = store.objects / record["sha256"]
    object_path.write_text("tampered", encoding="utf-8")

    with pytest.raises(ValueError, match="integrity failure"):
        store.verify()


def test_chain_tampering_is_detected(tmp_path: Path):
    source = tmp_path / "result.json"
    source.write_text("original", encoding="utf-8")
    store = EvidenceStore(tmp_path / "evidence")
    store.add_file(source, kind="json")
    event = store.chain / "00000001.json"
    event.write_text(event.read_text(encoding="utf-8").replace("COLLECTED", "ALTERED"), encoding="utf-8")

    with pytest.raises(ValueError, match="chain integrity failure"):
        store.verify()
