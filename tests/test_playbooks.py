from pathlib import Path

from docx import Document

from fdse_toolkit.playbooks import generate_playbook


def test_playbook_is_client_specific_and_does_not_hardcode_legal_deadline(tmp_path: Path):
    engagement = {"schema_version":"1.0.0","engagement_id":"FDSE-ACME-001","client":{"name":"Acme"},"scope":{"authorized_targets":["example.com"]},"created_at":"2026-10-05T08:00:00Z"}
    incident = {"schema_version":"1.0.0","incident_id":"INC-AAA","category":"RANSOMWARE","severity":"CRITICAL","status":"OPEN"}
    path = generate_playbook(engagement, incident, tmp_path / "playbook.docx")
    text = "\n".join(p.text for p in Document(path).paragraphs)
    assert "Acme" in text
    assert "authoritative source" in text
    assert "24 hours" not in text
