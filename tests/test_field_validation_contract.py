import json
from pathlib import Path

from fdse_toolkit.contracts import validate_document


def test_synthetic_field_validation_record_matches_contract():
    root = Path(__file__).parents[1]
    record = json.loads((root / "examples/field-validation-record.synthetic.json").read_text(encoding="utf-8"))
    validate_document("field-validation", record)


def test_field_validation_rejects_unknown_acceptance_result():
    root = Path(__file__).parents[1]
    record = json.loads((root / "examples/field-validation-record.synthetic.json").read_text(encoding="utf-8"))
    record["acceptance"]["criteria"][0]["result"] = "GREEN"
    try:
        validate_document("field-validation", record)
    except ValueError:
        return
    raise AssertionError("invalid acceptance result was accepted")
