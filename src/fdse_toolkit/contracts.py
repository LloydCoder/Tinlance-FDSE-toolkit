"""Canonical FDSE contract validation.

Schemas are versioned JSON Schema Draft 2020-12 documents. Validation is
local-only: no schema is fetched from the network at runtime.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"

class ContractValidationError(ValueError):
    """Raised when a canonical FDSE document violates its schema."""


def load_schema(kind: str, schema_dir: Path | None = None) -> dict[str, Any]:
    if not kind or any(ch in kind for ch in "/\\"):
        raise ValueError("invalid schema kind")
    path = (schema_dir or SCHEMA_DIR) / f"{kind}.schema.json"
    if not path.is_file():
        raise FileNotFoundError(f"schema not found: {kind}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_document(kind: str, instance: Any, *, schema_dir: Path | None = None) -> None:
    """Validate one FDSE document and raise with deterministic error details."""
    schema = load_schema(kind, schema_dir)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    if errors:
        details = "; ".join(
            f"{'/'.join(str(p) for p in error.absolute_path) or '<root>'}: {error.message}"
            for error in errors
        )
        raise ContractValidationError(f"{kind}: {details}")


def validate_document_file(kind: str, document_path: Path, *, schema_dir: Path | None = None) -> None:
    """Load UTF-8 JSON and validate it against a canonical contract."""
    data = json.loads(document_path.read_text(encoding="utf-8"))
    validate_document(kind, data, schema_dir=schema_dir)
