from fdse_toolkit.contracts import ContractValidationError, validate_document


def test_engagement_contract_accepts_minimum_document():
    validate_document(
        "engagement",
        {
            "schema_version": "1.0.0",
            "engagement_id": "FDSE-ACME-001",
            "client": {"name": "Acme"},
            "scope": {"authorized_targets": ["example.com"]},
            "created_at": "2026-10-05T08:00:00Z",
        },
    )


def test_finding_contract_rejects_plaintext_missing_evidence_reference():
    try:
        validate_document(
            "finding",
            {
                "schema_version": "1.0.0",
                "finding_id": "FND-001",
                "title": "Test finding",
                "severity": "HIGH",
                "status": "OPEN",
                "confidence": 0.9,
                "evidence_ids": [],
            },
        )
    except ContractValidationError as exc:
        assert "evidence_ids" in str(exc)
    else:
        raise AssertionError("invalid finding was accepted")


def test_delivery_manifest_rejects_invalid_sha256():
    try:
        validate_document(
            "delivery-manifest",
            {
                "schema_version": "1.0.0",
                "delivery_id": "DLV-001",
                "created_at": "2026-10-05T08:00:00Z",
                "artifacts": [{"artifact_id": "ART-001", "name": "report.pdf", "sha256": "bad", "size_bytes": 1}],
            },
        )
    except ContractValidationError as exc:
        assert "sha256" in str(exc)
    else:
        raise AssertionError("invalid manifest was accepted")
