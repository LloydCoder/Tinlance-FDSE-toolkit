"""Adapters normalize external tool output into FDSE canonical findings."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AdapterContext:
    evidence_id: str
    source: str
    source_version: str | None = None


class AdapterError(ValueError):
    pass


def _severity(value: str | None) -> str:
    value = (value or "INFO").upper()
    return {"ERROR": "HIGH", "WARNING": "MEDIUM", "WARN": "MEDIUM", "NOTE": "INFO"}.get(value, value if value in {"INFO","LOW","MEDIUM","HIGH","CRITICAL"} else "INFO")


def _confidence(value: Any) -> float:
    if isinstance(value, (int, float)):
        return max(0.0, min(1.0, float(value)))
    return 0.5
